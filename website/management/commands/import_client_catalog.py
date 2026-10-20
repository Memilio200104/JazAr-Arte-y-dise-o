from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from website.models import Product, SiteContent
from website.client_catalog import EXTRA_ITEMS


# Prices and units transcribed from the supplied 2026 catalog, not inferred.
ITEMS = [
    ('C03-01', 'Taza blanca', 'taza-blanca', 3, '65', 'Precio por taza.', 'regalos', 'sublimacion'),
    ('C03-03', 'Tazas para pareja', 'tazas-pareja', 3, '120', 'Precio por par.', 'regalos', 'sublimacion'),
    ('C06-01', 'Taza mágica', 'taza-magica', 6, '100', 'Precio por taza.', 'regalos', 'sublimacion'),
    ('C10-01', 'Termo recto 400 ml', 'termo-recto', 10, '250', 'Capacidad de 400 ml.', 'regalos', 'personalizacion'),
    ('C14-01', 'Playera blanca infantil', 'playera-blanca', 14, '130', 'Tallas infantiles 2 a 14. Sublimación.', 'prendas', 'sublimacion'),
    ('C14-02', 'Playera blanca adulto', 'playera-blanca', 14, '150', 'Tallas S a XL. Sublimación.', 'prendas', 'sublimacion'),
    ('C20-01', 'Bolsa de lona', 'bolsa-lona', 20, '150', 'Medidas: 40 × 35 cm.', 'textiles', 'personalizacion'),
    ('C24-01', 'Cuadro de cristal', 'cuadro-cristal', 24, '180', 'Cuadro personalizado.', 'regalos', 'personalizacion'),
    ('C30-01', 'Libreta con notas y pluma', 'libreta', 30, '130', 'Incluye notas adhesivas y pluma.', 'regalos', 'personalizacion'),
    ('C30-02', 'Separador acrílico', 'separador', 30, '45', 'Precio por separador.', 'regalos', 'personalizacion'),
]


class Command(BaseCommand):
    help = 'Importa el catálogo del cliente sin sobrescribir ediciones.'

    def add_arguments(self, parser):
        parser.add_argument('--update-site', action='store_true', help='Aplicar textos y retrato del cliente a la portada.')
        parser.add_argument('--hide-demo', action='store_true', help='Ocultar exclusivamente productos conceptuales con SKU DEMO-.')

    @transaction.atomic
    def handle(self, *args, **options):
        created = 0
        for order, (code, name, image, page, price, note, category, technique) in enumerate(ITEMS + EXTRA_ITEMS):
            _, new = Product.objects.get_or_create(sku='JAZ-' + code, defaults={
                'name': name, 'slug': code.lower() + '-' + image, 'description': note,
                'category': category, 'technique_key': technique, 'price': Decimal(price) if price else None,
                'sale_mode': 'fixed' if price else 'quote', 'catalog_page': page, 'price_note': note,
                'image': f'images/client/{image}.webp', 'image_alt': name + ', fotografía del catálogo JazAr',
                'is_active': True, 'is_concept': False, 'sort_order': order,
            })
            created += new
        for index, name in enumerate(['Servilletas para evento', 'Pantuflas para evento', 'Toallas faciales', 'Llaveros acrílicos'], 1):
            product, new = Product.objects.get_or_create(sku=f'JAZ-C29-0{index}', defaults={
                'name': name, 'slug': f'evento-c29-0{index}', 'description': 'Personalizados. Se cotiza por mayoreo.',
                'category': 'regalos', 'technique_key': 'personalizacion', 'sale_mode': 'quote',
                'catalog_page': 29, 'is_concept': False,
                'image': f'images/client/c29-0{index}.webp', 'image_alt': name + ', ejemplo del catálogo JazAr',
                'is_active': True, 'sort_order': 100 + index,
            })
            # Upgrade only untouched placeholder drafts created by the first import.
            if not new and not product.is_active and product.image == 'images/collection-concept.webp' and not product.photo and product.name == name and product.description == 'Personalizados. Se cotiza por mayoreo.':
                product.image = f'images/client/c29-0{index}.webp'
                product.image_alt = name + ', ejemplo del catálogo JazAr'
                product.is_active = True
                product.sort_order = 100 + index
                product.save()
            created += new
        _, new = Product.objects.get_or_create(sku='JAZ-3D', defaults={
            'name': 'Tu pieza en impresión 3D', 'slug': 'impresion-3d-personalizada',
            'description': 'Cotizamos según tamaño, cantidad de filamento, colores y detalle de la pieza.',
            'category': 'piezas-3d', 'technique_key': '3d', 'sale_mode': 'quote',
            'image': 'images/client/impresora-3d.webp', 'image_alt': 'Impresora 3D en el taller de JazAr',
            'is_active': True, 'is_concept': False, 'sort_order': 20,
        })
        created += new
        if options['hide_demo']:
            Product.objects.filter(sku__startswith='DEMO-', is_concept=True).update(is_active=False)
        if options['update_site']:
            site = SiteContent.objects.first() or SiteContent()
            site.hero_title = 'Personalizamos tus ideas, creamos momentos únicos.'
            site.hero_description = 'Prendas, regalos y accesorios para ti, tu negocio y tus celebraciones. Diseño gráfico y personalización con Jazmin Zarate.'
            site.intro_title = 'Hola, soy Jazmin.'
            site.intro_text = 'Soy diseñadora gráfica y estoy detrás de JazAr Arte y Diseño. Transformo tus ideas en prendas, tazas, termos, stickers y detalles personalizados. Para un regalo, una celebración o la presentación de tu negocio: tú imaginas, nosotros lo personalizamos.'
            site.intro_alt = 'Jazmin Zarate, diseñadora gráfica y propietaria de JazAr'
            with (Path(settings.BASE_DIR) / 'static/images/client/jazmin.webp').open('rb') as source:
                site.intro_photo = File(source, name='jazmin.webp')
                site.save()
        self.stdout.write(self.style.SUCCESS(f'{created} productos creados. Los registros existentes se conservaron.'))
