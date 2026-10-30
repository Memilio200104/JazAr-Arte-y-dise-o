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
        return _client().v1.checkout.sessions.retrieve(session_id,
            params={'expand': ['payment_intent.latest_charge']}).to_dict()
    except stripe.StripeError:
        raise PaymentUnavailable() from None


def expire_session(session_id):
    try:
        return _client().v1.checkout.sessions.expire(session_id).to_dict()
    except stripe.StripeError:
        # A payment can win the race against expiry. Read canonical state.
        return retrieve_session(session_id)


def create_refund(refund):
    try:
        return _client().v1.refunds.create({
            'charge': refund.attempt.charge_id, 'amount': refund.amount_minor,
            'reason': 'requested_by_customer', 'metadata': {'cancellation': str(refund.public_id)},
        }, options={'idempotency_key': 'cancel-' + str(refund.public_id)}).to_dict()
    except stripe.StripeError:
        # Keep the request: a timeout is not proof that Stripe rejected it.
        raise PaymentUnavailable() from None


def retrieve_refund(provider_id):
    try:
        return _client().v1.refunds.retrieve(provider_id).to_dict()
    except stripe.StripeError:
        raise PaymentUnavailable() from None


def find_refund(refund):
    """Recover acceptance even after Stripe's idempotency retention window."""
    try:
        results = _client().v1.refunds.list({'charge': refund.attempt.charge_id, 'limit': 100})
        for item in results.auto_paging_iter():
            if item.metadata.get('cancellation') == str(refund.public_id):
                return item.to_dict()
        return None
    except stripe.StripeError:
        raise PaymentUnavailable() from None
