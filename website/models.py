from decimal import Decimal

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.templatetags.static import static
from .images import process_fields, validate_image


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
    photo = models.ImageField(upload_to='products/', blank=True, validators=[validate_image])
    image_alt = models.CharField(max_length=250, blank=True)
    # Unknown commercial values stay null; a concept is never offered for sale.
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                validators=[MinValueValidator(Decimal("0.00"))])
    currency = models.CharField(max_length=3, default="MXN", choices=[("MXN", "Peso mexicano")])
    stock = models.PositiveIntegerField(null=True, blank=True)
    reserved_stock = models.PositiveIntegerField(default=0, editable=False)
    sale_mode = models.CharField(max_length=8, choices=[('quote', 'Cotización'), ('fixed', 'Precio fijo')], default='quote')
    price_note = models.CharField(max_length=250, blank=True)
    catalog_page = models.PositiveSmallIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_concept = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "pk"]
        constraints = [
            models.CheckConstraint(condition=models.Q(stock__isnull=False, stock__gte=models.F('reserved_stock')) | models.Q(stock__isnull=True, reserved_stock=0), name='product_reservation_within_stock'),
            models.CheckConstraint(condition=models.Q(price__gte=0) | models.Q(price__isnull=True), name="product_price_nonnegative"),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        reserved = type(self).objects.filter(pk=self.pk).values_list('reserved_stock', flat=True).first() if self.pk else self.reserved_stock
        if reserved and (self.stock is None or self.stock < reserved):
            raise ValidationError({'stock': 'No puedes reducir existencias por debajo de las unidades reservadas.'})
        if self.is_active and self.photo and not self.image_alt.strip():
            raise ValidationError({'image_alt': 'Describe la foto antes de publicar.'})
        if self.sale_mode == 'fixed' and self.price is None:
            raise ValidationError({'price': 'Indica el precio fijo antes de guardar.'})
        if self.sale_mode == 'fixed' and self.technique_key == '3d':
            raise ValidationError({'sale_mode': 'Las impresiones 3D personalizadas requieren cotización.'})

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        if 'stock' in field_names:
            instance._loaded_stock = instance.stock
        return instance

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.clean()
        process_fields(self, ['photo'])
        if self.pk and not kwargs.get('force_insert'):
            fields = kwargs.get('update_fields')
            write_stock = fields is None or 'stock' in fields
            if write_stock and 'stock' in self.__dict__:
                original = getattr(self, '_loaded_stock', self.stock)
                if self.stock != original:
                    if not type(self).objects.filter(pk=self.pk, stock=original).update(stock=self.stock):
                        raise ValidationError({'stock': 'Las existencias cambiaron. Recarga antes de guardar.'})
            kwargs['update_fields'] = (set(fields) if fields else {f.name for f in self._meta.concrete_fields if not f.primary_key and f.attname in self.__dict__}) - {'reserved_stock','stock'}
        super().save(*args, **kwargs)
        self._loaded_stock = self.stock

    def refresh_from_db(self, using=None, fields=None, from_queryset=None):
        super().refresh_from_db(using=using, fields=fields, from_queryset=from_queryset)
        if fields is None or 'stock' in fields:
            self._loaded_stock = self.stock

    @property
    def available_stock(self):
        return None if self.stock is None else max(0, self.stock - self.reserved_stock)

    @property
    def has_store_detail(self):
        return self.is_active and not self.is_concept and self.sale_mode == "fixed" and self.price is not None

    @property
    def image_url(self):
        return self.photo.url if self.photo else static(self.display_image)

    @property
    def interest(self):
        return self.category

    @property
    def technique(self):
        return self.get_technique_key_display()

    @property
    def display_image(self):
        if self.is_concept and self.image == "images/collection-concept.webp":
            return {
                "playeras": "images/shirt-concept.webp",
                "tazas": "images/mug-concept.webp",
                "piezas": "images/vase-concept.webp",
            }.get(self.slug, self.image)
        return self.image


class Package(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=160)
    description = models.TextField(max_length=1500)
    inclusions = models.TextField(max_length=1500, default='Definimos piezas, cantidad y fecha de entrega al cotizar.')
    cta = models.CharField(max_length=80, default='Cotizar este paquete')
    interest = models.CharField(max_length=16, choices=[('regalo', 'Regalo'), ('equipo', 'Equipo'), ('marca', 'Marca')], default='regalo')
    icon = models.CharField(max_length=16, choices=[('gift', 'Regalo'), ('shirt', 'Prenda'), ('layers', 'Conjunto')], default='gift')
    is_active = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'pk']

    def __str__(self):
        return self.name


class SiteContent(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    hero_title = models.CharField(max_length=100, default='Tu idea merece un buen diseño.')
    hero_description = models.TextField(max_length=600, default='Prendas, regalos y piezas personalizadas. Con el criterio de Jazmin Zarate, diseñadora gráfica.')
    intro_title = models.CharField(max_length=150, default='No empieza con un objeto. Empieza contigo.')
    intro_text = models.TextField(max_length=1500, default='Soy Jazmin Zarate, diseñadora gráfica detrás de JazAr. Mi propuesta es ayudarte a transformar una idea en una pieza que tenga sentido para ti: desde cómo se ve hasta cómo se adapta al material.')
    contact_title = models.CharField(max_length=150, default='Cuéntame qué quieres crear.')
    contact_text = models.TextField(max_length=1000, default='Una idea muy clara o apenas una chispa. Comparte lo que tienes en mente y revisemos las posibilidades.')
    owner_name = models.CharField(max_length=120, default='Jazmin Zarate')
    signature = models.CharField(max_length=150, default='Diseñadora gráfica · JazAr')
    facebook_url = models.URLField(default='https://www.facebook.com/profile.php?id=100084852678555')
    hero_photo = models.ImageField(upload_to='site/', blank=True, validators=[validate_image])
    hero_alt = models.CharField(max_length=250, blank=True)
    intro_photo = models.ImageField(upload_to='site/', blank=True, validators=[validate_image])
    intro_alt = models.CharField(max_length=250, blank=True)

    class Meta:
        verbose_name_plural = 'Contenido de la portada'
        constraints = [models.CheckConstraint(condition=models.Q(id=1), name='site_content_singleton')]

    def __str__(self):
        return 'Portada JazAr'

    def clean(self):
        super().clean()
        if not self.facebook_url.startswith('https://'):
            raise ValidationError({'facebook_url': 'Usa un enlace HTTPS.'})
        for name in ['hero', 'intro']:
            if getattr(self, name + '_photo') and not getattr(self, name + '_alt').strip():
                raise ValidationError({name + '_alt': 'Describe la imagen.'})
        if self._state.adding and SiteContent.objects.exists():
            raise ValidationError('La portada ya existe. Edita el registro actual.')

    def save(self, *args, **kwargs):
        self.pk = 1
        self.clean()
        process_fields(self, ['hero_photo', 'intro_photo'])
        super().save(*args, **kwargs)
