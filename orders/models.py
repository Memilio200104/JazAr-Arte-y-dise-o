from uuid import uuid4
from django.conf import settings
from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'En revisión'
        CHANGES = 'changes', 'Cambios solicitados'
        APPROVED = 'approved', 'Diseño aprobado'

    public_id = models.UUIDField(default=uuid4, unique=True, editable=False)
    customer = models.ForeignKey('accounts.CustomerProfile', on_delete=models.PROTECT, related_name='orders')
    currency = models.CharField(max_length=3, default='MXN')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_address = models.JSONField()
    notes = models.TextField(max_length=1500, blank=True)
    review_status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_orders')
    approved_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(max_length=1500, blank=True)
    version = models.PositiveIntegerField(default=0)
    idempotency_key = models.UUIDField()
    request_digest = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-pk']
        permissions = [('approve_order', 'Puede aprobar diseños de pedidos')]
        constraints = [models.UniqueConstraint(fields=['customer','idempotency_key'],name='order_customer_request_unique'),
                       models.CheckConstraint(condition=models.Q(subtotal__gte=0),name='order_subtotal_nonnegative')]

    def __str__(self):
        return str(self.public_id)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('website.Product', on_delete=models.PROTECT)
    sku = models.CharField(max_length=64)
    name = models.CharField(max_length=160)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()
    details = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ['pk']
        constraints = [models.UniqueConstraint(fields=['order','product'],name='order_product_unique'),
                       models.CheckConstraint(condition=models.Q(quantity__gte=1),name='order_quantity_positive'),
                       models.CheckConstraint(condition=models.Q(unit_price__gte=0),name='order_price_nonnegative')]

    @property
    def total(self):
        return self.quantity * self.unit_price


class OrderReviewEvent(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='review_events')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    from_status = models.CharField(max_length=10)
    to_status = models.CharField(max_length=10)
    note = models.TextField(max_length=1500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at','pk']


class OrderCreationBucket(models.Model):
    customer = models.OneToOneField('accounts.CustomerProfile', on_delete=models.CASCADE)
    started_at = models.DateTimeField()
    count = models.PositiveIntegerField(default=0)
