import hashlib
import hmac
import math
from datetime import timedelta
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from .models import AuthAttemptBucket
from .services import normalize_email

WINDOW = 900
LIMITS = {'login':(30,10), 'register':(5,None), 'recovery':(10,3), 'verify':(10,3)}


def consume_limits(action, ip, email=''):
    now=timezone.now()
    specs=[('ip',ip,LIMITS[action][0])]
    if LIMITS[action][1] is not None:
        specs.append(('email',normalize_email(email),LIMITS[action][1]))
    allowed, retry = True, 0
    with transaction.atomic():
        for kind, value, limit in specs:
            key=hmac.new(settings.SECRET_KEY.encode(),f'{action}:{kind}:{value}'.encode(),hashlib.sha256).hexdigest()
            bucket,_=AuthAttemptBucket.objects.get_or_create(key=key,defaults={'started_at':now})
            AuthAttemptBucket.objects.filter(pk=bucket.pk,started_at__lte=now-timedelta(seconds=WINDOW)).update(started_at=now,count=0)
            updated=AuthAttemptBucket.objects.filter(pk=bucket.pk,count__lt=limit).update(count=F('count')+1)
            if not updated:
                bucket.refresh_from_db()
                allowed=False
                retry=max(retry,max(1,math.ceil(WINDOW-(now-bucket.started_at).total_seconds())))
    return allowed,retry
