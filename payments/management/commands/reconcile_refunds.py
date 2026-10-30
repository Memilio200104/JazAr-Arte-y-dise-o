from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from payments.models import Refund
from payments.refunds import reconcile_refund


class Command(BaseCommand):
    help = 'Concilia devoluciones y posibles rechazos bancarios posteriores sin duplicarlas.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=100)

    def handle(self, *args, **options):
        refunds = Refund.objects.filter(state__in=('requested', 'pending', 'succeeded')).order_by('updated_at')[:max(1, min(options['limit'], 100))]
        for refund in refunds:
            try:
                result = reconcile_refund(refund.pk)
                self.stdout.write(f'{result.public_id}: {result.state}')
            except (ValidationError, DatabaseError):
                self.stderr.write(f'{refund.public_id}: necesita revisión; solicitud conservada')
