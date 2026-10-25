from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class ValidatedPacking(models.Model):
    validated_at = models.DateTimeField(null=True, blank=True, editable=False)
    validated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
        editable=False, on_delete=models.SET_NULL, related_name='+')
    operational_fields = ()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.pk:
            old = type(self).objects.filter(pk=self.pk).values(*self.operational_fields).first()
            if old and any(old[field] != getattr(self, field) for field in self.operational_fields):
                self.validated_at = self.validated_by = None
                if kwargs.get('update_fields'):
                    kwargs['update_fields'] = set(kwargs['update_fields']) | {'validated_at', 'validated_by'}
        super().save(*args, **kwargs)


class PackageProfile(ValidatedPacking):
    code = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    length_cm = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(Decimal('.01'))])
    width_cm = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(Decimal('.01'))])
    height_cm = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(Decimal('.01'))])
    tare_kg = models.DecimalField(max_digits=7, decimal_places=3, validators=[MinValueValidator(Decimal('.001'))])
    max_weight_kg = models.DecimalField(max_digits=7, decimal_places=3, validators=[MinValueValidator(Decimal('.001'))])
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    active = models.BooleanField(default=True)
    operational_fields = ('length_cm', 'width_cm', 'height_cm', 'tare_kg', 'max_weight_kg', 'capacity', 'active')

    class Meta:
        verbose_name = 'perfil de caja'
        verbose_name_plural = 'perfiles de caja'
        constraints = [models.CheckConstraint(condition=models.Q(length_cm__gt=0, width_cm__gt=0,
            height_cm__gt=0, tare_kg__gt=0, max_weight_kg__gt=models.F('tare_kg'), capacity__gt=0),
            name='shipping_profile_positive')]

    def clean(self):
        if self.max_weight_kg is not None and self.tare_kg is not None and self.max_weight_kg <= self.tare_kg:
            raise ValidationError({'max_weight_kg': 'El peso maximo debe superar el peso de la caja vacia.'})

    def __str__(self):
        return self.name


class ProductPacking(ValidatedPacking):
    product = models.OneToOneField('website.Product', on_delete=models.CASCADE, related_name='packing')
    profile = models.ForeignKey(PackageProfile, on_delete=models.PROTECT)
    protected_unit_weight_kg = models.DecimalField(max_digits=7, decimal_places=3, validators=[MinValueValidator(Decimal('.001'))])
    capacity_units = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    operational_fields = ('profile_id', 'protected_unit_weight_kg', 'capacity_units')

    class Meta:
        verbose_name = 'empaque de producto'
        verbose_name_plural = 'empaques de productos'
        constraints = [models.CheckConstraint(condition=models.Q(protected_unit_weight_kg__gt=0,
            capacity_units__gt=0), name='shipping_product_packing_positive')]

    def __str__(self):
        return str(self.product)


class ShippingQuote(models.Model):
    order = models.ForeignKey('orders.Order', on_delete=models.PROTECT, related_name='shipping_quotes')
    customer = models.ForeignKey('accounts.CustomerProfile', on_delete=models.PROTECT)
    fingerprint = models.CharField(max_length=64)
    snapshot = models.JSONField()
    carrier = models.CharField(max_length=80)
    service = models.CharField(max_length=80)
    amount_minor = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, default='MXN')
    provider_reference = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    @property
    def amount(self):
        return Decimal(self.amount_minor) / 100


class ShippingRateBucket(models.Model):
    customer = models.OneToOneField('accounts.CustomerProfile', on_delete=models.CASCADE)
    started_at = models.DateTimeField()
    count = models.PositiveIntegerField(default=0)
