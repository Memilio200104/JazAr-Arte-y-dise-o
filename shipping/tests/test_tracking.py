import importlib
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from payments.tests import test_refunds as fixtures


class TrackingTests(fixtures.RefundTests):
    # Reuse setup, not the parent test cases (see load_tests below).
    def setUp(self):
        super().setUp()
        self.assertIsNotNone(importlib.util.find_spec('shipping.tracking'), 'Falta registro de guías')
        self.tracking=importlib.import_module('shipping.tracking')
        self.staff=get_user_model().objects.create_user('operator',is_staff=True,is_superuser=True)

    def save_tracking(self, **kwargs):
        return self.tracking.register_shipment(self.staff,self.order.pk,carrier='DHL',
            tracking_number='1234567890',tracking_url='https://www.dhl.com/mx-es/home/rastreo.html',
            status=kwargs.get('status','shipped'))

    def test_paid_order_tracking_visible_only_to_owner(self):
        shipment=self.save_tracking()
        self.assertEqual(shipment.order_id,self.order.pk)
        url=f'/pedido/{self.order.public_id}/'
        self.client.force_login(self.customer.user,backend='accounts.backends.CustomerEmailBackend')
        self.assertContains(self.client.get(url),'1234567890')
        self.assertContains(self.client.get(url),'En camino')
        self.save_tracking(status='delivered')
        self.assertContains(self.client.get(url),'Entregado')

    def test_permission_unpaid_canceled_and_unsafe_url_rejected(self):
        with self.assertRaises(PermissionDenied):
            self.tracking.register_shipment(self.customer.user,self.order.pk,carrier='DHL',tracking_number='x')
        with self.assertRaises(ValidationError):
            self.tracking.register_shipment(self.staff,self.order.pk,carrier='DHL',tracking_number='x',tracking_url='javascript:alert(1)')
        self.attempt.state='open'; self.attempt.save()
        with self.assertRaises(ValidationError): self.save_tracking()
        self.attempt.state='paid'; self.attempt.save()
        self.request()
        with self.assertRaises(ValidationError): self.save_tracking()

    def test_admin_form_and_audit_log(self):
        from django.contrib.admin.models import LogEntry
        self.client.force_login(self.staff)
        url=f'/admin/orders/order/{self.order.pk}/shipment/'
        response=self.client.post(url,{'carrier':'DHL','tracking_number':'TRACK123','status':'shipped'})
        self.assertEqual(response.status_code,302)
        self.assertEqual(self.order.shipment.tracking_number,'TRACK123')
        self.assertTrue(LogEntry.objects.filter(user=self.staff,object_id=str(self.order.pk)).exists())


def load_tests(loader, tests, pattern):
    import unittest
    return unittest.TestSuite(TrackingTests(name) for name in TrackingTests.__dict__ if name.startswith('test_'))
