from uuid import uuid4
from django.db import models

ACTIVE = ('creating', 'open', 'reconciliation_required')


class PaymentAttempt(models.Model):
    public_id = models.UUIDField(default=uuid4, unique=True, editable=False)
    order = models.ForeignKey('orders.Order', on_delete=models.PROTECT, related_name='payment_attempts')
    quote = models.ForeignKey('shipping.ShippingQuote', on_delete=models.PROTECT)
    approved_version = models.PositiveIntegerField()
    total_minor = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, default='MXN')
    state = models.CharField(max_length=24, default='creating', choices=[
        ('creating','Preparando pago'),('open','Pago pendiente'),('paid','Pago confirmado'),
        ('expired','Sesion vencida'),('failed','Pago no completado'),('reconciliation_required','Verificando pago')])
    session_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    paid_at = models.DateTimeField(null=True, blank=True, editable=False)
    payment_intent_id = models.CharField(max_length=255, blank=True, editable=False)
    charge_id = models.CharField(max_length=255, blank=True, editable=False)
    checkout_url = models.URLField(max_length=2048, blank=True)
    payload = models.JSONField(default=dict)
    creation_requests = models.PositiveIntegerField(default=0, editable=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [('reconcile_payment','Puede conciliar pagos y expirar sesiones')]
        constraints = [models.UniqueConstraint(fields=['order'], condition=models.Q(state__in=ACTIVE), name='payment_one_active'),
            models.UniqueConstraint(fields=['order'], condition=models.Q(state='paid'), name='payment_one_paid')]

    def __str__(self):
        return str(self.public_id)


class StockReservation(models.Model):
    attempt = models.ForeignKey(PaymentAttempt, on_delete=models.PROTECT, related_name='reservations')
    product = models.ForeignKey('website.Product', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    state = models.CharField(max_length=10, default='held')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['attempt','product'],name='payment_reservation_unique'),
            models.CheckConstraint(condition=models.Q(quantity__gt=0), name='payment_reservation_positive')]


class ProviderEvent(models.Model):
    event_id = models.CharField(max_length=255, unique=True)
    attempt = models.ForeignKey(PaymentAttempt, on_delete=models.PROTECT)
    processed_at = models.DateTimeField()


class Refund(models.Model):
    public_id = models.UUIDField(default=uuid4, unique=True, editable=False)
    attempt = models.OneToOneField(PaymentAttempt, on_delete=models.PROTECT, related_name='refund')
    amount_minor = models.PositiveIntegerField()
    state = models.CharField(max_length=16, default='requested', choices=[
        ('requested', 'Cancelación solicitada'), ('pending', 'Reembolso en proceso'),
        ('succeeded', 'Reembolso confirmado'), ('failed', 'Reembolso requiere revisión'),
        ('canceled', 'Reembolso requiere revisión')])
    provider_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'cancelación y reembolso'
        verbose_name_plural = 'cancelaciones y reembolsos'
        permissions = [('reconcile_refund', 'Puede conciliar reembolsos')]
        constraints = [models.CheckConstraint(condition=models.Q(amount_minor__gt=0, amount_minor__lt=200000), name='refund_policy_amount')]

    def __str__(self):
        return str(self.public_id)
