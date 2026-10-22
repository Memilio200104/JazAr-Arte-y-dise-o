import json
from uuid import uuid4
from unittest.mock import patch
from django.test import TestCase, Client
from django.db import OperationalError
from orders.models import Order
from orders.services import create_order, OrderRateLimited
from orders.quotes import sign_quote
from .test_requests import RequestTests


class ViewTests(TestCase):
    setUp=RequestTests.setUp
    quote=RequestTests.quote

    def login(self):
        self.client.force_login(self.customer.user,backend='accounts.backends.CustomerEmailBackend')

    def test_private_flow(self):
        self.assertEqual(self.client.get('/pedido/solicitud/').status_code,302)
        self.login()
        response=self.client.post('/pedido/solicitud/',{'action':'preview','rows':json.dumps(self.rows),'address':self.address.pk,'notes':'Idea'})
        self.assertContains(response,'399.80')
        self.assertEqual(Order.objects.count(),0)
        token=response.context['quote_token']; key=response.context['idempotency_key']
        response=self.client.post('/pedido/solicitud/',{'action':'confirm','quote_token':token,'idempotency_key':key,'approved':'on'})
        self.assertEqual(response.status_code,302)
        order=Order.objects.get(); self.assertEqual(order.review_status,'pending')
        detail=self.client.get(response.url); self.assertContains(detail,'En revisión')
        self.assertIn('no-store',detail.headers['Cache-Control'])
        self.assertIsNotNone(detail.context['submitted_cart'])
        self.assertIsNone(self.client.get(response.url).context['submitted_cart'])
        self.assertContains(self.client.get(f'/pedido/{order.public_id}/pago/'),'disabled')

    def test_permissions_and_errors(self):
        order,_=create_order(self.customer,sign_quote(self.quote()),uuid4())
        from django.contrib.auth import get_user_model
        from accounts.models import CustomerProfile
        other=CustomerProfile.objects.create(user=get_user_model().objects.create_user('other'),email='other@example.com',full_name='Otro')
        self.client.force_login(other.user,backend='accounts.backends.CustomerEmailBackend')
        self.assertEqual(self.client.get(f'/pedido/{order.public_id}/').status_code,404)
        self.assertEqual(self.client.get(f'/pedido/{order.public_id}/pago/').status_code,404)
        self.login()
        csrf=Client(enforce_csrf_checks=True); csrf.force_login(self.customer.user)
        self.assertEqual(csrf.post('/pedido/solicitud/',{}).status_code,403)
        with patch('orders.views.create_order',side_effect=OperationalError):
            self.assertEqual(self.client.post('/pedido/solicitud/',{'action':'confirm'}).status_code,503)
        with patch('orders.views.create_order',side_effect=OrderRateLimited(42)):
            r=self.client.post('/pedido/solicitud/',{'action':'confirm'})
            self.assertEqual(r.status_code,429); self.assertEqual(r['Retry-After'],'42')
        self.assertEqual(self.client.post('/pedido/solicitud/',{'action':'preview','rows':'bad','address':self.address.pk}).status_code,200)
