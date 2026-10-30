# Operación técnica del MVP

[Volver al manual](README.md) · MVP 1.0 · Para el responsable del proyecto

Esta guía acompaña la entrega local; no sustituye una configuración de producción ni ejecuta el despliegue. La rama de referencia del MVP es `main`. Las credenciales, las cuentas y los datos locales no viajan con Git.

## Arranque habitual

Desde la carpeta del proyecto, en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver
```

Abre http://127.0.0.1:8000/. Sin activar el entorno puedes usar `.\.venv\Scripts\python.exe manage.py runserver`. Si ya hay un servidor en el puerto 8000, usa ese proceso o detenlo antes de iniciar otro; cambiar el puerto requiere revisar también las direcciones de retorno y webhook.

Para instalar en otra máquina, sigue **Preparar otra maquina** en el [README principal](../../README.md). Ejecuta la importación inicial del catálogo solo cuando corresponda, no en cada arranque. `--update-site` sustituye explícitamente textos y retrato de portada.

## Datos, cuentas y permisos

- Base local: `runtime/db.sqlite3`.
- Fotos subidas: `runtime/media/`.
- Activos incluidos en el proyecto: `static/`.
- Configuración privada: `.env`, excluido de Git. Las variables del proceso prevalecen sobre el archivo; reinicia Django después de cambiarlo.

Para crear un administrador en una instalación nueva:

```powershell
python manage.py createsuperuser
```

Para cambiar una contraseña existente, usa `python manage.py changepassword NOMBRE_DE_USUARIO`. El comando la solicita de forma interactiva. No publiques contraseñas en documentación ni conviertas una cuenta de cliente en superusuario para resolver un problema de acceso.

La cuenta operativa de Jazmin debe estar activa y ser staff. Concede solo lo que necesita:

| Función | Permisos relevantes |
|---|---|
| Consultar y revisar pedidos | `orders.view_order`, `orders.approve_order` |
| Registrar guías | Los de consulta de pedidos y `shipping.manage_shipment` |
| Consultar y conciliar pagos | `payments.view_paymentattempt`, `payments.reconcile_payment` |
| Consultar y conciliar devoluciones | `payments.view_refund`, `payments.reconcile_refund` |
| Editar catálogo, paquetes y portada | Ver, agregar y cambiar los modelos correspondientes de `website`; omitir eliminación en la operación habitual. |
| Editar y validar empaques | Ver, agregar y cambiar `shipping.PackageProfile` y `shipping.ProductPacking`. |

La administración de usuarios requiere especial cuidado: los permisos del administrador estándar pueden permitir cambios de privilegios. Mantén esa tarea en una cuenta de confianza controlada por el responsable; el panel del Módulo 3 deberá exponer acciones acotadas como bloquear usuarios.

En el MVP el comprador ingresa por correo a `/cuenta/ingresar/`; el administrador usa el nombre de usuario de su cuenta staff en `/admin/`. Estar autenticado como comprador no concede acceso administrativo. Una cuenta staff sin perfil de comprador tampoco equivale automáticamente a una cuenta de compra.

## Proveedores y configuración local

Usa `.env.example` y `config/settings.py` como referencia de variables. La aplicación lee `ENVIA_TOKEN`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` y `PAYMENT_ORIGIN`. El nombre histórico `STRIPE_TOKEN` no debe darse por suficiente: comprueba que la clave esté asignada a la variable que lee esta versión. Stripe Checkout alojado no necesita que el navegador reciba la clave secreta.

Conserva el entorno de pruebas: el cliente de Stripe rechaza claves live. Para habilitar ventas reales hará falta una entrega de activación explícita, no solo editar `.env`. Los empaques iniciales deben validarse físicamente antes de esa activación.

En una terminal separada, el operador inicia Stripe CLI autenticado en pruebas:

```powershell
stripe listen --events checkout.session.completed,checkout.session.expired,refund.created,refund.updated,refund.failed --forward-to http://127.0.0.1:8000/pagos/stripe/webhook/
```

Configura el secreto de firma que muestra ese listener en `STRIPE_WEBHOOK_SECRET` y reinicia Django. No confundas ese secreto con la clave API. Mantén el listener abierto mientras pruebas la entrega de eventos. Nunca copies su salida con secretos a Git o al manual.

Para recuperar estados pendientes, con las credenciales configuradas:

```powershell
python manage.py reconcile_payments --limit 100
python manage.py reconcile_refunds --limit 100
```

Estos comandos consultan proveedores y pueden actualizar estados de pagos, reservas y devoluciones; no son simples informes. La recuperación de una cancelación ya solicitada puede completar su petición de reembolso. Revisa el entorno y las solicitudes existentes antes de ejecutarlos. El segundo también consulta devoluciones confirmadas por posibles rechazos posteriores.

El retorno del navegador no acredita un pago: se confirma mediante la consulta canónica a Stripe. No edites estados financieros directamente ni liberes reservas porque haya transcurrido tiempo sin comprobar la sesión. El detalle del mecanismo está en [cancelaciones y seguimiento](../cancellations-tracking.md) y [envíos y Checkout](../shipping-checkout-progress.md).

## Correo local y soporte

Con `CONTACT_LOCAL_MODE=1`, los enlaces de cuentas se generan en la consola de Django; no se entregan por Gmail. El formulario de contacto informa su modo local y ofrece contacto alternativo. Mantén este modo hasta abordar el Módulo 3.5.

Para ayudar con recuperación o verificación en local, identifica la solicitud correcta en la consola. Trata esos enlaces como credenciales temporales; no los publiques ni incluyas en capturas. La conexión real de Gmail y los avisos a clientes o Jazmin todavía no forman parte de esta entrega.

## Respaldo y restauración

Respalda **base y medios juntos** antes de migraciones importantes, importaciones o ajustes masivos. Suspende las escrituras del sitio y del administrador durante el respaldo. Para SQLite utiliza su API de backup; no copies un archivo de base que está recibiendo escrituras.

Ejemplo local, con el servidor detenido y desde la raíz del proyecto:

```powershell
@'
from datetime import datetime
from pathlib import Path
import shutil
import sqlite3

source = Path('runtime/db.sqlite3').resolve()
if not source.is_file():
    raise SystemExit('No existe la base local; revisa la carpeta antes de continuar.')
target = Path('runtime/backups') / datetime.now().strftime('%Y%m%d-%H%M%S')
target.mkdir(parents=True, exist_ok=False)
with sqlite3.connect(source.as_uri() + '?mode=ro', uri=True) as src:
    with sqlite3.connect(target / 'db.sqlite3') as dst:
        src.backup(dst)
media = Path('runtime/media')
if media.exists():
    shutil.copytree(media, target / 'media')
print('Respaldo creado en:', target)
'@ | .\.venv\Scripts\python.exe -
```

Conserva una copia fuera del equipo, con acceso restringido porque contiene datos de clientes. Guarda `.env` aparte mediante un medio privado; no dentro del repositorio.

Para restaurar: detén el servidor, conserva el estado actual, verifica el respaldo en una copia separada y restaura su base y medios juntos. Usa una versión de código compatible, aplica las migraciones requeridas y comprueba cuentas, productos y pedidos antes de reabrir. Restaurar una base antigua no revierte operaciones ya efectuadas en Stripe o Envia: concilia esas diferencias antes de permitir pagos.

En Docker los datos persisten en `runtime_data`. No uses `docker compose down -v` como rutina de mantenimiento: elimina los volúmenes. El despliegue y su política de respaldo los define el responsable del servidor.

## Verificación de una entrega

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test --noinput
node scripts/test_cart_state.cjs
git diff --check
```

Las pruebas automatizadas de Django usan bases de prueba; no sustituyen el recorrido contra los proveedores configurados. Para una comprobación manual coordinada, recorre compra → aprobación → envío → pago → consulta; prueba cancelación sobre un pedido separado y registra una guía ficticia únicamente en datos internos. Nunca pruebes devoluciones sobre pedidos de un cliente sin autorización.

Las páginas de error se pueden revisar con `DEBUG=True` en `/tienda/revision/errores/400/`, `/403/`, `/404/` y `/500/`, usando el mismo prefijo completo para cada código. El índice es `/tienda/revision/`. Estas rutas de revisión no se publican con `DEBUG=False`.

## Qué comprobar antes de publicar

El despliegue lo realiza el usuario. Esta entrega no afirma verificados dominio, HTTPS, Docker en ejecución ni SMTP real. Antes de abrir ventas hay que comprobar la infraestructura, configuración de producción, credenciales y webhooks del entorno correcto, empaques reales, conciliación periódica, respaldos y permisos del operador. Gmail conserva su planificación independiente en el Módulo 3.5.
