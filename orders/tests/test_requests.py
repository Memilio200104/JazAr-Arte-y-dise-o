from datetime import timedelta
from uuid import uuid4
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import OperationalError
from django.test import TestCase
from django.utils import timezone
from accounts.models import CustomerProfile, ShippingAddress
from orders.models import Order, OrderCreationBucket
from orders.quotes import build_quote, sign_quote
from orders.services import create_order, QuoteChanged, OrderRateLimited
from .test_models import product


class RequestTests(TestCase):
    def setUp(self):
        self.customer=CustomerProfile.objects.create(user=get_user_model().objects.create_user('buyer'),email='buyer@example.com',full_name='Cliente')
        self.address=ShippingAddress.objects.create(customer=self.customer,recipient='Persona',phone='5512345678',street='Calle',exterior='1',district='Centro',postcode='01234',city='Ciudad',state='Estado')
        self.product=product(stock=30)
        self.rows=[{'id':self.product.pk,'quantity':2,'details':'Azul'}]

    def quote(self):
        return build_quote(self.customer,self.rows,self.address.pk,'Idea')

    def test_validation(self):
        bad=[[],self.rows*101,self.rows*2,[{'id':True,'quantity':1,'details':''}]]
        bad += [[{**self.rows[0],'quantity':n}] for n in [True,0,-1,31,100,1.5,'2']]
        bad += [[{**self.rows[0],'details':'x'*301}]]
        for rows in bad:
            with self.subTest(rows=str(rows)[:80]),self.assertRaises(ValidationError):
                build_quote(self.customer,rows,self.address.pk,'')
        with self.assertRaises(ValidationError): build_quote(self.customer,self.rows,self.address.pk,'x'*1501)
        with self.assertRaises(ValidationError): build_quote(self.customer,self.rows,999,'')
        for field,value in [('stock',None),('is_active',False),('is_concept',True),('sale_mode','quote')]:
            original=getattr(self.product,field)
            type(self.product).objects.filter(pk=self.product.pk).update(**{field:value})
            with self.assertRaises(ValidationError): self.quote()
            type(self.product).objects.filter(pk=self.product.pk).update(**{field:original})

    def test_create_snapshot_and_idempotency(self):
        token=sign_quote(self.quote()); key=uuid4()
        order,created=create_order(self.customer,token,key)
        self.assertTrue(created); self.assertEqual(str(order.subtotal),'399.80')
        self.product.price='10'; self.product.save()
        self.address.street='Otra'; self.address.save()
        same,created=create_order(self.customer,token,key)
        self.assertFalse(created); self.assertEqual(same.pk,order.pk)
        self.assertEqual(order.shipping_address['street'],'Calle')
        self.assertEqual(str(order.items.get().unit_price),'199.90')
        self.product.refresh_from_db(); self.assertEqual(self.product.stock,30)
        with self.assertRaises(ValidationError): create_order(self.customer,sign_quote(self.quote()),key)

    def test_changed_quote_and_signature(self):
        token=sign_quote(self.quote())
        with self.assertRaises(ValidationError): create_order(self.customer,token+'x',uuid4())
        with patch('django.core.signing.time.time',return_value=1): expired=sign_quote(self.quote())
        with self.assertRaises(ValidationError): create_order(self.customer,expired,uuid4())
        self.product.price='5'; self.product.save()
        with self.assertRaises(QuoteChanged): create_order(self.customer,token,uuid4())
        token=sign_quote(self.quote()); self.address.street='Nueva'; self.address.save()
        with self.assertRaises(QuoteChanged): create_order(self.customer,token,uuid4())

    def test_limits_and_rollback(self):
        token=sign_quote(self.quote()); key=uuid4()
        with patch('orders.services.OrderItem.objects.bulk_create',side_effect=OperationalError):
            with self.assertRaises(OperationalError): create_order(self.customer,token,key)
        self.assertEqual(Order.objects.count(),0); self.assertEqual(OrderCreationBucket.objects.count(),0)
        first,_=create_order(self.customer,token,key)
        for _ in range(9): create_order(self.customer,token,uuid4())
        self.assertEqual(create_order(self.customer,token,key)[0].pk,first.pk)
        with self.assertRaises(OrderRateLimited): create_order(self.customer,token,uuid4())
        OrderCreationBucket.objects.update(started_at=timezone.now()-timedelta(seconds=901))
        self.assertTrue(create_order(self.customer,token,uuid4())[1])
