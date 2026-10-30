# Order Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crear solicitudes reales y privadas que Jazmin pueda aprobar desde Django Admin sin habilitar cobros prematuros.

**Architecture:** Nueva app orders con servicios atomicos para creacion y revision. Los templates actuales consumen esos servicios y el admin usa el mismo control de permisos y versiones. El carrito sigue siendo seleccion local, no inventario reservado.

**Tech Stack:** Django existente, SQLite local, templates, JavaScript nativo y CSS existentes; sin nuevas dependencias de produccion.

**Spec:** `docs/superpowers/specs/2026-10-21-order-review-design.md`

## Global Constraints

- Ejecucion directa en carpeta y rama actuales; no worktree, merge ni despliegue.
- Cuenta obligatoria; solo productos reales de precio fijo. No Stripe, envios, reservas, reembolsos ni nuevos correos en este bloque.
- 30 unidades iniciales por producto, no variante; inicializar solo stock desconocido, preservar valores definidos.
- Maximo 100 lineas distintas, 99 unidades por linea, notas 1500 caracteres; detalles por linea maximo 300 caracteres.
- 10 solicitudes nuevas por cliente por 15 minutos; repeticion idempotente no consume otra solicitud.
- Aprobacion exclusivamente por staff activo con `orders.approve_order`; registrar actor y fecha.
- Copias de precios y direccion; propietario/producto protegidos contra borrado. Solicitud y aprobacion no reservan inventario.
- Reutilizar estilo existente, no cambiar hero. Skills ui-ux-pro-max y web-design-guidelines para interfaz y revision.

## Review Focus

- Doble clic y timeout despues de commit: devolver el mismo pedido sin consumir otro intento (Task 2).
- Otra pestana cambia carrito durante envio: no borrar esa nueva seleccion (Task 4).
- Precio cambia entre resumen y envio: devolver conflicto y exigir nueva confirmacion (Task 2).
- Dos administradores revisan el mismo pedido: rechazar version obsoleta sin perder auditoria (Task 3).
- Producto o direccion se modifica despues de solicitar: historial conserva copia original (Task 1/2).

## Archivos y limites

- `orders/models.py`, `apps.py`, `migrations/`: persistencia y constraints; registrar app en `config/settings.py`.
- `orders/quotes.py`: validar seleccion y emitir resumen firmado para confirmacion.
- `orders/services.py`: creacion idempotente, limites y transiciones; sin HTTP ni templates.
- `orders/forms.py`, `views.py`, `urls.py`: formularios, autorizacion y respuestas privadas.
- `orders/admin.py`, `templates/admin/orders/order/change_form.html`: revision y errores recuperables; no duplicar reglas de servicio.
- `orders/management/commands/initialize_order_stock.py`: preview por defecto y `--apply` explicito.
- `orders/tests/test_models.py`, `test_requests.py`, `test_review.py`, `test_views.py`: pruebas por responsabilidad.
- `templates/orders/request.html`, `detail.html`, `list.html`, `static/js/orders.js`: experiencia de comprador; estilos en `static/css/store.css`.
- Integracion en `website/urls.py`, `templates/store/screen.html`, `templates/accounts/page.html`, `website/test_store.py`.
- `scripts/check_orders.cjs`, `config/test_accounts_browser.py`: navegador aislado, sin pedidos de prueba en base real.
- `README.md`, `docs/order-review-progress.md`: operacion y resultados.

### Task 1: persistencia e inventario inicial

**Interfaces:** Order con public_id UUID unico, customer PROTECT, currency MXN, subtotal Decimal(12,2), shipping_address JSON validado por servicio, notes, review_status (pending/changes/approved), approved_by SET_NULL, approved_at, review_note, version entero inicial 0, idempotency_key UUID y request_digest SHA256; unique(customer,idempotency_key). OrderItem con order CASCADE, product PROTECT, sku/name/unit_price/quantity/details; unique(order,product), cantidad >=1 y precio >=0. OrderReviewEvent con order PROTECT, actor SET_NULL, from_status/to_status/note/created_at. OrderCreationBucket OneToOne customer, started_at y count.

- [ ] Escribir test_models: constraints de cantidad/precio/clave, PROTECT de cliente/producto, stock command preview no escribe, `--apply` cambia null a 30 y conserva 0/12/30, conceptos y cotizaciones intactos.
- [ ] Ejecutar `.venv/Scripts/python.exe manage.py test orders.tests.test_models --noinput`; observar RED.
- [ ] Crear modelos, app y migracion; declarar permiso approve_order. Implementar comando con queryset fijo/no concepto y stock nulo; imprimir conteos, no PII. Agregar timestamps a Order y pedido de mas reciente primero.
- [ ] Ejecutar test_models y `makemigrations --check --dry-run`; exigir PASS y sin cambios pendientes.
- [ ] Respaldar SQLite mediante API backup con nombre nuevo, registrar conteos sin PII, migrar, preview y aplicar stock autorizado. Nunca sobrescribir respaldo anterior ni valores definidos.
- [ ] Commit `feat: add persistent order records and stock initialization`.

### Task 2: resumen y creacion segura

**Interfaces:** `build_quote(customer, rows, address_id, notes) -> dict`; `sign_quote(quote) -> str`; `create_order(customer, quote_token, idempotency_key) -> (Order, created: bool)`. Rows contienen exactamente id int, quantity int (no bool) y details str. Quote incluye owner, rows con precio, copia completa de direccion, notes, subtotal y currency; firma Django con salt propio `orders.quote.v1`, TTL 1800 segundos. Errores: ValidationError para datos, QuoteChanged para resumen desactualizado y OrderRateLimited(retry_after) para limite.

- [ ] Escribir test_requests: rechazar vacio, 101 lineas, duplicados, booleanos/negativos/100 unidades, productos no elegibles, stock nulo/insuficiente, direccion ajena, notas >1500 y detalles >300. Total Decimal exacto; snapshot no cambia tras editar origen.
- [ ] Agregar tests: firma manipulada/expirada/otro propietario; cambios de precio, disponibilidad o direccion exigen resumen nuevo; doble envio devuelve mismo ID; clave igual con payload distinto falla; 10 creaciones permitidas y 11 rechazada, reintento no consume cupo, ventana expirada permite. Fallo DB no deja lineas/pedido/cupo parcial.
- [ ] Ejecutar test_requests RED. Implementar quotes con ORM y serializer estructurado; ninguna cantidad monetaria proviene del cliente. Digest canonico JSON del contenido firmado. Comprobar repeticion existente antes de validar caducidad o disponibilidad para recuperar pedidos ya creados, pero verificar firma y propietario siempre.
- [ ] Implementar creacion y contador en transaccion; revalidar valores actuales sin recalcular silenciosamente. Capturar colision unique fuera de atomic y buscar pedido coincidente; SQLite ocupado produce error recuperable, no reintentos ilimitados ni bypass.
- [ ] Agregar TransactionTestCase con dos conexiones a SQLite de archivo: envios simultaneos crean un solo pedido; uno puede recibir fallo recuperable de contencion, su reintento obtiene el existente. No decrementar Product.stock.
- [ ] Ejecutar test_requests y test_models GREEN. Commit `feat: create idempotent order requests from server quotes`.

### Task 3: revision exclusiva de personal

**Interfaces:** `review_order(actor, order_id, expected_version, target_status, note) -> Order`; `ReviewConflict` para version obsoleta. Requiere staff activo y has_perm('orders.approve_order'); atomic update condicionado por version y evento en misma transaccion. target_status solo pending/changes/approved. Cambios requiere nota no vacia <=1500. Pasar a pending/changes borra aprobador/fecha actual, no el historial.

- [ ] Escribir test_review: cliente/staff sin permiso/inactivo denegados; staff permitido aprueba con actor/fecha; no-op conserva fecha/version/eventos; revocacion y cambios trazables; nota obligatoria; estado invalido rechazado; version antigua no escribe; error al crear evento revierte estado.
- [ ] Ejecutar test_review RED y crear servicio. Usar compare-and-swap para SQLite, no asumir select_for_update efectivo. Version enviada por formulario nunca reemplaza la version DB sin condicion.
- [ ] Implementar OrderAdmin con listas/filtros/busqueda; lineas y eventos inline solo lectura, sin alta/borrado de pedidos. Checkbox con etiqueta "Diseño revisado y aprobado por Jazmin", accion de solicitar cambios y nota, version oculta. Checkbox aprobado incompatible con solicitar cambios se rechaza. Campos comerciales y auditoria nunca editables.
- [ ] Pruebas HTTP admin con CSRF: staff con permiso limitado ve/guarda, sin approve_order puede consultar pero no revisar, POST manipulado no cambia subtotal/cliente/lineas. Conflicto y DatabaseError devuelven formulario con error recuperable, no 500 ni guardado de ModelAdmin que pise version del servicio.
- [ ] Ejecutar test_review GREEN. Commit `feat: add audited design approval in Django admin`.

### Task 4: solicitud y seguimiento del comprador

**Interfaces/rutas:** GET/POST `/pedido/solicitud/` name order_request (GET formulario, POST action=preview|confirm); GET `/cuenta/pedidos/` order_list; GET `/pedido/<uuid:public_id>/` order_detail; GET `/pedido/<uuid:public_id>/pago/` order_payment bloqueado. POST confirm usa quote_token y UUID de idempotencia del resumen. Reutilizar customer_required y store_context; todas las consultas limitadas al cliente.

- [ ] Escribir test_views: anonimo redirige login, cliente ajeno 404, CSRF 403, no-store, GET sin efectos, resumen previo, confirmacion redirect a detalle, errores conservan datos, limite429 con Retry-After y falloDB503 recuperable. POST de approved/actor/price no tiene efecto. Pago siempre inactivo y no revela pedido ajeno.
- [ ] Ejecutar test_views RED. Crear forms/views/urls/templates; reemplazar ruta placeholder de solicitud, conservar pago generico como informacion sin cobro. Agregar listado a cuenta sin consultar pedidos de terceros. Mostrar subtotal de referencia, no total final; estado textual y nota publica escapada.
- [ ] Crear orders.js solo para importar seleccion local al formulario. Detalles por producto y selector de direccion propia, resumen renderizado por servidor; preservar seleccion ante login, errors o refresh. Nunca usar innerHTML con datos del cliente. UUID de confirmacion se conserva al reintentar.
- [ ] Tras exito, limpiar carrito solo si coincide exactamente con IDs/cantidades enviados; si otra pestana lo cambio, conservarlo y avisar. GET ordinario de detalle no limpia carrito. Añadir tests de ambos casos.
- [ ] Enlace WhatsApp solo referencia publica codificada y texto fijo; no incluir correo/direccion. UI sin JS explica limitacion de seleccion local y enlaza catalogo/contacto. Sin direccion enlaza agenda; el carrito persiste mientras se agrega.
- [ ] Estilos scoped, 44px tactil, foco/errores/labels, feedback sin movimiento si prefers-reduced-motion. Aplicar ui-ux-pro-max y revisar guidelines vigentes; no animar el admin global ni modificar hero.
- [ ] Ejecutar test_views y suite completa GREEN. Actualizar test_store solo para el contrato nuevo autorizado, conservar ausencia de pagos. Commit `feat: connect customer order submission and tracking`.

### Task 5: verificacion e integracion

- [ ] Crear check_orders.cjs en servidor de pruebas aislado: producto fijo, cliente y staff con permiso efimeros; solicitud, doble envio, consulta propia, aprobacion en admin, revocacion y nota de cambios. Comprobar boton de cobro inactivo en todos los estados. Nunca registrar claves/tokens ni usar cuentas del propietario.
- [ ] Verificar cliente y admin a 390 y 1440; formularios/listado/detalle en 320,390,844,1440,1920, teclado, errores, sin JS, sin overflow. Capturas inspeccionadas, no solo guardadas. Cerrar servidor temporal al terminar.
- [ ] Ejecutar `manage.py test`, `manage.py check`, `manage.py makemigrations --check --dry-run`, `node scripts/test_cart_state.cjs`, check_orders y regresiones check_accounts/check_store/check_browser/check_process/check_hero/check_errors. Comandos Python usan .venv/Scripts/python.exe. Exigir exit0; documentar cualquier limitacion real.
- [ ] Revision independiente final segun executing-plans, con spec y diff; corregir hallazgos importantes con tests RED/GREEN antes del cierre.
- [ ] Documentar como consultar/aprobar/revocar, permisos de Jazmin sin compartir contrasenas, stock preservado, bloqueo de pagos, resultados y tareas diferidas a Modulo 3. Actualizar README y ledger.
- [ ] `git diff --check`, revisar archivos staged sin secretos/datos de prueba; commit final y push rama codex/pulido-visual. Mantener servidor local para el usuario, sin merge/deploy.

## Revision del plan

Cobertura comprobada: snapshots e inventario (1), validacion/idempotencia/limites (2), permisos/auditoria/version (3), UI y privacidad (4), regresiones/operacion (5). No dependencias de proveedor externo ni datos de envio inventados. Firmas usadas por consumidores coinciden con interfaces declaradas.

Plan aprobado y ejecutado directamente, con revision independiente final. Las listas anteriores conservan los pasos originales; resultados y decisiones de ejecucion en docs/order-review-progress.md.
