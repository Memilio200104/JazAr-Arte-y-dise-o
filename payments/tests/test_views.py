import hashlib
import hmac
import json
import time
from unittest.mock import patch
from django.test import TestCase, Client, override_settings
from payments.tests import test_checkout as fixtures
from payments.inventory import reserve_order
from shipping.tests.test_quotes import ORIGIN


@override_settings(SHIPPING_ORIGIN=ORIGIN, STRIPE_SECRET_KEY='sk_test_fixture',
    STRIPE_WEBHOOK_SECRET='whsec_fixture', PAYMENT_ORIGIN='http://localhost:8000')
class PaymentViewTests(TestCase):
    add = fixtures.CheckoutTests.add
    setUp = fixtures.CheckoutTests.setUp

    def test_checkout_private_and_no_false_success(self):
        url=f'/pedido/{self.order.public_id}/pago/'
        self.assertEqual(self.client.get(url).status_code,302)
        self.client.force_login(self.customer.user,backend='accounts.backends.CustomerEmailBackend')
        response=self.client.get(url+'?success=1')
        self.assertContains(response,'Calcular envio')
        self.assertIn('no-store',response['Cache-Control'])
        self.assertFalse(self.order.payment_attempts.exists())
        self.assertEqual(self.client.post(url,{'action':'pay','quote_id':'invalid'}).status_code,200)
        client=Client(enforce_csrf_checks=True); client.force_login(self.customer.user)
        self.assertEqual(client.post(url,{'action':'quote'}).status_code,403)

    def test_signed_webhook_and_duplicate(self):
        attempt=reserve_order(self.order.pk,self.quote.pk)
        data=fixtures.snapshot(attempt,'complete',True)
        event=dict(id='evt_confirmed',type='checkout.session.completed',livemode=False,data={'object':data})
        body=json.dumps(event)
        timestamp=str(int(time.time()))
        signature=hmac.new(b'whsec_fixture',f'{timestamp}.{body}'.encode(),hashlib.sha256).hexdigest()
        headers={'HTTP_STRIPE_SIGNATURE':f't={timestamp},v1={signature}'}
        with patch('payments.stripe_gateway.retrieve_session',return_value=data):
            for _ in range(2):
                response=self.client.post('/pagos/stripe/webhook/',body,content_type='application/json',**headers)
                self.assertEqual(response.status_code,200)
        attempt.refresh_from_db(); self.assertEqual(attempt.state,'paid')
        self.assertEqual(self.client.post('/pagos/stripe/webhook/',body,content_type='application/json').status_code,400)

    def test_other_customer_cannot_view_or_change_order(self):
        from accounts.models import CustomerProfile
        from django.contrib.auth import get_user_model
        stranger=get_user_model().objects.create_user('stranger')
        CustomerProfile.objects.create(user=stranger,full_name='Otro',email='other@example.com')
        self.client.force_login(stranger,backend='accounts.backends.CustomerEmailBackend')
        url=f'/pedido/{self.order.public_id}/pago/'
        self.assertEqual(self.client.get(url).status_code,404)
        for action in ('quote','select','pay','resume','refresh'):
            self.assertEqual(self.client.post(url,{'action':action,'quote_id':self.quote.pk}).status_code,404)
        self.assertFalse(self.order.payment_attempts.exists())
