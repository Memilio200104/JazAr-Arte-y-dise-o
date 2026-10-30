from django.core.management.base import BaseCommand
from website.models import Product


class Command(BaseCommand):
    help = 'Inicializa solo existencias desconocidas de productos fijos reales. Vista previa sin --apply.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true')

    def handle(self, *args, **options):
        products = Product.objects.filter(is_concept=False, sale_mode='fixed')
        missing = products.filter(stock__isnull=True)
        count = missing.count()
        other = products.filter(stock__isnull=False).exclude(stock=30).count()
        if options['apply']:
            count = missing.update(stock=30)
        self.stdout.write(f'{"Actualizados" if options["apply"] else "Por inicializar"}: {count}. Valores definidos distintos de 30 conservados: {other}.')
