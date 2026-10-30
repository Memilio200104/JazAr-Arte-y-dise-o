# JazAr Arte y Diseño

Sitio Django de presentacion, catalogo editable y frontend de tienda. Estado actualizado: 20 de octubre de 2026. El catalogo contiene 85 fichas con fotografias del cliente: 79 de precio fijo y 6 por cotizacion. El hero conserva el fondo original por peticion expresa del usuario.

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
- Gmail real y notificaciones operativas quedan para el Modulo 3. Mantener `CONTACT_LOCAL_MODE=1` durante estas pruebas: el formulario no envia correos reales y lo informa.
- Operacion reportada como probada por el usuario; no equivale a una validacion adicional del servidor realizada por Codex.
- Los productos fijos abren una ficha propia y se agregan a una seleccion local en `/carrito/`. Continuar permite crear una solicitud real desde `/pedido/solicitud/`, con cuenta, direccion y resumen confirmado. No reserva stock ni cobra.
- Registro, ingreso por correo, recuperacion, perfil, direcciones y solicitudes ya tienen backend. Jazmin aprueba desde Django Admin; el cliente consulta `/cuenta/pedidos/`. Los pedidos aprobados abren envio y pago: cotizacion Envia sandbox, reserva de stock y Stripe Checkout alojado en modo pruebas. Se requieren credenciales para probar la conexion externa; no hay cobros reales habilitados.
- `/tienda/revision/` permite revisar todas las pantallas y ejemplos de estados solo con DEBUG=True; devuelve 404 en produccion.
- Precios visibles no activan compras. Impresion 3D y excepciones marcadas en el PDF se cotizan.
- Disenos sobre prendas negras: DTF. Los modelos multicolor indican la regla segun el color elegido.
- El Modulo 2 tiene cotizacion, pago, cancelacion con devolucion completa y seguimiento manual de guias implementados. Se verificaron cobros y reembolso con Stripe sandbox. Los 79 productos de precio fijo tienen empaque asignado. Antes de ventas reales faltan validar fisicamente esos empaques y preparar la activacion operativa; las claves live siguen deshabilitadas. Ver [cancelaciones y seguimiento](docs/cancellations-tracking.md).

## Envios y pagos locales

Ver [operacion de envio y Checkout](docs/shipping-checkout-progress.md). Ejecutar `python manage.py migrate` y `python manage.py seed_shipping_profiles --apply` tras respaldar la base. Este comando conserva ediciones y solo asigna los SKU identificados; cajas y pesos siguen siendo provisionales.

En `.env`, configurar `ENVIA_TOKEN` del sandbox, `STRIPE_SECRET_KEY` de pruebas y `STRIPE_WEBHOOK_SECRET`. No compartir claves por chat ni versionarlas. `PAYMENT_ORIGIN=http://127.0.0.1:8000` permite el retorno local. Sin credenciales se muestran errores recuperables, no pagos simulados exitosos.

Con Stripe CLI instalado y autenticado en pruebas:

```powershell
stripe listen --events checkout.session.completed,checkout.session.expired,refund.created,refund.updated,refund.failed --forward-to http://127.0.0.1:8000/pagos/stripe/webhook/
python manage.py reconcile_payments --limit 100
python manage.py reconcile_refunds --limit 100
```

El primer comando muestra el secreto de firma de ese listener; configurarlo localmente en `.env` y reiniciar Django. La conciliacion se ejecuta manualmente en local; el operador debera programarla periodicamente al preparar produccion. El retorno desde Stripe no acredita por si solo un pago.

Cancelacion: **Mis pedidos → Ver pedido → Solicitar cancelacion**. Plazo: antes de cumplir 24 horas desde el pago, total menor a $2,000 MXN incluido envio, devolucion completa. No se repone stock automaticamente. Guias: **Admin → Orders → pedido pagado → Guia y seguimiento**; generar la guia en Envia antes de registrarla. Los reembolsos aparecen en **Payments → Cancelaciones y reembolsos**.

## Configuracion y persistencia

`config/settings.py` carga `.env`; las variables del entorno prevalecen. `.env.example` documenta las opciones, sin secretos reales. `setup_local.py` genera una clave aleatoria y no reemplaza un archivo existente.

`runtime/db.sqlite3`, `runtime/media`, cache y logs son locales y estan excluidos de Git y de la imagen Docker. Respaldar base y medios juntos. En contenedores viven en `runtime_data`; las fotos de catalogo y bundles estan en `static/`.

Gmail usa SMTP nativo de Django, sin automatizadores externos. WhatsApp y Facebook funcionan independientemente del correo.

## Errores e identidad

Paginas artisticas personalizadas para 400, 403, 404 y 500, incluida la denegacion CSRF. La pagina 500 no depende de consultas de base de datos ni muestra excepciones. Django muestra su pagina tecnica 404/500 cuando `DEBUG=1`; probar los handlers con `DEBUG=False` en tests, sin cambiar el entorno habitual.

Para revisarlas con el servidor local, abrir `/tienda/revision/` o `/tienda/revision/errores/400/` (tambien 403, 404 y 500). Estas vistas reutilizan las paginas originales y sus codigos HTTP, sin lanzar excepciones, sin consultas a la base de datos y sin cache. Solo funcionan con DEBUG=True; en produccion devuelven 404.

Favicon ICO, PNG y Apple Touch Icon derivados del logo suministrado, sin redibujarlo. Las fuentes y dependencias JavaScript se sirven localmente. Animaciones GSAP con alternativa de movimiento reducido y contenido accesible sin JavaScript.

## Verificacion

```powershell
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
docker compose config --quiet
```

Suite Django y pruebas puras del carrito (`node scripts/test_cart_state.cjs`). Scripts Playwright en `scripts/check_*.cjs` requieren Node, Playwright y Chrome; las utilidades de imagen requieren sharp o Pillow segun el script. No son dependencias de ejecucion del sitio. `check_store.cjs` comprueba la tienda en siete anchos. `check_errors.cjs` comprueba los errores en cuatro anchos. `check_accounts.cjs` y `check_orders.cjs` usan el servidor aislado del puerto 8011. Consultar [cuentas](docs/customer-accounts-progress.md) y [pedidos y aprobacion](docs/order-review-progress.md) para comandos y resultados.

El motor Docker no estaba disponible para la ultima comprobacion del agente. El despliegue real, TLS y SMTP no se afirman verificados por estas pruebas locales. `check --deploy` muestra advertencias esperadas con el entorno de desarrollo.

## Documentacion y Git

- [Estado del Modulo 1](docs/modulo-1-estado.md): alcance actual y pendientes diferidos.
- [Catalogo del cliente](docs/catalogo-cliente-2026.md): precios, fuentes y responsividad.
- [Administracion](docs/editar-contenido.md): fotos, permisos y respaldos.
- [Infraestructura](docs/fase-1-infraestructura.md): referencia historica y pasos de servidor; no es estado actual.
- `AGENTS.md`: Superpowers, ui-ux-pro-max y web-design-guidelines, aplicados segun la etapa. Los antiguos plugins UI UX Designer y Web Design fueron sustituidos; no se presentan como disponibles.

Rama de trabajo: `codex/pulido-visual`. `main` y `master` conservan la base anterior; un push de la rama no despliega ni fusiona automaticamente esos cambios.
