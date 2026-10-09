# JazAr Arte y Diseño

Demo del Módulo 1: Django sirve presentación, catálogo y solicitudes de cotización. La identidad parte de la captura de Facebook aportada por el usuario. Las imágenes actuales son visualizaciones conceptuales, no fotografías de trabajos reales.

## Arranque local en PowerShell

El entorno `.venv`, el `.env` local y la base SQLite ya están preparados en esta máquina. Desde la raíz del proyecto:

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

Abrir [la demo local](http://127.0.0.1:8000/). Django recarga Python y templates al guardar; recargar el navegador para CSS/JS. Si PowerShell bloquea la activación, no es necesario cambiar su política: ejecutar directamente `.\.venv\Scripts\python.exe manage.py runserver`.

La demo puede estar ya ejecutándose en el puerto 8000. Para una segunda instancia usar `python manage.py runserver 8001` y abrir `http://127.0.0.1:8001/`. El origen de mismo host funciona con CSRF; no requiere modificar credenciales.

## Preparar otra máquina

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/setup_local.py
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver
```

`setup_local.py` crea una clave aleatoria y el directorio de datos; no reemplaza un `.env` existente. `seed_demo` crea seis conceptos, sin modificar registros existentes ni inventar precio o inventario. Las fuentes, imágenes y dependencias JS se sirven localmente: no se necesita Node ni un CDN para mostrar la demo.

## Configuración

`config/settings.py` carga `.env` automáticamente con python-dotenv. Las variables ya presentes en el entorno prevalecen sobre el archivo.

| Variable | Demo local | Producción |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Aleatoria, ya generada | Secreto propio del servidor |
| `DJANGO_DEBUG` | `1` | `0` |
| `DJANGO_ALLOWED_HOSTS` | localhost, 127.0.0.1, IPv6 local | Dominio real |
| `DJANGO_HTTPS` | `0` | `1` después de emitir TLS |
| `CONTACT_LOCAL_MODE` | `1`: correo en consola, aviso de demo visible | `0`: SMTP Gmail |
| `CONTACT_TRUST_PROXY` | `0` con runserver | `1` solo detrás del Nginx configurado |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `CONTACT_EMAIL` | Vacías; no se requieren para demo | Cuenta Gmail, contraseña de aplicación y destino reales |

La demo no envía correos externos. El formulario valida datos, CSRF, honeypot y límite de solicitudes compartido entre procesos. Fallos SMTP conservan los valores y nunca se presentan como éxito. Antes de publicar se requiere configurar Gmail, probar recepción y confirmar aviso de privacidad y contenido comercial. `.env`, SQLite y logs se excluyen de Git y de la imagen Docker.

## Estructura

- `config/`: proyecto Django, configuración, rutas y WSGI/ASGI.
- `website/`: aplicación, modelo `Product`, formularios, vistas, datos conceptuales y pruebas.
- `templates/`: página de cinco secciones y base.
- `static/`: estilos, GSAP/ScrollTrigger, iconos Lucide, fuentes y conceptos visuales.
- `runtime/`: SQLite, limitación de solicitudes y logs locales, fuera de control de versiones.
- `deploy/`: Nginx, HTTPS y renovación Certbot. Consultar `docs/fase-1-infraestructura.md`.

## Alcance y Módulo 2

`Product` tiene SKU único, precio decimal nullable, moneda MXN, stock nullable, slug, categoría, técnica, imagen, publicación y fechas. `null` significa que el dato comercial aún no está definido; no equivale a precio cero ni existencia cero. Los campos se validan, pero no se realizan compras ni movimientos de inventario.

La navegación reserva dos espacios de 44 px para futuros accesos. Están vacíos y fuera del árbol accesible: no hay botones ficticios, rutas de carrito, login de clientes, checkout, Stripe ni webhooks. Las aplicaciones de autenticación que trae Django permanecen como infraestructura estándar, sin rutas expuestas ni flujos de acceso. SQLite permite revisar este módulo; antes del módulo transaccional se deberá planificar PostgreSQL y el diseño de variantes/pedidos/pagos por separado.

## Verificación

```powershell
python manage.py check
python manage.py test website
python manage.py makemigrations --check --dry-run
docker compose config --quiet
```

Las comprobaciones de navegador están en `scripts/check_browser.cjs`; requieren Playwright y Chrome. Revisan recursos, filtros, preselección, menú, anchos 320/390/768/1024/1440 px, movimiento reducido, formulario local y contenido sin JavaScript. Capturas en `artifacts/` (ignorado).

## Flujo obligatorio

Superpowers, UI UX Designer, Web Design y web-design-guidelines son obligatorios según `AGENTS.md`. El plan de trabajo y las decisiones están en `docs/`; no se requiere instalar de nuevo los complementos que ya están disponibles en la sesión.

## Versiones y continuidad

Repositorio: https://github.com/Memilio200104/JazAr-Arte-y-dise-o

`main` y `master` conservan la demo base (`2689de8`). `codex/pulido-visual` contiene la identidad original, las imágenes conceptuales por producto y el proceso animado. Cambiar de rama afecta al mismo runserver; detenerlo antes de cambiar y arrancarlo de nuevo después.

GitHub respalda el código: no hospeda Django ni traslada esta conversación a un ejecutor cloud. No hay una automatización de reanudación configurada. El estado de entrega y los pendientes están en `docs/pulido-visual.md`.
