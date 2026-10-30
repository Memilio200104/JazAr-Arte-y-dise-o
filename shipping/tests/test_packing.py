from decimal import Decimal
from io import StringIO

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from orders.tests.test_models import ModelTests, product
from orders.models import OrderItem
from shipping.models import PackageProfile, ProductPacking
from shipping.packing import pack_order


class PackingTests(TestCase):
    def setUp(self):
        ModelTests.setUp(self)
        self.box = PackageProfile.objects.create(code='textiles', name='Textiles', length_cm=30,
            width_cm=20, height_cm=15, tare_kg='0.100', max_weight_kg=5, capacity=4)

    def add(self, quantity=1, box=None, weight='0.200', units=1):
        item = product(stock=30)
        ProductPacking.objects.create(product=item, profile=box or self.box,
            protected_unit_weight_kg=weight, capacity_units=units)
        OrderItem.objects.create(order=self.order, product=item, quantity=quantity,
            unit_price=10, sku=item.sku, name=item.name)
        return item

    def test_shared_box_and_weight(self):
        self.add(); self.add()
        result = pack_order(self.order)
        self.assertEqual(len(result.packages), 1)
        self.assertEqual(Decimal(result.packages[0]['weight']), Decimal('0.500'))
        self.assertEqual(sum(x['quantity'] for x in result.packages[0]['items']), 2)
        self.assertEqual(result, pack_order(self.order))

    def test_capacity_splits_without_losing_units(self):
        self.add(quantity=5)
        result = pack_order(self.order)
        self.assertEqual([sum(i['quantity'] for i in p['items']) for p in result.packages], [4, 1])

    def test_weight_limit_and_incompatible_profiles(self):
        self.box.max_weight_kg = Decimal('0.4'); self.box.save()
        self.add(quantity=2)
        other = PackageProfile.objects.create(code='fragile', name='Fragil', length_cm=20,
            width_cm=20, height_cm=20, tare_kg='.1', max_weight_kg=2, capacity=2)
        self.add(box=other)
        self.assertEqual(len(pack_order(self.order).packages), 3)

    def test_missing_inactive_and_oversized_rejected(self):
        item = self.add(units=5)
        with self.assertRaises(ValidationError): pack_order(self.order)
        ProductPacking.objects.filter(product=item).update(capacity_units=1, protected_unit_weight_kg=6)
        with self.assertRaises(ValidationError): pack_order(self.order)
        ProductPacking.objects.filter(product=item).update(protected_unit_weight_kg='.2')
        self.box.active = False; self.box.save()
        with self.assertRaises(ValidationError): pack_order(self.order)
        ProductPacking.objects.filter(product=item).delete()
        with self.assertRaises(ValidationError): pack_order(self.order)

    def test_edit_changes_fingerprint_and_clears_validation(self):
        from django.utils import timezone
        item = self.add()
        before = pack_order(self.order)
        self.box.validated_at = timezone.now(); self.box.save()
        self.box.width_cm = 25; self.box.save()
        self.assertIsNone(self.box.validated_at)
        self.assertNotEqual(before.fingerprint, pack_order(self.order).fingerprint)
        packing = item.packing
        packing.validated_at = timezone.now(); packing.save()
        packing.capacity_units = 2; packing.save()
        self.assertIsNone(packing.validated_at)

    def test_positive_values(self):
        self.box.tare_kg = -1
        with self.assertRaises(ValidationError): self.box.full_clean()
        self.box.capacity = 0
        with self.assertRaises(ValidationError): self.box.full_clean()

    def test_seed_dry_run_and_preserves_edits(self):
        mug = product(stock=30)
        type(mug).objects.filter(pk=mug.pk).update(sku='JAZ-C03-01')
        call_command('seed_shipping_profiles', stdout=StringIO())
        self.assertEqual(PackageProfile.objects.count(), 1)
        call_command('seed_shipping_profiles', apply=True, stdout=StringIO())
        count = PackageProfile.objects.count()
        self.assertEqual(ProductPacking.objects.get(product=mug).profile.code, 'tazas')
        self.box.refresh_from_db(); self.assertEqual(self.box.width_cm, 20)
        call_command('seed_shipping_profiles', apply=True, stdout=StringIO())
        self.assertEqual(PackageProfile.objects.count(), count)
