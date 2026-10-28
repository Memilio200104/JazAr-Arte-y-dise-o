from django.core.management.base import BaseCommand
from django.db import transaction
from shipping.models import PackageProfile, ProductPacking
from website.models import Product


class Command(BaseCommand):
    help = 'Completa empaques provisionales del catalogo conocido sin sobrescribir ediciones.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true')

    @transaction.atomic
    def handle(self, *args, **options):
        profiles = [
            ('textiles', 'Caja textiles', 35, 25, 20, '.250', 5, 6),
            ('tazas', 'Caja tazas protegidas', 35, 25, 20, '.350', 5, 4),
            ('voluminosos', 'Caja articulos voluminosos', 50, 40, 35, '.700', 10, 4),
            ('bebidas', 'Caja termos y vasos protegidos', 40, 30, 35, '.500', 10, 6),
            ('planos', 'Caja articulos planos protegidos', 45, 35, 18, '.450', 8, 6),
            ('accesorios', 'Caja accesorios', 35, 25, 25, '.300', 5, 6),
            ('enrollados', 'Caja textiles enrollados', 40, 20, 20, '.300', 5, 4),
            ('globos', 'Caja globo protegido', 60, 60, 60, '.600', 3, 1),
        ]
        for code, name, length, width, height, tare, maximum, capacity in profiles:
            if options['apply']:
                _, created = PackageProfile.objects.get_or_create(code=code, defaults=dict(name=name,
                    length_cm=length, width_cm=width, height_cm=height, tare_kg=tare,
                    max_weight_kg=maximum, capacity=capacity))
                self.stdout.write(f'{code}: {"creado" if created else "conservado"}')
            else:
                self.stdout.write(f'{code}: sin cambios (usa --apply)')
        # Provisional weights include protection per sales unit (pair/set where sold as such).
        # Only explicit catalogue SKUs: unknown products need individual configuration.
        assignments = {
            'tazas': ('0.550', 1, ['JAZ-C03-01', 'JAZ-C03-02', 'JAZ-C03-04', 'JAZ-C04-01',
                'JAZ-C04-02', 'JAZ-C04-03', 'JAZ-C04-04', 'JAZ-C05-01', 'JAZ-C05-02',
                'JAZ-C06-01', 'JAZ-C06-02', 'JAZ-C06-03']),
            'textiles': ('0.350', 1, ['JAZ-C14-01', 'JAZ-C14-02', 'JAZ-C14-03', 'JAZ-C14-04',
                'JAZ-C14-05', 'JAZ-C15-01', 'JAZ-C15-02', 'JAZ-C15-03', 'JAZ-C15-04',
                'JAZ-C15-05', 'JAZ-C16-01', 'JAZ-C16-02', 'JAZ-C16-03', 'JAZ-C18-01',
                'JAZ-C18-02', 'JAZ-C19-01', 'JAZ-C20-01', 'JAZ-C20-02', 'JAZ-C20-03']),
        }
        remaining = [
            ('tazas', '1.100', 2, ['C03-03']),
            ('bebidas', '.750', 2, ['C08-01', 'C08-02', 'C08-03']),
            ('bebidas', '.200', 1, ['C08-04']),
            ('bebidas', '.550', 1, ['C10-01', 'C10-02', 'C10-03', 'C11-01', 'C11-02', 'C11-03', 'C12-01', 'C12-03']),
            ('bebidas', '.700', 2, ['C12-02']),
            ('textiles', '.800', 2, ['C17-01', 'C17-02', 'C17-03', 'C17-04', 'C17-05', 'C17-06']),
            ('textiles', '.450', 1, ['C18-03']),
            ('accesorios', '.250', 2, ['C19-02', 'C19-03']),
            ('voluminosos', '.800', 2, ['C21-01']),
            ('textiles', '.150', 1, ['C21-02', 'C21-03', 'C31-02', 'C31-03']),
            ('planos', '.250', 1, ['C22-01']),
            ('enrollados', '.600', 2, ['C22-02']),
            ('planos', '.200', 1, ['C22-03']),
            ('planos', '.300', 1, ['C22-04']),
            ('planos', '1.200', 2, ['C24-01']),
            ('planos', '.900', 2, ['C24-02', 'C25-01']),
            ('planos', '1.500', 2, ['C24-03']),
            ('planos', '.350', 1, ['C25-02']),
            ('accesorios', '.100', 1, ['C25-03', 'C31-01']),
            ('voluminosos', '.500', 2, ['C26-01']),
            ('globos', '.150', 1, ['C27-01']),
            ('bebidas', '.300', 1, ['C28-01', 'C28-04', 'C28-05']),
            ('bebidas', '.450', 2, ['C28-02', 'C28-03']),
            ('planos', '.500', 1, ['C30-01']),
            ('planos', '.050', 1, ['C30-02']),
        ]
        rows = [(code, weight, units, skus) for code, (weight, units, skus) in assignments.items()]
        rows.extend((code, weight, units, ['JAZ-' + sku for sku in skus])
                    for code, weight, units, skus in remaining)
        if options['apply']:
            for code, weight, units, skus in rows:
                profile = PackageProfile.objects.get(code=code)
                for product in Product.objects.filter(sku__in=skus, sale_mode='fixed', is_concept=False):
                    ProductPacking.objects.get_or_create(product=product, defaults=dict(profile=profile,
                        protected_unit_weight_kg=weight, capacity_units=units))
            missing = Product.objects.filter(sale_mode='fixed', is_concept=False, packing__isnull=True).count()
            self.stdout.write(f'Productos de precio fijo sin empaque: {missing}. Los perfiles requieren validacion fisica antes de produccion.')
