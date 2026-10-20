from django.urls import reverse
from .models import Product, SiteContent


def eligible_products():
    return Product.objects.filter(is_active=True, is_concept=False, sale_mode="fixed", price__isnull=False)


def store_context():
    return {
        "site_content": SiteContent.objects.first() or SiteContent(),
        "store_products": [{
            "id": p.pk, "name": p.name, "url": reverse("product_detail", args=[p.slug]),
            "image_url": p.image_url, "price_minor": int(p.price * 100),
            "currency": p.currency, "stock": p.stock,
        } for p in eligible_products()],
    }
