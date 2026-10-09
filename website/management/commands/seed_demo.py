from django.core.management.base import BaseCommand

from website.catalog import PRODUCTS
from website.models import Product


class Command(BaseCommand):
    help = "Crea conceptos de catálogo sin precios ni stock ficticios. No modifica productos existentes."

    def handle(self, *args, **options):
        created = 0
        for index, product in enumerate(PRODUCTS):
            _, is_new = Product.objects.get_or_create(slug=product["id"], defaults={
                "sku": f"DEMO-{index + 1:03d}", "name": product["name"],
                "description": product["description"], "category": product["interest"],
                "technique_key": product["technique_key"], "image": product["image"],
                "sort_order": index, "is_concept": True,
            })
            created += int(is_new)
        self.stdout.write(self.style.SUCCESS(f"Catálogo listo: {created} conceptos nuevos. Productos existentes conservados."))
