from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import AuthAttemptBucket


class Command(BaseCommand):
    help='Elimina contadores de acceso con más de 24 horas.'

    def handle(self,*args,**options):
        count,_=AuthAttemptBucket.objects.filter(started_at__lt=timezone.now()-timedelta(hours=24)).delete()
        self.stdout.write(f'{count} contadores eliminados.')
