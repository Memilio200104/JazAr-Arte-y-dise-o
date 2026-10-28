"""Isolated browser-test server; never loads the working catalog database."""
from .settings import *

DATABASES = {'default': {'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR / 'runtime' / 'accounts-browser.sqlite3'}}
DEBUG = True
ACCOUNT_ORIGIN = 'http://127.0.0.1:8011'
CONTACT_LOCAL_MODE = True
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
ALLOWED_HOSTS = ['127.0.0.1','localhost']
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
# Browser fixtures must stay isolated even after local provider keys are configured.
ENVIA_TOKEN = ''
STRIPE_SECRET_KEY = ''
STRIPE_WEBHOOK_SECRET = ''
