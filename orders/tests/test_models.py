from io import StringIO
from uuid import uuid4
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from accounts.models import CustomerProfile
from website.models import Product
from orders.models import Order, OrderItem


def product(**kwargs):
    return Product.objects.create(**dict(name='Taza', slug=str(uuid4()), sku=str(uuid4()).upper(),
        description='Arte', category='regalos', technique_key='sublimacion', price='199.90',
        sale_mode='fixed', is_active=True, is_concept=False, **kwargs))


class ModelTests(TestCase):
    def setUp(self):
        self.customer = CustomerProfile.objects.create(user=get_user_model().objects.create_user('buyer'), full_name='Cliente', email='buyer@example.com')
        self.product = product(stock=30)
        self.order = Order.objects.create(customer=self.customer, subtotal='199.90', shipping_address={}, idempotency_key=uuid4(), request_digest='a'*64)

    def test_constraints_and_protection(self):
        for quantity, price in [(0, '10'), (1, '-1')]:
            with self.assertRaises(IntegrityError), transaction.atomic():
                OrderItem.objects.create(order=self.order, product=self.product, quantity=quantity, unit_price=price, sku='X', name='Taza')
        OrderItem.objects.create(order=self.order, product=self.product, quantity=1, unit_price='199.90', sku='X', name='Taza')
        with self.assertRaises(ProtectedError): self.product.delete()
        with self.assertRaises(ProtectedError): self.customer.delete()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Order.objects.create(customer=self.customer, subtotal=0, shipping_address={}, idempotency_key=self.order.idempotency_key, request_digest='b'*64)

    def test_stock_initialization(self):
        missing = product(stock=None)
        zero = product(stock=0)
        twelve = product(stock=12)
        excluded = product(stock=None)
        Product.objects.filter(pk=excluded.pk).update(sale_mode='quote')
        call_command('initialize_order_stock', stdout=StringIO())
        missing.refresh_from_db(); self.assertIsNone(missing.stock)
        call_command('initialize_order_stock', apply=True, stdout=StringIO())
        for p, expected in [(missing,30),(zero,0),(twelve,12),(self.product,30),(excluded,None)]:
            p.refresh_from_db(); self.assertEqual(p.stock,expected)
