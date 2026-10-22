from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import OperationalError
from django.test import Client, TestCase
from orders.services import review_order, ReviewConflict, create_order
from orders.quotes import sign_quote
from .test_requests import RequestTests
from uuid import uuid4


class ReviewTests(TestCase):
    quote=RequestTests.quote

    def setUp(self):
        RequestTests.setUp(self)
        self.order,_=create_order(self.customer,sign_quote(self.quote()),uuid4())
        self.staff=get_user_model().objects.create_user('staff',is_staff=True)
        self.staff.user_permissions.add(*Permission.objects.filter(content_type__app_label='orders',codename__in=['view_order','approve_order']))

    def test_permissions_and_transitions(self):
        with self.assertRaises(PermissionDenied): review_order(self.customer.user,self.order.pk,0,'approved','')
        approved=review_order(self.staff,self.order.pk,0,'approved','Bien')
        self.assertEqual(approved.approved_by,self.staff)
        self.assertIsNotNone(approved.approved_at)
        same=review_order(self.staff,self.order.pk,1,'approved','Bien')
        self.assertEqual(same.approved_at,approved.approved_at)
        self.assertEqual(same.review_events.count(),1)
        with self.assertRaises(ReviewConflict): review_order(self.staff,self.order.pk,0,'pending','')
        with self.assertRaises(ValidationError): review_order(self.staff,self.order.pk,1,'changes','')
        changed=review_order(self.staff,self.order.pk,1,'changes','Enviar PNG')
        self.assertIsNone(changed.approved_at); self.assertIsNone(changed.approved_by)
        self.assertEqual(changed.review_events.count(),2)

    def test_review_rollback(self):
        with patch('orders.services.OrderReviewEvent.objects.create',side_effect=OperationalError):
            with self.assertRaises(OperationalError): review_order(self.staff,self.order.pk,0,'approved','')
        self.order.refresh_from_db(); self.assertEqual(self.order.review_status,'pending')

    def test_admin_review(self):
        self.client.force_login(self.staff)
        url=f'/admin/orders/order/{self.order.pk}/review/'
        self.assertContains(self.client.get(f'/admin/orders/order/{self.order.pk}/change/'),'Diseño revisado')
        response=self.client.post(url,{'approved':'on','version':0,'note':'','subtotal':'1','customer':999})
        self.assertEqual(response.status_code,302)
        self.order.refresh_from_db(); self.assertEqual(self.order.review_status,'approved')
        self.assertEqual(str(self.order.subtotal),'399.80')
        self.assertEqual(self.client.post(url,{'version':0,'note':''}).status_code,409)
        with patch('orders.admin.review_order',side_effect=OperationalError):
            self.assertEqual(self.client.post(url,{'version':1,'note':''}).status_code,503)
        csrf=Client(enforce_csrf_checks=True); csrf.force_login(self.staff)
        self.assertEqual(csrf.post(url,{'version':1}).status_code,403)
        self.staff.user_permissions.clear()
        self.assertEqual(self.client.post(url,{'version':1}).status_code,403)
