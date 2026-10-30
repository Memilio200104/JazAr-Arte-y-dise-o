from django.conf import settings
from django.db import models


class CustomerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_profile')
    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254, unique=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    default_address = models.ForeignKey('ShippingAddress', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    def __str__(self):
        return self.full_name


class ShippingAddress(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='addresses')
    recipient = models.CharField(max_length=150)
    phone = models.CharField(max_length=32)
    street = models.CharField(max_length=150)
    exterior = models.CharField(max_length=20)
    interior = models.CharField(max_length=20, blank=True)
    district = models.CharField(max_length=100)
    postcode = models.CharField(max_length=5)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    reference = models.CharField(max_length=300, blank=True)
    label = models.CharField(max_length=40, blank=True)

    class Meta:
        ordering = ['pk']


class AuthAttemptBucket(models.Model):
    key = models.CharField(max_length=64, unique=True)
    started_at = models.DateTimeField()
    count = models.PositiveIntegerField(default=0)
