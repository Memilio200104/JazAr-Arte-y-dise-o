"""Generate local development settings without displaying or replacing secrets."""
import secrets
from pathlib import Path

from dotenv import set_key

root = Path(__file__).resolve().parent.parent
env = root / ".env"
(root / "runtime").mkdir(exist_ok=True)
if env.exists():
    print(".env ya existe; se conserva sin cambios.")
else:
    values = {
        "DJANGO_SECRET_KEY": secrets.token_urlsafe(64),
        "DJANGO_DEBUG": "1",
        "DJANGO_ALLOWED_HOSTS": "localhost,127.0.0.1,[::1]",
        "DJANGO_CSRF_TRUSTED_ORIGINS": "http://localhost:8000,http://127.0.0.1:8000,http://localhost:8080",
        "DJANGO_HTTPS": "0", "DJANGO_HSTS_SECONDS": "0",
        "CONTACT_LOCAL_MODE": "1", "CONTACT_TRUST_PROXY": "0",
        "EMAIL_HOST_USER": "", "EMAIL_HOST_PASSWORD": "", "CONTACT_EMAIL": "",
        "HTTP_BIND": "127.0.0.1", "HTTP_PORT": "8080", "HTTPS_PORT": "8443",
        "DOMAIN": "localhost", "NGINX_TEMPLATE": "./deploy/nginx/http.conf.template",
    }
    for key, value in values.items():
        set_key(str(env), key, value)
    print(".env local creado con una clave aleatoria. Correo en modo demo local.")
