from uuid import uuid4
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from .models import CustomerProfile, ShippingAddress


def normalize_email(value):
    return value.strip().lower()


def register_customer(full_name, email, password):
    email = normalize_email(email)
    validate_email(email)
    name = full_name.strip()
    if not name or len(name) > 150 or len(email) > 254:
        raise ValidationError('Revisa el nombre y el correo.')
    User = get_user_model()
    user = User(username=uuid4().hex, email=email, first_name=name)
    password_validation.validate_password(password, user)
    try:
        with transaction.atomic():
            if User.objects.filter(email__iexact=email).exists():
                raise ValidationError('No pudimos crear la cuenta con estos datos. Intenta ingresar o recuperar tu acceso.')
            user.set_password(password)
            user.save()
            return CustomerProfile.objects.create(user=user, email=email, full_name=name)
    except IntegrityError:
        raise ValidationError('No pudimos crear la cuenta con estos datos. Intenta ingresar o recuperar tu acceso.') from None


@transaction.atomic
def save_address(customer, cleaned_data, address_id=None):
    # Serializes default-address decisions on databases supporting row locks.
    customer = CustomerProfile.objects.select_for_update().get(pk=customer.pk)
    address = get_object_or_404(ShippingAddress, customer=customer, pk=address_id) if address_id else ShippingAddress(customer=customer)
    fields = ['recipient','phone','street','exterior','interior','district','postcode','city','state','reference','label']
    for field in fields:
        setattr(address, field, cleaned_data.get(field, '').strip())
    address.full_clean()
    address.save()
    if customer.default_address_id is None:
        customer.default_address = address
        customer.save(update_fields=['default_address'])
    return address


@transaction.atomic
def set_default_address(customer, address_id):
    customer = CustomerProfile.objects.select_for_update().get(pk=customer.pk)
    customer.default_address = get_object_or_404(ShippingAddress, customer=customer, pk=address_id)
    customer.save(update_fields=['default_address'])


@transaction.atomic
def delete_address(customer, address_id):
    customer = CustomerProfile.objects.select_for_update().get(pk=customer.pk)
    address = get_object_or_404(ShippingAddress, customer=customer, pk=address_id)
    was_default = customer.default_address_id == address.pk
    address.delete()
    if was_default:
        customer.default_address = customer.addresses.first()
        customer.save(update_fields=['default_address'])
