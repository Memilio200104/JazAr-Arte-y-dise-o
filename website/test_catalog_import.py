from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from .models import Product


class ClientCatalogTests(TestCase):
    def test_complete_catalog_pages_prices_and_black_textiles(self):
        call_command('import_client_catalog')
        self.assertEqual(set(Product.objects.exclude(catalog_page=None).values_list('catalog_page', flat=True)),
                         {3,4,5,6,8,10,11,12,14,15,16,17,18,19,20,21,22,24,25,26,27,28,29,30,31})
        self.assertEqual(Product.objects.get(sku='JAZ-C14-03').technique_key, 'dtf')
        self.assertEqual(Product.objects.get(sku='JAZ-C15-01').technique_key, 'dtf')
        self.assertEqual(Product.objects.get(sku='JAZ-C26-01').price, Decimal('150'))
        self.assertEqual(Product.objects.get(sku='JAZ-C26-02').sale_mode, 'quote')
        self.assertTrue(Product.objects.get(sku='JAZ-C29-01').is_active)
        self.assertEqual(Product.objects.get(sku='JAZ-C28-04').price, Decimal('35'))

    def test_sale_mode_is_explicit_not_inferred_from_price(self):
        product = Product(price=Decimal('100'))
        self.assertEqual(product.sale_mode, 'quote')

    def test_fixed_price_requires_price_and_custom_3d_requires_quote(self):
        product = Product(sale_mode='fixed')
        with self.assertRaises(ValidationError):
            product.clean()
        product.price = Decimal('100')
        product.clean()
        product.technique_key = '3d'
        with self.assertRaises(ValidationError):
            product.clean()

    def test_client_import_preserves_editor_changes_and_modes(self):
        call_command('import_client_catalog')
        mug = Product.objects.get(sku='JAZ-C03-01')
        self.assertEqual(mug.price, Decimal('65'))
        self.assertEqual(mug.sale_mode, 'fixed')
        self.assertFalse(mug.is_concept)
        self.assertEqual(Product.objects.get(sku='JAZ-C29-01').sale_mode, 'quote')
        self.assertEqual(Product.objects.get(sku='JAZ-3D').sale_mode, 'quote')
        count = Product.objects.count()
        mug.name = 'Edited by owner'
        mug.save()
        call_command('import_client_catalog')
        mug.refresh_from_db()
        self.assertEqual(mug.name, 'Edited by owner')
        self.assertEqual(Product.objects.count(), count)

    def test_contact_social_links_and_no_fake_checkout(self):
        response = self.client.get('/')
        self.assertContains(response, 'https://wa.me/525539754777')
        self.assertContains(response, 'icons/facebook.svg')
        self.assertContains(response, 'icons/whatsapp.svg')
        self.assertNotContains(response, '/checkout')
