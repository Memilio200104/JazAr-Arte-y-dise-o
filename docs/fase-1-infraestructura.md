# JazAr: infraestructura de la primera fase

Nota de continuidad: este documento registra la base de la primera fase. El proyecto y la app ya evolucionaron a una demo funcional con catálogo en SQLite; consultar `README.md` y `docs/modulo-1-estado.md` para el arranque y estado actuales. Compose ahora incluye migraciones y un volumen runtime persistente.

## Alcance

Base tecnica para Django con Gunicorn detras de Nginx, Docker Compose,
estaticos compartidos y Certbot. El repositorio original solo contenia AGENTS.md.
Se incluye un proyecto minimo con `/healthz/`, un template base y un fragmento
optativo de animacion. La ruta `/` devuelve 404 hasta implementar el sitio.
No hay formulario, catalogo, panel administrador, base de datos ni envio de
correo implementados todavia. Las credenciales y el dominio son externos.

## Archivos y decisiones

- `Dockerfile`: dos etapas, ruedas Python en construccion, runtime sin herramientas
  de compilacion, usuario sin privilegios, Gunicorn con logs a stdout/stderr.
- `docker-compose.yml`: estaticos en tarea de una ejecucion; web saludable antes
  de arrancar Nginx; Gunicorn no publica un puerto al host; volumen de certificados
  de solo lectura para Nginx. Certbot se ejecuta bajo perfil `tls`.
- `deploy/nginx/http.conf.template`: arranque HTTP local y validacion ACME.
- `deploy/nginx/https.conf.template`: HTTP redirige a HTTPS salvo ACME; TLS1.2/1.3.
- `deploy/renew-certificates.sh`: renovacion, comprobacion y recarga Nginx.
- `config/settings.py`: DEBUG desactivado; secretos por entorno; SMTP Gmail nativo.

Versiones directas verificadas en registros PyPI/npm durante esta fase:
Django 5.2.18 (rama LTS), Gunicorn 26.2.0, GSAP 3.15.0, Lenis 1.3.26,
Three.js 0.186.1. Python usa 3.13-slim. Nginx `stable-alpine` y Certbot `latest`
son etiquetas actualizables de esta base; antes del despliegue se deben resolver
y fijar sus digests, asi como bloquear dependencias Python transitivas con hashes.
No se afirma que esta entrega sea una imagen de produccion reproducible ya auditada.

## Prueba local (PowerShell)

Con Docker Desktop iniciado en modo contenedores Linux:

```powershell
python scripts/setup_local.py
# Conserva el .env existente; revisar variables antes de usarlo en produccion.
docker compose config --quiet
docker compose up --build -d
# Solo para una demo: cargar conceptos en la base del contenedor.
docker compose exec web python manage.py seed_demo
docker compose exec nginx nginx -t
Invoke-RestMethod http://localhost:8080/healthz/
docker compose logs --tail=50 web nginx
```

El resultado de salud esperado es `{"status":"ok"}`. No es una vista del sitio.
Generar una clave con Python: `python -c "import secrets; print(secrets.token_urlsafe(64))"`.
No subir `.env`. Los secretos no se copian a la imagen. `collectstatic` se vuelve
a ejecutar al desplegar una nueva imagen; no se ejecuta desde cada worker.

## Activar HTTPS en el servidor Linux

Prerequisitos: dominio propio con DNS A/AAAA correcto, puertos publicos 80/443,
Docker Compose instalado, firewall configurado y respaldo de volumen de certificados.
Eliminar un registro AAAA incorrecto o configurar tambien la ruta IPv6. Esta base
publica en IPv4; el host/proxy debe resolver cualquier exposicion IPv6 adicional.
Sustituir `jazar.example` y `responsable@example.com` por datos reales.

1. En `.env`: `DOMAIN=jazar.example`, `HTTP_BIND=0.0.0.0`, `HTTP_PORT=80`,
   `HTTPS_PORT=443`, `DJANGO_ALLOWED_HOSTS=jazar.example,127.0.0.1`,
   `DJANGO_CSRF_TRUSTED_ORIGINS=https://jazar.example`.
   Mantener `DJANGO_HTTPS=0` y la plantilla HTTP durante la emision.
2. Arrancar y emitir:

```sh
docker compose up --build -d
docker compose --profile tls run --rm certbot certonly --webroot -w /var/www/certbot --cert-name jazar.example -d jazar.example --email responsable@example.com --agree-tos --non-interactive
```

3. Tras emision exitosa, cambiar en `.env`:
   `NGINX_TEMPLATE=./deploy/nginx/https.conf.template` y `DJANGO_HTTPS=1`.
   El nombre `DOMAIN` debe coincidir con el `--cert-name` usado arriba.

```sh
docker compose up -d --force-recreate web nginx
docker compose exec -T nginx nginx -t
docker compose exec -T web python manage.py check --deploy
docker compose --profile tls run --rm certbot renew --dry-run
```

4. Verificar `https://jazar.example/healthz/`. Activar HSTS gradualmente con
   `DJANGO_HSTS_SECONDS=3600` tras verificar HTTPS; ampliar a 31536000 cuando
   el dominio este estable. No se habilitan preload ni subdominios automaticamente.
5. Programar en cron del host, dos veces al dia (ruta absoluta real):

```cron
17 3,15 * * * /bin/sh /srv/jazar/deploy/renew-certificates.sh >> /var/log/jazar-certbot.log 2>&1
```

La renovacion debe ejecutarse desde el usuario del despliegue con acceso a Docker.
El script usa el mismo proyecto Compose `jazar`. Recarga Nginx despues de una
renovacion exitosa (tambien si no habia nada que renovar) para cargar certificados.
No monta el socket Docker en Certbot. Configurar rotacion de logs y alertas de fallo
en el host. Certbot no renueva solo por aparecer en Compose: requiere este cron.

Si la emision falla, mantener HTTP y consultar DNS/ACME antes de seleccionar TLS;
Nginx no puede iniciar la plantilla HTTPS sin certificados existentes.

## Gmail nativo

Configurar `EMAIL_HOST_USER` con la cuenta Gmail, `EMAIL_HOST_PASSWORD` con una
contrasena de aplicacion permitida por la cuenta y `CONTACT_EMAIL` con el destino.
Google requiere verificacion en dos pasos para las contrasenas de aplicacion y
puede no ofrecerlas en cuentas administradas o con ciertas politicas. No usar la
contrasena habitual. SMTP: `smtp.gmail.com:587`, STARTTLS, tiempo limite 10s.

En la segunda fase, el formulario usara `django.core.mail.EmailMessage`, remitente
igual a `EMAIL_HOST_USER` y correo del visitante en `reply_to`; nunca en `from_email`.
Implementar Django Form, CSRF, limites de longitud, honeypot/limitacion de frecuencia,
mensaje de exito solo despues del envio y error recuperable sin perder lo escrito.
No n8n ni automatizadores externos. Gmail tiene cuotas: validar entrega real antes
de publicacion. No se ha enviado ningun correo en esta fase.

## Templates y animacion

`templates/base.html` define bloques sin cargar librerias globalmente. Solo una
pagina que las necesite incluira el fragmento:

```django
{% extends "base.html" %}
{% block motion %}{% include "includes/motion.html" %}{% endblock %}
```

| Libreria | Papel | Carga y limites |
| --- | --- | --- |
| GSAP + ScrollTrigger | Timelines, scrub, pin, parallax y matchMedia | `defer`, solo paginas animadas; transforms y opacity preferidos |
| Lenis | Suavizado coordinado con GSAP | Solo se instancia a partir de 1024px, puntero fino y sin movimiento reducido; un solo ticker |
| Three.js | Escena futura de un producto real, GLTFLoader si hay GLB | No se carga ni instancia en esta fase; import dinamico al acercarse escena al viewport, con imagen de respaldo |

El fragmento usa URLs CDN con versiones exactas para revision de fase 1. Antes de
publicar, alojar bundles versionados en static con npm/lockfile y un bundler;
aplicar CSP segun origen definitivo. Three.js debe instalarse como `three@0.186.1`
para ese build e importarse con `import('three')` dentro de la escena aprobada.
No requiere React. No usar simultaneamente Lenis y ScrollSmoother.

Los valores de pin/parallax del storyboard se implementaran mediante
`gsap.matchMedia()`, incluyendo cambio en vivo de preferencias y limpieza al
desmontar. Movimiento reducido: orden natural, sin pin, scrub ni suavizado;
todo texto/producto permanece visible sin JS. En movil se mantiene scroll nativo,
se eliminan pins largos y se simplifica profundidad. No cargar canvas vacio.
Validar tactil, teclado, focus, anchors y rendimiento con activos reales.

## Verificacion y pendientes

- Compose validado con `docker compose --env-file .env.example config --no-env-resolution --quiet`, sin crear un archivo de secretos. Esto valida estructura e interpolacion; no la disponibilidad del servicio Docker ni credenciales reales.
- Dependencias instaladas en `.venv`; `manage.py check` finalizo sin incidencias.
- Cliente de pruebas Django: `/healthz/` devuelve HTTP 200 y `{"status":"ok"}`; renderizados `base.html` e `includes/motion.html` correctamente.
- Sintaxis Python validada en cinco archivos mediante `ast.parse`.
- Sintaxis de `static/js/motion.js` validada mediante Node.
- Docker CLI existe, pero el daemon Linux de Docker Desktop no estaba disponible:
  build, `nginx -t` real y prueba del conjunto de contenedores pendientes.
- Certificado real y Gmail requieren dominio/cuenta; no se simula su verificacion.
- Base Django sin persistencia deliberadamente: si se agregan pedidos/admin,
  definir PostgreSQL y copias de seguridad antes de implementar esos flujos.

## Referencias oficiales

- [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Django email](https://docs.djangoproject.com/en/5.2/topics/email/)
- [Docker Compose startup order](https://docs.docker.com/compose/how-tos/startup-order/)
- [Certbot webroot y renovacion](https://eff-certbot.readthedocs.io/en/stable/using.html)
- [Contrasenas de aplicacion Google](https://support.google.com/accounts/answer/185833)
- [GSAP installation](https://gsap.com/docs/v3/Installation/)
- [Lenis e integracion GSAP](https://github.com/darkroomengineering/lenis)
- [Three.js installation](https://threejs.org/manual/en/installation.html)
