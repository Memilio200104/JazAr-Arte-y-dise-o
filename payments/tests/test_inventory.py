from unittest.mock import patch
from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError
from orders.tests.test_models import ModelTests
from orders.models import OrderItem
from shipping.tests.test_quotes import QuoteTests, ORIGIN
from shipping.envia import Rate
from shipping.services import fetch_order_rates
from payments.inventory import reserve_order, consume_reservation, release_reservation


@override_settings(SHIPPING_ORIGIN=ORIGIN)
class InventoryTests(TestCase):
    add = QuoteTests.add

    def setUp(self):
        QuoteTests.setUp(self)
        self.order.subtotal = 50
        self.order.save()
        with patch('shipping.services.quote_rates', return_value=[Rate('dhl','ground',10000,'MXN')]):
            self.quote = fetch_order_rates(self.customer, self.order.pk)[0]

    def test_reserve_consume_exactly_once(self):
        attempt = reserve_order(self.order.pk, self.quote.pk)
        p = self.order.items.first().product
        p.refresh_from_db(); self.assertEqual(p.reserved_stock, 5); self.assertEqual(p.stock,30)
        self.assertEqual(reserve_order(self.order.pk, self.quote.pk).pk, attempt.pk)
        consume_reservation(attempt.pk); consume_reservation(attempt.pk)
        p.refresh_from_db(); self.assertEqual(p.stock,25); self.assertEqual(p.reserved_stock,0)

    def test_release_and_unavailable(self):
        attempt = reserve_order(self.order.pk, self.quote.pk)
        release_reservation(attempt.pk); release_reservation(attempt.pk)
        p = self.order.items.first().product
        p.refresh_from_db(); self.assertEqual(p.stock,30); self.assertEqual(p.reserved_stock,0)

    def test_no_partial_reservation(self):
        p = self.order.items.first().product
        p.stock = 4; p.save()
        with self.assertRaises(ValidationError): reserve_order(self.order.pk,self.quote.pk)
        p.refresh_from_db(); self.assertEqual(p.reserved_stock,0)
        self.assertEqual(self.order.payment_attempts.count(),0)

    def test_admin_cannot_reduce_reserved_stock(self):
        reserve_order(self.order.pk,self.quote.pk)
        p = self.order.items.first().product
        p.stock = 0
        with self.assertRaises(ValidationError): p.full_clean()

    def test_stale_product_save_does_not_restore_sold_stock(self):
        stale=self.order.items.first().product
        attempt=reserve_order(self.order.pk,self.quote.pk)
        consume_reservation(attempt.pk)
        stale.name='Nuevo nombre'; stale.save()
        stale.refresh_from_db(); self.assertEqual(stale.stock,25)

    def test_null_stock_cannot_hide_active_reservations(self):
        from django.db import IntegrityError, transaction
        from website.models import Product
        reserve_order(self.order.pk,self.quote.pk)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Product.objects.filter(pk=self.order.items.first().product_id).update(stock=None)

    def test_admin_stale_form_is_rejected(self):
        from django.core import signing
        from website.admin_forms import ProductAdminForm
        stale=self.order.items.first().product
        token=signing.dumps({'pk':stale.pk,'stock':stale.stock},salt='product-stock')
        attempt=reserve_order(self.order.pk,self.quote.pk); consume_reservation(attempt.pk)
        stale.refresh_from_db()
        form=ProductAdminForm(data={'name':'Editar','stock':30,'stock_snapshot':token},instance=stale)
        self.assertFalse(form.is_valid())
        self.assertIn('Las existencias cambiaron',str(form.non_field_errors()))

    def test_refreshed_product_can_edit_without_restock(self):
        stale=self.order.items.first().product
        attempt=reserve_order(self.order.pk,self.quote.pk); consume_reservation(attempt.pk)
        stale.refresh_from_db(); stale.name='Nombre actualizado'; stale.save()
        stale.refresh_from_db(); self.assertEqual(stale.stock,25)

    def test_detail_disables_fully_reserved_product(self):
        p=self.order.items.first().product
        p.stock=5; p.save()
        reserve_order(self.order.pk,self.quote.pk)
        self.assertContains(self.client.get('/productos/'+p.slug+'/'),'Sin existencias')
