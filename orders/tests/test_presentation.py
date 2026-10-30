from datetime import timedelta
from django.test import TestCase, override_settings
from django.utils import timezone
from payments.tests import test_inventory as fixtures
from payments.models import PaymentAttempt
from orders.presentation import order_progress
from shipping.tests.test_quotes import ORIGIN


@override_settings(SHIPPING_ORIGIN=ORIGIN)
class PresentationTests(TestCase):
    add=fixtures.InventoryTests.add
    setUp=fixtures.InventoryTests.setUp

    def attempt(self, state):
        return PaymentAttempt.objects.create(order=self.order,quote=self.quote,
            approved_version=0,total_minor=15000,state=state,
            expires_at=timezone.now()+timedelta(minutes=30))

    def test_review_states_and_approved_not_paid(self):
        for status, expected in [('pending','En revisión'),('changes','Cambios solicitados'),('approved','Diseño aprobado')]:
            self.order.review_status=status
            progress=order_progress(self.order)
            self.assertEqual(progress['label'],expected)
            self.assertFalse(progress['paid'])
        self.assertEqual(progress['action_label'],'Elegir envío y pagar')

    def test_payment_states_and_paid_total(self):
        for state,label in [('creating','Preparando pago'),('open','Pago pendiente'),
                ('expired','Sesión vencida'),('failed','Pago no completado'),
                ('reconciliation_required','Verificando pago'),('paid','Pago confirmado')]:
            attempt=self.attempt(state)
            progress=order_progress(self.order)
            self.assertEqual(progress['label'],label)
            self.assertEqual(progress['paid'],state=='paid')
            if state=='paid':
                self.assertEqual(progress['total'],150)
                self.assertEqual(progress['action_label'],'Ver pago')
            attempt.delete()

    def test_paid_list_and_detail_show_correct_next_step(self):
        self.attempt('paid')
        self.client.force_login(self.customer.user,backend='accounts.backends.CustomerEmailBackend')
        for url in ['/cuenta/pedidos/',f'/pedido/{self.order.public_id}/']:
            response=self.client.get(url)
            self.assertContains(response,'Pago confirmado')
            self.assertContains(response,'150.00')
            self.assertNotContains(response,'Pendiente de calcular')
            self.assertNotContains(response,'Enviar diseño por WhatsApp')
            self.assertContains(response,'Ver pago')
            self.assertIn('no-store',response['Cache-Control'])
