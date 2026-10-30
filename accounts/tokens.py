from django.core import signing
from django.utils import timezone
from .models import CustomerProfile

SALT='jazar.customer.verify.v1'


def make_verification_token(profile):
    return signing.dumps({'pk':profile.pk,'email':profile.email},salt=SALT)


def verify_email(token):
    try:
        data=signing.loads(token,salt=SALT,max_age=86400)
    except signing.BadSignature:
        return False
    return bool(CustomerProfile.objects.filter(pk=data['pk'],email=data['email'],email_verified_at__isnull=True,user__is_active=True).update(email_verified_at=timezone.now()))
