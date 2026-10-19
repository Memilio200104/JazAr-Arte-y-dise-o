# JazAr Arte y Diseño

Sitio Django de presentacion, catalogo editable y solicitudes de contacto. Estado actualizado: 19 de octubre de 2026. El catalogo contiene 85 fichas con fotografias del cliente: 79 de precio fijo y 6 por cotizacion. El hero conserva una visualizacion conceptual identificada.

## Arranque local

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

Abrir http://127.0.0.1:8000/. Si el puerto esta ocupado, usar `python manage.py runserver 8001`. Para ejecutar sin activar el entorno: `.\.venv\Scripts\python.exe manage.py runserver`.

## Preparar otra maquina

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/setup_local.py
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py import_client_catalog --update-site --hide-demo
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

El importador conserva ediciones de productos existentes. `--update-site` reemplaza explicitamente textos y retrato de portada. Consultar [catalogo del cliente](docs/catalogo-cliente-2026.md). No usar `seed_demo` para cargar el catalogo actual; solo sirve para pruebas de conceptos.

## Administracion

El panel privado esta en `/admin/`. En esta maquina se creo `jazar_admin` sin contrasena utilizable; el propietario debe definirla en su terminal:

```powershell
python manage.py changepassword jazar_admin
```

La cuenta y su correo solo viven en SQLite local, no en Git. En otra maquina se crea una cuenta propia. Ver [edicion de contenido](docs/editar-contenido.md).

## Alcance acordado

- Contenido comercial aprobado por el usuario.
- Despliegue a cargo del usuario, una vez terminados ambos modulos.
- Gmail real se configura al final del Modulo 2. Mantener `CONTACT_LOCAL_MODE=1` durante estas pruebas: el formulario no envia correos reales y lo informa.
- Operacion reportada como probada por el usuario; no equivale a una validacion adicional del servidor realizada por Codex.
- No hay carrito, checkout, cuentas de compradores, Stripe ni webhooks. Los productos fijos permiten consultar disponibilidad hasta conectar la tienda.
- Precios visibles no activan compras. Impresion 3D y excepciones marcadas en el PDF se cotizan.
- Disenos sobre prendas negras: DTF. Los modelos multicolor indican la regla segun el color elegido.
- Modulo 2 pendiente de especificacion de variantes, pedidos, envio y pagos en pruebas. No activar cobros reales por defecto.

## Configuracion y persistencia

`config/settings.py` carga `.env`; las variables del entorno prevalecen. `.env.example` documenta las opciones, sin secretos reales. `setup_local.py` genera una clave aleatoria y no reemplaza un archivo existente.

`runtime/db.sqlite3`, `runtime/media`, cache y logs son locales y estan excluidos de Git y de la imagen Docker. Respaldar base y medios juntos. En contenedores viven en `runtime_data`; las fotos de catalogo y bundles estan en `static/`.

Gmail usa SMTP nativo de Django, sin automatizadores externos. WhatsApp y Facebook funcionan independientemente del correo.

## Errores e identidad

Paginas artisticas personalizadas para 400, 403, 404 y 500, incluida la denegacion CSRF. La pagina 500 no depende de consultas de base de datos ni muestra excepciones. Django muestra su pagina tecnica 404/500 cuando `DEBUG=1`; probar los handlers con `DEBUG=False` en tests, sin cambiar el entorno habitual.

Favicon ICO, PNG y Apple Touch Icon derivados del logo suministrado, sin redibujarlo. Las fuentes y dependencias JavaScript se sirven localmente. Animaciones GSAP con alternativa de movimiento reducido y contenido accesible sin JavaScript.

## Verificacion

```powershell
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
docker compose config --quiet
```

32 pruebas Django al cierre de esta entrega. Scripts Playwright en `scripts/check_*.cjs` requieren Node, Playwright y Chrome; las utilidades de imagen requieren sharp o Pillow segun el script. No son dependencias de ejecucion del sitio.

El motor Docker no estaba disponible para la ultima comprobacion del agente. El despliegue real, TLS y SMTP no se afirman verificados por estas pruebas locales. `check --deploy` muestra advertencias esperadas con el entorno de desarrollo.

## Documentacion y Git

- [Estado del Modulo 1](docs/modulo-1-estado.md): alcance actual y pendientes diferidos.
- [Catalogo del cliente](docs/catalogo-cliente-2026.md): precios, fuentes y responsividad.
- [Administracion](docs/editar-contenido.md): fotos, permisos y respaldos.
- [Infraestructura](docs/fase-1-infraestructura.md): referencia historica y pasos de servidor; no es estado actual.
- `AGENTS.md`: Superpowers, ui-ux-pro-max y web-design-guidelines, aplicados segun la etapa. Los antiguos plugins UI UX Designer y Web Design fueron sustituidos; no se presentan como disponibles.

Rama de trabajo: `codex/pulido-visual`. `main` y `master` conservan la base anterior; un push de la rama no despliega ni fusiona automaticamente esos cambios.
