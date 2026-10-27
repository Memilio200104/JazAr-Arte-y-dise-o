import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = os.getenv("DJANGO_DEBUG", "0") == "1"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
if "127.0.0.1" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("127.0.0.1")
CSRF_TRUSTED_ORIGINS = [
    origin for origin in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if origin
]
ROOT_URLCONF = "config.urls"
CSRF_FAILURE_VIEW = 'website.errors.csrf_failure'
WSGI_APPLICATION = "config.wsgi.application"
INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "website.apps.WebsiteConfig",
    "accounts.apps.AccountsConfig",
    "orders.apps.OrdersConfig",
    "shipping.apps.ShippingConfig",
    "payments.apps.PaymentsConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "runtime" / "db.sqlite3"}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_ROOT = BASE_DIR / 'runtime' / 'media'
MEDIA_URL = '/media/'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.' + name}
    for name in ['UserAttributeSimilarityValidator', 'MinimumLengthValidator',
                 'CommonPasswordValidator', 'NumericPasswordValidator']
]
AUTHENTICATION_BACKENDS = ['accounts.backends.CustomerEmailBackend', 'django.contrib.auth.backends.ModelBackend']
LOGIN_URL = '/cuenta/ingresar/'
PASSWORD_RESET_TIMEOUT = 86400
ACCOUNT_ORIGIN = os.getenv('ACCOUNT_ORIGIN', 'http://127.0.0.1:8000' if DEBUG else '')
if os.getenv("CONTACT_TRUST_PROXY", "0") == "1":
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = os.getenv("DJANGO_HTTPS", "0") == "1"
SECURE_REDIRECT_EXEMPT = [r"^healthz/$"]
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT
SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
CONTACT_LOCAL_MODE = os.getenv("CONTACT_LOCAL_MODE", "0") == "1"
EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend" if CONTACT_LOCAL_MODE
    else "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 10
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER or ("local@localhost" if CONTACT_LOCAL_MODE else "")
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "") or DEFAULT_FROM_EMAIL
CONTACT_TRUST_PROXY = os.getenv("CONTACT_TRUST_PROXY", "0") == "1"
CONTACT_RATE_LIMIT = 5
CONTACT_RATE_WINDOW = 600
CONTACT_CACHE_DIR = BASE_DIR / "runtime" / "cache"
ENVIA_TOKEN = os.getenv('ENVIA_TOKEN', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
PAYMENT_ORIGIN = os.getenv('PAYMENT_ORIGIN', ACCOUNT_ORIGIN)
ENVIA_CARRIERS = [value.strip() for value in os.getenv('ENVIA_CARRIERS', 'dhl,fedex,estafeta').split(',') if value.strip()]
SHIPPING_ORIGIN = {
    'name': os.getenv('SHIPPING_ORIGIN_NAME', 'JazAr Arte y Diseno'),
    'phone': os.getenv('SHIPPING_ORIGIN_PHONE', '5539754777'),
    'street': os.getenv('SHIPPING_ORIGIN_STREET', '2a Privada de Aconitos'),
    'number': os.getenv('SHIPPING_ORIGIN_NUMBER', '729'),
    'district': os.getenv('SHIPPING_ORIGIN_DISTRICT', 'Villa de las Flores'),
    'city': os.getenv('SHIPPING_ORIGIN_CITY', 'Coacalco'),
    'state': os.getenv('SHIPPING_ORIGIN_STATE', 'EM'),
    'country': 'MX', 'postalCode': os.getenv('SHIPPING_ORIGIN_POSTCODE', '55710'),
    'reference': os.getenv('SHIPPING_ORIGIN_REFERENCE', 'Manzana K7 lote 16'),
}
DATA_UPLOAD_MAX_MEMORY_SIZE = 32768
