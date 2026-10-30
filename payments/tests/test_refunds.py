"""Cancellation policy and provider boundaries; only Stripe I/O is mocked."""
import importlib
from datetime import timedelta
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings, Client
from django.utils import timezone

from payments.tests import test_inventory as inventory_fixtures
from payments.tests.test_checkout import snapshot
from payments.inventory import reserve_order
from payments.services import apply_session_snapshot
from payments.models import PaymentAttempt
from shipping.tests.test_quotes import ORIGIN


def paid_session(attempt, paid_at):
    data = snapshot(attempt, 'complete', True)
    charge = dict(id='ch_fixture', created=int(paid_at.timestamp()), paid=True,
                  captured=True, status='succeeded', livemode=False, currency='mxn',
                  amount=attempt.total_minor, amount_captured=attempt.total_minor,
                  payment_intent='pi_fixture', amount_refunded=0)
    data['payment_intent'] = dict(id='pi_fixture', status='succeeded', latest_charge=charge)
    return data


@override_settings(SHIPPING_ORIGIN=ORIGIN, STRIPE_SECRET_KEY='sk_test_fixture',
                   PAYMENT_ORIGIN='http://localhost:8000', STRIPE_WEBHOOK_SECRET='whsec_fixture')
class RefundTests(TestCase):
    add = inventory_fixtures.InventoryTests.add

    def setUp(self):
        inventory_fixtures.InventoryTests.setUp(self)
        self.assertIsNotNone(importlib.util.find_spec('payments.refunds'), 'Falta el servicio de cancelación')
        self.service = importlib.import_module('payments.refunds')
        self.attempt = reserve_order(self.order.pk, self.quote.pk)
        PaymentAttempt.objects.filter(pk=self.attempt.pk).update(created_at=timezone.now()-timedelta(days=3))
        self.paid_at = timezone.now().replace(microsecond=0) - timedelta(hours=1)
        self.session = paid_session(self.attempt, self.paid_at)
        apply_session_snapshot(self.attempt.pk, self.session)
        self.attempt.refresh_from_db()

    def response(self, refund, status='succeeded'):
        return dict(id='re_fixture', object='refund', status=status, currency='mxn',
                    amount=self.attempt.total_minor, payment_intent='pi_fixture', charge='ch_fixture',
                    metadata={'cancellation': str(refund.public_id)})

    def request(self):
        with patch('payments.stripe_gateway.create_refund', side_effect=self.response):
            return self.service.request_cancellation(self.customer, self.order.pk)

    def test_full_refund_preserves_payment_and_does_not_restock(self):
        result = self.request()
        self.assertEqual(result.state, 'succeeded')
        self.assertEqual(result.amount_minor, 15000)  # 50 products + 100 shipping
        self.attempt.refresh_from_db()
        self.assertEqual(self.attempt.state, 'paid')
        product = self.order.items.first().product
        product.refresh_from_db()
        self.assertEqual((product.stock, product.reserved_stock), (25, 0))
        with patch('payments.stripe_gateway.retrieve_refund',return_value=self.response(result)):
            self.assertEqual(self.request().pk, result.pk)
        self.assertEqual(self.attempt.refund.amount_minor, 15000)

    def test_clock_comes_from_successful_charge(self):
        self.assertEqual(self.attempt.paid_at, self.paid_at)
        self.assertEqual(self.attempt.charge_id, 'ch_fixture')
        self.assertEqual(self.attempt.payment_intent_id, 'pi_fixture')

    def test_boundary_is_under_2000_and_under_24_hours(self):
        for amount, elapsed, eligible in [(199999, 86399, True), (200000, 1, False),
                                          (199999, 86400, False), (199999, -10, False)]:
            with self.subTest(amount=amount, elapsed=elapsed):
                self.attempt.total_minor = amount
                self.attempt.paid_at = timezone.now() - timedelta(seconds=elapsed)
                self.assertEqual(self.service.eligible(self.attempt), eligible)

    def test_server_enforces_limit_and_deadline(self):
        for changes in [{'total_minor': 200000}, {'paid_at': timezone.now()-timedelta(hours=24)}]:
            with self.subTest(changes=changes):
                PaymentAttempt.objects.filter(pk=self.attempt.pk).update(**changes)
                with self.assertRaises(ValidationError): self.request()
                self.assertFalse(self.service.Refund.objects.exists())
                PaymentAttempt.objects.filter(pk=self.attempt.pk).update(total_minor=15000, paid_at=self.paid_at)

    def test_historical_payment_fetches_canonical_clock(self):
        PaymentAttempt.objects.filter(pk=self.attempt.pk).update(paid_at=None, charge_id='', payment_intent_id='')
        with patch('payments.stripe_gateway.retrieve_session', return_value=self.session):
            self.assertEqual(self.request().state, 'succeeded')

    def test_historical_old_payment_cannot_restart_clock(self):
        PaymentAttempt.objects.filter(pk=self.attempt.pk).update(paid_at=None, charge_id='', payment_intent_id='')
        old = paid_session(self.attempt, timezone.now()-timedelta(days=2))
        with patch('payments.stripe_gateway.retrieve_session', return_value=old):
            with self.assertRaises(ValidationError): self.request()

    def test_timeout_recovers_same_request_without_second_refund(self):
        from payments.stripe_gateway import PaymentUnavailable
        with patch('payments.stripe_gateway.create_refund', side_effect=PaymentUnavailable()):
            with self.assertRaises(ValidationError): self.service.request_cancellation(self.customer, self.order.pk)
        pending = self.service.Refund.objects.get()
        self.assertEqual(pending.state, 'requested')
        with patch('payments.stripe_gateway.find_refund', return_value=self.response(pending)):
            result = self.service.reconcile_refund(pending.pk)
        self.assertEqual(result.public_id, pending.public_id)
        self.assertEqual(result.state, 'succeeded')

    def test_pending_does_not_claim_completed_and_events_are_idempotent(self):
        with patch('payments.stripe_gateway.create_refund', side_effect=lambda r:self.response(r,'pending')):
            refund=self.service.request_cancellation(self.customer,self.order.pk)
        self.assertEqual(refund.state,'pending')
        self.service.apply_refund_snapshot(refund.pk,self.response(refund),'evt_refund')
        self.service.apply_refund_snapshot(refund.pk,self.response(refund),'evt_refund')
        self.service.apply_refund_snapshot(refund.pk,self.response(refund,'pending'),'evt_late')
        refund.refresh_from_db(); self.assertEqual(refund.state,'succeeded')
        from payments.models import ProviderEvent
        self.assertEqual(ProviderEvent.objects.filter(event_id='evt_refund').count(),1)

    def test_wrong_refund_identity_amount_and_live_mode_rejected(self):
        with patch('payments.stripe_gateway.create_refund', side_effect=lambda r:self.response(r,'pending')):
            refund=self.service.request_cancellation(self.customer,self.order.pk)
        for changes in [{'amount':1},{'payment_intent':'pi_other'},{'charge':'ch_other'},
                        {'livemode':True},{'currency':'usd'},{'metadata':{}},{'id':'re_other'}]:
            with self.subTest(changes=changes):
                with self.assertRaises(ValidationError):
                    self.service.apply_refund_snapshot(refund.pk,{**self.response(refund),**changes})
                refund.refresh_from_db(); self.assertEqual(refund.state,'pending')

    def test_non_owner_and_unpaid_cannot_cancel(self):
        from accounts.models import CustomerProfile
        from django.contrib.auth import get_user_model
        stranger=CustomerProfile.objects.create(user=get_user_model().objects.create_user('other'),email='other@example.com',full_name='Other')
        with self.assertRaises(ValidationError): self.service.request_cancellation(stranger,self.order.pk)
        PaymentAttempt.objects.filter(pk=self.attempt.pk).update(state='open')
        with self.assertRaises(ValidationError): self.request()

    def test_failed_refund_needs_review_not_new_charge_or_refund(self):
        with patch('payments.stripe_gateway.create_refund', side_effect=lambda r:self.response(r,'failed')):
            refund=self.service.request_cancellation(self.customer,self.order.pk)
        self.assertEqual(refund.state,'failed')
        with patch('payments.stripe_gateway.retrieve_refund',return_value=self.response(refund,'failed')):
            result=self.service.request_cancellation(self.customer,self.order.pk)
        self.assertEqual(result.pk,refund.pk)
        self.assertEqual(self.service.Refund.objects.count(),1)

    def test_page_requires_confirmation_owner_and_csrf(self):
        url=f'/pedido/{self.order.public_id}/cancelar/'
        self.assertEqual(self.client.get(url).status_code,302)
        self.client.force_login(self.customer.user,backend='accounts.backends.CustomerEmailBackend')
        self.assertContains(self.client.get(url),'Confirmar cancelación')
        self.assertFalse(self.service.Refund.objects.exists())
        self.client.post(url,{})
        self.assertFalse(self.service.Refund.objects.exists())
        csrf=Client(enforce_csrf_checks=True); csrf.force_login(self.customer.user)
        self.assertEqual(csrf.post(url,{'confirm':'on'}).status_code,403)
        with patch('payments.stripe_gateway.create_refund',side_effect=self.response):
            self.assertEqual(self.client.post(url,{'confirm':'on'}).status_code,302)
        self.assertContains(self.client.get(f'/pedido/{self.order.public_id}/'),'Reembolso confirmado')

    def test_signed_refund_webhook_reads_canonical_state(self):
        import hashlib, hmac, json, time
        with patch('payments.stripe_gateway.create_refund',side_effect=lambda r:self.response(r,'pending')):
            refund=self.service.request_cancellation(self.customer,self.order.pk)
        event=dict(id='evt_refund_webhook',type='refund.updated',livemode=False,
                   data={'object':self.response(refund,'pending')})
        body=json.dumps(event); timestamp=str(int(time.time()))
        sig=hmac.new(b'whsec_fixture',f'{timestamp}.{body}'.encode(),hashlib.sha256).hexdigest()
        with patch('payments.stripe_gateway.retrieve_refund',return_value=self.response(refund)):
            for _ in range(2):
                result=self.client.post('/pagos/stripe/webhook/',body,content_type='application/json',
                                        HTTP_STRIPE_SIGNATURE=f't={timestamp},v1={sig}')
                self.assertEqual(result.status_code,200)
        refund.refresh_from_db(); self.assertEqual(refund.state,'succeeded')

    def test_unknown_request_older_than_idempotency_window_never_reissued(self):
        from payments.stripe_gateway import PaymentUnavailable
        with patch('payments.stripe_gateway.create_refund',side_effect=PaymentUnavailable()):
            with self.assertRaises(ValidationError): self.service.request_cancellation(self.customer,self.order.pk)
        refund=self.service.Refund.objects.get()
        self.service.Refund.objects.filter(pk=refund.pk).update(requested_at=timezone.now()-timedelta(days=2))
        with patch('payments.stripe_gateway.find_refund',return_value=None), patch('payments.stripe_gateway.create_refund',side_effect=AssertionError('No debe crear otro reembolso')):
            with self.assertRaises(ValidationError): self.service.reconcile_refund(refund.pk)

    def test_cancelled_order_cannot_start_another_payment(self):
        self.request()
        from payments.services import start_checkout
        result=start_checkout(self.customer,self.order.pk,self.quote.pk)
        self.assertEqual(result.attempt.pk,self.attempt.pk)
        self.assertEqual(self.order.payment_attempts.count(),1)

    def test_bank_can_reject_a_previously_confirmed_refund(self):
        refund=self.request()
        self.service.apply_refund_snapshot(refund.pk,self.response(refund,'failed'),'evt_bank_failed')
        refund.refresh_from_db(); self.assertEqual(refund.state,'failed')

    def test_admin_rechecks_confirmed_refunds_with_provider(self):
        refund=self.request()
        with patch('payments.stripe_gateway.retrieve_refund',return_value=self.response(refund,'failed')):
            result=self.service.reconcile_refund(refund.pk)
        self.assertEqual(result.state,'failed')
