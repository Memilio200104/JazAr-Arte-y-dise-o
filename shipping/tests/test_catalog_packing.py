from decimal import Decimal
from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from shipping.models import ProductPacking, PackageProfile
from website.models import Product


class CatalogPackingTests(TestCase):
    def setUp(self):
        call_command('import_client_catalog', stdout=StringIO())

    def test_all_fixed_catalog_products_have_valid_provisional_packing(self):
        call_command('seed_shipping_profiles', apply=True, stdout=StringIO())
        products = Product.objects.filter(sale_mode='fixed', is_concept=False)
        self.assertEqual(products.count(), 79)
        self.assertEqual(ProductPacking.objects.count(), 79)
        for product in products:
            packing = product.packing
            packing.full_clean(); packing.profile.full_clean()
            self.assertIsNone(packing.validated_at)
            self.assertGreaterEqual(packing.profile.capacity, packing.capacity_units)
            self.assertGreaterEqual(packing.profile.max_weight_kg,
                packing.profile.tare_kg + packing.protected_unit_weight_kg)
        self.assertFalse(ProductPacking.objects.filter(product__sale_mode='quote').exists())

    def test_pairs_and_sets_represent_one_sales_unit(self):
        call_command('seed_shipping_profiles', apply=True, stdout=StringIO())
        pair = ProductPacking.objects.get(product__sku='JAZ-C03-03')
        mug = ProductPacking.objects.get(product__sku='JAZ-C03-01')
        self.assertEqual(pair.capacity_units, 2 * mug.capacity_units)
        self.assertEqual(pair.protected_unit_weight_kg, 2 * mug.protected_unit_weight_kg)
        four = ProductPacking.objects.get(product__sku='JAZ-C22-03')
        six = ProductPacking.objects.get(product__sku='JAZ-C22-04')
        self.assertGreater(six.protected_unit_weight_kg, four.protected_unit_weight_kg)

    def test_dry_run_and_repeated_seed_preserve_staff_edits(self):
        call_command('seed_shipping_profiles', stdout=StringIO())
        self.assertFalse(ProductPacking.objects.exists())
        self.assertFalse(PackageProfile.objects.exists())
        call_command('seed_shipping_profiles', apply=True, stdout=StringIO())
        packing = ProductPacking.objects.get(product__sku='JAZ-C03-03')
        packing.protected_unit_weight_kg=Decimal('1.250'); packing.save()
        box=packing.profile; box.capacity=8; box.save()
        call_command('seed_shipping_profiles', apply=True, stdout=StringIO())
        packing.refresh_from_db(); box.refresh_from_db()
        self.assertEqual(packing.protected_unit_weight_kg, Decimal('1.250'))
        self.assertEqual(box.capacity, 8)
        self.assertEqual(ProductPacking.objects.count(), 79)
