from unittest.mock import patch
from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError
from payments.tests import test_inventory as fixtures
from shipping.tests.test_quotes import ORIGIN
from shipping.envia import Rate
from payments.services import start_checkout, apply_session_snapshot, reconcile_attempt
from payments.models import PaymentAttempt
from payments import stripe_gateway


def snapshot(attempt, status='open', paid=False):
    return dict(id='cs_test_' + str(attempt.pk), status=status, payment_status='paid' if paid else 'unpaid',
        amount_total=attempt.total_minor, currency='mxn', livemode=False,
        client_reference_id=str(attempt.public_id), url='https://checkout.stripe.com/c/test',
        expires_at=int(attempt.expires_at.timestamp()))


@override_settings(SHIPPING_ORIGIN=ORIGIN, STRIPE_SECRET_KEY='sk_test_localfixture', PAYMENT_ORIGIN='http://localhost:8000')
class CheckoutTests(TestCase):
    add = fixtures.InventoryTests.add
    setUp = fixtures.InventoryTests.setUp

    @patch('payments.stripe_gateway.create_session', side_effect=lambda a: snapshot(a))
    @patch('shipping.services.quote_rates', return_value=[Rate('dhl','ground',10000,'MXN')])
    def test_checkout_idempotency_and_confirmation(self, rates, create):
        result = start_checkout(self.customer, self.order.pk, self.quote.pk)
        self.assertEqual(result.attempt.total_minor, 15000)
        again = start_checkout(self.customer,self.order.pk,self.quote.pk)
        self.assertEqual(again.attempt.pk, result.attempt.pk)
        self.assertEqual(self.order.payment_attempts.count(),1)
        paid = snapshot(result.attempt, 'complete', True)
        apply_session_snapshot(result.attempt.pk,paid,event_id='evt_1')
        apply_session_snapshot(result.attempt.pk,paid,event_id='evt_1')
        p=self.order.items.first().product
        p.refresh_from_db(); self.assertEqual(p.stock,25); self.assertEqual(p.reserved_stock,0)
        self.assertEqual(self.order.payment_attempts.get().state,'paid')

    @patch('payments.stripe_gateway.create_session', side_effect=stripe_gateway.PaymentUnavailable())
    @patch('shipping.services.quote_rates', return_value=[Rate('dhl','ground',10000,'MXN')])
    def test_unknown_creation_keeps_reservation(self, rates, create):
        with self.assertRaises(ValidationError): start_checkout(self.customer,self.order.pk,self.quote.pk)
        attempt=self.order.payment_attempts.get()
        payload=attempt.payload
        self.assertTrue(payload)
        with patch('payments.stripe_gateway.create_session',side_effect=lambda a: snapshot(a)):
            recovered=start_checkout(self.customer,self.order.pk,self.quote.pk)
        self.assertEqual(recovered.attempt.pk,attempt.pk)
        attempt.refresh_from_db(); self.assertEqual(attempt.payload,payload)

    @patch('shipping.services.quote_rates', return_value=[Rate('dhl','ground',10001,'MXN')])
    def test_changed_quote_needs_consent(self, rates):
        result=start_checkout(self.customer,self.order.pk,self.quote.pk)
        self.assertIsNone(result.attempt)
        self.assertEqual(result.quote.amount_minor,10001)
        self.assertFalse(self.order.payment_attempts.exists())

    def test_missing_approval_and_live_key_rejected(self):
        self.order.review_status='pending'; self.order.save()
        with self.assertRaises(ValidationError): start_checkout(self.customer,self.order.pk,self.quote.pk)
        with override_settings(STRIPE_SECRET_KEY='sk_live_notallowed'):
            with self.assertRaises(ValidationError): stripe_gateway.ensure_configured()

    def test_mismatched_amount_never_paid(self):
        from payments.inventory import reserve_order
        attempt=reserve_order(self.order.pk,self.quote.pk)
        data=snapshot(attempt,'complete',True); data['amount_total']=1
        apply_session_snapshot(attempt.pk,data)
        attempt.refresh_from_db(); self.assertEqual(attempt.state,'reconciliation_required')
        self.assertEqual(attempt.reservations.get().state,'held')

    def test_expired_releases_once(self):
        from payments.inventory import reserve_order
        attempt=reserve_order(self.order.pk,self.quote.pk)
        data=snapshot(attempt,'expired')
        apply_session_snapshot(attempt.pk,data); apply_session_snapshot(attempt.pk,data)
        p=self.order.items.first().product; p.refresh_from_db()
        self.assertEqual(p.stock,30); self.assertEqual(p.reserved_stock,0)

    @patch('shipping.services.quote_rates', return_value=[Rate('dhl','ground',10000,'MXN')])
    def test_definitive_creation_rejection_releases_reservation(self,rates):
        import stripe
        with patch('payments.stripe_gateway._client') as client:
            client.return_value.v1.checkout.sessions.create.side_effect=stripe.InvalidRequestError(
                'Expiration is invalid',param='expires_at',http_status=400)
            with self.assertRaises(ValidationError): start_checkout(self.customer,self.order.pk,self.quote.pk)
        attempt=self.order.payment_attempts.get()
        self.assertEqual(attempt.state,'failed')
        self.assertEqual(attempt.reservations.get().state,'released')

    @patch('shipping.services.quote_rates', return_value=[Rate('dhl','ground',10000,'MXN')])
    def test_rejection_after_unknown_creation_does_not_release(self, rates):
        with patch('payments.stripe_gateway.create_session', side_effect=stripe_gateway.PaymentUnavailable()):
            with self.assertRaises(ValidationError): start_checkout(self.customer,self.order.pk,self.quote.pk)
        with patch('payments.stripe_gateway.create_session', side_effect=stripe_gateway.PaymentRejected()):
            with self.assertRaises(ValidationError): start_checkout(self.customer,self.order.pk,self.quote.pk)
        attempt=self.order.payment_attempts.get()
        self.assertEqual(attempt.reservations.get().state,'held')
        self.assertNotEqual(attempt.state,'failed')

    def test_paid_never_downgraded_by_late_event(self):
        from payments.inventory import reserve_order
        attempt=reserve_order(self.order.pk,self.quote.pk)
        apply_session_snapshot(attempt.pk,snapshot(attempt,'complete',True),'evt_paid')
        apply_session_snapshot(attempt.pk,snapshot(attempt,'expired'),'evt_expired')
        attempt.refresh_from_db()
        self.assertEqual(attempt.state,'paid')
        self.assertEqual(attempt.reservations.get().state,'consumed')

    def test_live_snapshot_never_consumes_stock(self):
        from payments.inventory import reserve_order
        attempt=reserve_order(self.order.pk,self.quote.pk)
        data=snapshot(attempt,'complete',True); data['livemode']=True
        apply_session_snapshot(attempt.pk,data)
        attempt.refresh_from_db()
        self.assertEqual(attempt.state,'reconciliation_required')
        self.assertEqual(attempt.reservations.get().state,'held')

    def test_cannot_revoke_approval_with_active_reservation(self):
        from django.contrib.auth import get_user_model
        from orders.services import review_order
        from payments.inventory import reserve_order
        staff=get_user_model().objects.create_user('reviewer',is_staff=True,is_superuser=True)
        reserve_order(self.order.pk,self.quote.pk)
        self.order.refresh_from_db()
        with self.assertRaises(ValidationError):
            review_order(staff,self.order.pk,self.order.version,'pending','')
        self.order.refresh_from_db(); self.assertEqual(self.order.review_status,'approved')

    def test_provider_timeout_during_expiry_keeps_stock(self):
        from payments.inventory import reserve_order
        attempt=reserve_order(self.order.pk,self.quote.pk)
        apply_session_snapshot(attempt.pk,snapshot(attempt))
        with patch('payments.stripe_gateway.retrieve_session',side_effect=stripe_gateway.PaymentUnavailable()):
            with self.assertRaises(ValidationError): reconcile_attempt(attempt.pk,expire=True)
        self.assertEqual(attempt.reservations.get().state,'held')
