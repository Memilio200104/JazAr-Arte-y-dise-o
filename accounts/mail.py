from smtplib import SMTPException
from urllib.parse import urlsplit
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.urls import reverse
from .tokens import make_verification_token


def account_origin():
    origin=settings.ACCOUNT_ORIGIN.rstrip('/')
    parts=urlsplit(origin)
    if not parts.netloc or parts.path or parts.query or parts.fragment or parts.username or parts.password:
        raise ImproperlyConfigured('Configura ACCOUNT_ORIGIN con un origen válido.')
    if parts.scheme != 'https' and not (settings.DEBUG and parts.scheme=='http' and parts.hostname in ['localhost','127.0.0.1','testserver']):
        raise ImproperlyConfigured('ACCOUNT_ORIGIN requiere HTTPS fuera de desarrollo.')
    return origin


def send_verification(profile):
    try:
        url=account_origin()+reverse('verify_email',args=[make_verification_token(profile)])
        return EmailMessage('Confirma tu correo en JazAr',f'Confirma tu correo para preparar tus próximas piezas.\n\n{url}\n\nEl enlace vence en 24 horas. Si no creaste esta cuenta, ignora este mensaje.',settings.DEFAULT_FROM_EMAIL,[profile.email]).send()==1
    except (SMTPException,OSError,ValueError,ImproperlyConfigured):
        return False
