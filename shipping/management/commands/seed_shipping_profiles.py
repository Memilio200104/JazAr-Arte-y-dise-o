from django.core.management.base import BaseCommand
from shipping.models import PackageProfile, ProductPacking
from website.models import Product


class Command(BaseCommand):
    help = 'Crea cajas provisionales sin sobrescribir datos existentes. No asigna productos ambiguos.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true')

    def handle(self, *args, **options):
        profiles = [
            ('textiles', 'Caja textiles', 35, 25, 20, '.250', 5, 6),
            ('tazas', 'Caja tazas protegidas', 35, 25, 20, '.350', 5, 4),
            ('voluminosos', 'Caja articulos voluminosos', 50, 40, 35, '.700', 10, 4),
        ]
        for code, name, length, width, height, tare, maximum, capacity in profiles:
            if options['apply']:
                _, created = PackageProfile.objects.get_or_create(code=code, defaults=dict(name=name,
                    length_cm=length, width_cm=width, height_cm=height, tare_kg=tare,
                    max_weight_kg=maximum, capacity=capacity))
                self.stdout.write(f'{code}: {"creado" if created else "conservado"}')
            else:
                self.stdout.write(f'{code}: sin cambios (usa --apply)')
        # Explicit catalogue SKUs only; unknown/fragile formats need individual review.
        assignments = {
            'tazas': ('0.550', 1, ['JAZ-C03-01', 'JAZ-C03-02', 'JAZ-C03-04', 'JAZ-C04-01',
                'JAZ-C04-02', 'JAZ-C04-03', 'JAZ-C04-04', 'JAZ-C05-01', 'JAZ-C05-02',
                'JAZ-C06-01', 'JAZ-C06-02', 'JAZ-C06-03']),
            'textiles': ('0.350', 1, ['JAZ-C14-01', 'JAZ-C14-02', 'JAZ-C14-03', 'JAZ-C14-04',
                'JAZ-C14-05', 'JAZ-C15-01', 'JAZ-C15-02', 'JAZ-C15-03', 'JAZ-C15-04',
                'JAZ-C15-05', 'JAZ-C16-01', 'JAZ-C16-02', 'JAZ-C16-03', 'JAZ-C18-01',
                'JAZ-C18-02', 'JAZ-C19-01', 'JAZ-C20-01', 'JAZ-C20-02', 'JAZ-C20-03']),
        }
        if options['apply']:
            for code, (weight, units, skus) in assignments.items():
                profile = PackageProfile.objects.get(code=code)
                for product in Product.objects.filter(sku__in=skus, sale_mode='fixed', is_concept=False):
                    ProductPacking.objects.get_or_create(product=product, defaults=dict(profile=profile,
                        protected_unit_weight_kg=weight, capacity_units=units))
