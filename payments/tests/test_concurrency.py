from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4
from unittest.mock import patch
from django.test import TransactionTestCase, override_settings
from django.db import close_old_connections, DatabaseError
from django.core.exceptions import ValidationError
from orders.models import Order, OrderItem
from shipping.services import fetch_order_rates
from shipping.envia import Rate
from shipping.tests.test_quotes import ORIGIN
from payments.tests import test_inventory as fixtures
from payments.inventory import reserve_order
from payments.models import PaymentAttempt


@override_settings(SHIPPING_ORIGIN=ORIGIN)
class ReservationConcurrencyTests(TransactionTestCase):
    add=fixtures.InventoryTests.add
    setUp=fixtures.InventoryTests.setUp

    def test_two_orders_cannot_reserve_same_last_stock(self):
        row=self.order.items.first()
        product=row.product; product.stock=5; product.save()
        other=Order.objects.create(customer=self.customer,subtotal=50,shipping_address=self.order.shipping_address,
            review_status='approved',idempotency_key=uuid4(),request_digest='b'*64)
        OrderItem.objects.create(order=other,product=product,quantity=5,unit_price=10,name=product.name,sku=product.sku)
        with patch('shipping.services.quote_rates',return_value=[Rate('dhl','ground',10000,'MXN')]):
            quote=fetch_order_rates(self.customer,other.pk)[0]
        barrier=Barrier(2)
        def reserve(pair):
            close_old_connections(); barrier.wait()
            try:
                return reserve_order(*pair).pk
            except (DatabaseError,ValidationError):
                return None
            finally:
                close_old_connections()
        with ThreadPoolExecutor(2) as pool:
            results=list(pool.map(reserve,[(self.order.pk,self.quote.pk),(other.pk,quote.pk)]))
        self.assertEqual(sum(value is not None for value in results),1)
        product.refresh_from_db(); self.assertEqual(product.stock,5); self.assertEqual(product.reserved_stock,5)
        self.assertEqual(PaymentAttempt.objects.count(),1)
