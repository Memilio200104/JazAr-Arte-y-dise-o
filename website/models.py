from decimal import Decimal

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


class Product(models.Model):
    class Category(models.TextChoices):
        APPAREL = "prendas", "Prendas"
        GIFTS = "regalos", "Regalos"
        TEXTILES = "textiles", "Textiles"
        THREE_D = "piezas-3d", "Piezas 3D"

    class Technique(models.TextChoices):
        SUBLIMATION = "sublimacion", "Sublimación"
        DTF = "dtf", "DTF"
        THREE_D = "3d", "Impresión 3D"
        CUSTOM = "personalizacion", "Personalización"

    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    sku = models.CharField(max_length=64, unique=True, validators=[
        RegexValidator(r"^[A-Z0-9][A-Z0-9._-]*$", "Usa letras mayúsculas, números, puntos o guiones.")
    ])
    description = models.TextField(max_length=1500)
    category = models.CharField(max_length=16, choices=Category.choices)
    technique_key = models.CharField(max_length=20, choices=Technique.choices)
    image = models.CharField(max_length=255, default="images/collection-concept.webp")
    # Unknown commercial values stay null; a concept is never offered for sale.
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                validators=[MinValueValidator(Decimal("0.00"))])
    currency = models.CharField(max_length=3, default="MXN", choices=[("MXN", "Peso mexicano")])
    stock = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_concept = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "pk"]
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gte=0) | models.Q(price__isnull=True), name="product_price_nonnegative"),
        ]

    def __str__(self):
        return self.name

    @property
    def interest(self):
        return self.category

    @property
    def technique(self):
        return self.get_technique_key_display()
