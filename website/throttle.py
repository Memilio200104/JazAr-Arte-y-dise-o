import hashlib
import hmac
import os
import threading
import time
from pathlib import Path

from django.conf import settings
from django.core.cache.backends.filebased import FileBasedCache


_thread_lock = threading.Lock()


def allow_contact(address):
    directory = Path(settings.CONTACT_CACHE_DIR).resolve()
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    cache = FileBasedCache(str(directory), {"TIMEOUT": settings.CONTACT_RATE_WINDOW})
    key = hmac.new(settings.SECRET_KEY.encode(), address.encode(), hashlib.sha256).hexdigest()
    # FileBasedCache alone cannot atomically increment across Gunicorn workers.
    with _thread_lock, (directory / "contact.lock").open("a+b") as lock:
        lock.seek(0)
        if os.name == "nt":
            import msvcrt
            if not lock.read(1):
                lock.write(b"0")
                lock.flush()
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            now = time.time()
            attempts = [stamp for stamp in cache.get(key, []) if stamp > now - settings.CONTACT_RATE_WINDOW]
            if len(attempts) >= settings.CONTACT_RATE_LIMIT:
                return False
            cache.set(key, attempts + [now])
            return True
        finally:
            if os.name == "nt":
                lock.seek(0)
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
