from urllib.parse import urlsplit
import stripe
from django.conf import settings
from django.core.exceptions import ValidationError


class PaymentUnavailable(ValidationError):
    def __init__(self):
        super().__init__('No pudimos conectar con el servicio de pago. Puedes volver a intentarlo.')


class PaymentRejected(PaymentUnavailable):
    pass


def ensure_configured():
    key = settings.STRIPE_SECRET_KEY
    origin = urlsplit(settings.PAYMENT_ORIGIN)
    if (not key.startswith('sk_test_') or not origin.hostname or origin.username or origin.password
            or origin.query or origin.fragment or origin.path not in ('', '/')
            or (origin.scheme != 'https' and not (origin.scheme == 'http' and origin.hostname in ('localhost','127.0.0.1')))):
        raise PaymentUnavailable()


def _client():
    ensure_configured()
    return stripe.StripeClient(settings.STRIPE_SECRET_KEY, stripe_version='2026-09-30.endive',
        max_network_retries=1, http_client=stripe.RequestsClient(timeout=10))


def create_session(attempt):
    try:
        return _client().v1.checkout.sessions.create(attempt.payload,
            options={'idempotency_key': str(attempt.public_id)}).to_dict()
    except stripe.InvalidRequestError as exc:
        if exc.http_status == 400:
            raise PaymentRejected() from None
        raise PaymentUnavailable() from None
    except (stripe.AuthenticationError, stripe.PermissionError):
        raise PaymentRejected() from None
    except stripe.StripeError:
        # Even a provider error may have occurred after accepting the request.
        raise PaymentUnavailable() from None


def retrieve_session(session_id):
    try:
        return _client().v1.checkout.sessions.retrieve(session_id).to_dict()
    except stripe.StripeError:
        raise PaymentUnavailable() from None


def expire_session(session_id):
    try:
        return _client().v1.checkout.sessions.expire(session_id).to_dict()
    except stripe.StripeError:
        # A payment can win the race against expiry. Read canonical state.
        return retrieve_session(session_id)
