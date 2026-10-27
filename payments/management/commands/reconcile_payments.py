from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.utils import timezone
from payments.models import PaymentAttempt, ACTIVE
from payments.services import reconcile_attempt


class Command(BaseCommand):
    help = 'Consulta pagos pendientes y libera reservas solo al confirmar expiracion en Stripe.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=100)

    def handle(self, *args, **options):
        attempts=PaymentAttempt.objects.filter(state__in=ACTIVE).order_by('updated_at')[:max(1,min(options['limit'],100))]
        for attempt in attempts:
            try:
                result=reconcile_attempt(attempt.pk,expire=attempt.expires_at<=timezone.now())
                self.stdout.write(f'{attempt.public_id}: {result.state}')
            except (ValidationError,DatabaseError):
                self.stderr.write(f'{attempt.public_id}: pendiente de conciliacion')
