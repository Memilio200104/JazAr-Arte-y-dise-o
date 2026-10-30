# Order review execution ledger

Plan and spec: docs/superpowers/{plans,specs}/2026-10-21-order-review*.md.
Approved 2026-10-22. Direct execution in current checkout; baseline 441b9c7.
Preflight: existing customer decorator, catalog queryset and local cart reused. No external provider required.
Task 1 complete: model tests RED (missing module) -> GREEN 2/2. Backup runtime/backups/before-orders-20261022.sqlite3; 91 products and 3 users before migration. Initialized 79 unknown fixed-product stocks to 30; no differing defined stocks.
Tasks 1-5 completed and verified. Integrated commits on codex/pulido-visual; no merge or deployment.
Ruling: admin uses a separate review POST after the read-only change form, rather than ModelAdmin save hooks. Prevents generic model saves from bypassing version checks; cost: a separate save-review button.
Ruling: styles isolated in orders.css rather than adding to minified store.css; keeps new selectors scoped to order pages. Cost: one small local stylesheet.
Task 2: validation/idempotency/snapshot/limit/rollback tests RED -> GREEN; file-backed concurrency test PASS (duplicate requests yield one order and one rate-limit count). SQLite contention is recoverable.
Task 3: permission/approval/conflict/audit tests RED -> GREEN. Review notes are public and never privileged instructions.
Task 4: anonymous request and missing views RED -> GREEN; private detail, CSRF, error handling and disabled payment checked. Main DB remains 91 products, 3 users, 0 orders; browser data isolated.
Final review: three important findings reproduced then fixed: raw cart mutation on rejected confirmation (Playwright RED -> GREEN); missing read-only inlines for limited staff (test_admin_review RED -> GREEN); changed approval attribution on note edit (test_note_edit_preserves_approval_attribution RED -> GREEN). No deferred minor findings.

## Operacion local

1. El comprador agrega productos al carrito, pulsa Continuar, ingresa a su cuenta y elige una direccion guardada. Puede indicar talla/color y notas como instrucciones para revisar, no como variantes garantizadas.
2. Revisa subtotal y direccion, luego Solicitar revision. El pedido conserva esa copia; no cambia si despues se edita la agenda o el catalogo.
3. En `/cuenta/pedidos/` consulta estado, nota y enlace WhatsApp con referencia del pedido. Envia PDF/PNG por ese medio.
4. Jazmin entra en `/admin/orders/order/`, abre el pedido, marca "Diseno revisado y aprobado por Jazmin" y pulsa "Guardar revision". Para pedir ajustes, desmarca aprobacion, marca Solicitar cambios y escribe la nota visible para el cliente. Para volver a pendiente desmarca ambas opciones.
5. Una revision simultanea obsoleta exige recargar. No sobrescribir la decision de otra persona ni editar precios/direccion del pedido desde admin.

Usar cuenta staff individual con permisos orders.view_order y orders.approve_order. No necesita permisos de edicion de catalogo o usuarios para revisar pedidos. Los superusuarios existentes pueden hacerlo; no se cambiaron sus contrasenas ni se promovio al comprador. Para crear la cuenta de Jazmin, el propietario administra usuarios/permisos desde Django Admin y establece una contrasena propia, no compartida.

Subtotal es de referencia; envio no calculado. Aprobacion necesaria pero no suficiente para pagar. No hay sesiones Stripe, reserva, reembolso ni correo operativo. Esos controles se conectaran en su bloque, revalidando estado y disponibilidad.

## Verificar sin tocar datos reales

```powershell
python manage.py migrate --settings=config.test_accounts_browser
python manage.py runserver 8011 --settings=config.test_accounts_browser --noreload
# Otra terminal, Node + Playwright + Chrome:
node scripts/check_orders.cjs
python manage.py test orders.tests.test_concurrency --settings=config.test_orders --noinput
```

El script crea cliente, staff y producto aleatorios SOLO en runtime/accounts-browser.sqlite3; no imprime contrasenas. La prueba concurrente utiliza runtime/orders-concurrency-test.sqlite3, archivo exclusivo descartable de pruebas. Nunca usar estos settings para produccion. Cerrar servidor 8011 al terminar.

`python manage.py initialize_order_stock` muestra conteos sin escribir; `--apply` fija 30 solo donde stock es null, producto real y precio fijo. No rellena stocks ya consumidos. Respaldo de esta migracion: runtime/backups/before-orders-20261022.sqlite3.

## Revision de interfaz

ui-ux-pro-max aplicado al flujo y controles. Web Interface Guidelines vigente consultado el 22 de octubre de 2026: etiquetas, feedback de errores, foco, estados textuales, dimensiones tactiles, lectura sin JS y movimiento reducido. orders.css limita sus estilos a las paginas de pedido. Capturas de detalle desktop/movil inspeccionadas; no overflow en cinco anchos. No se modifico el hero.

## Resultado final (22 de octubre de 2026)

Mejora posterior aprobada: Mis pedidos ahora es un boton magenta con icono, debajo del titulo de Mi cuenta. Prueba de template RED/GREEN y recorrido de cuentas en cinco anchos PASS; captura movil inspeccionada. Reutiliza foco, contraste y movimiento reducido existentes; revision web-design-guidelines sin incidencias en este cambio acotado.

- Suite completa: 80 pruebas Django PASS; concurrencia SQLite de archivo PASS.
- check_orders PASS: solicitud, stock cambiado antes de confirmar, carrito preservado, aprobacion/revocacion, cambios, pago inactivo, 5 anchos y alternativa sin JS. Capturas de formulario, detalle y admin movil inspeccionadas.
- check_accounts, check_store, check_browser, check_process, check_hero, check_errors y test_cart_state PASS.
- manage.py check y makemigrations --check --dry-run sin incidencias; git diff --check limpio salvo avisos de normalizacion CRLF.
- Tres hallazgos importantes de revision independiente corregidos con regresion RED/GREEN; suite final 80/80. No hallazgos menores diferidos.
- Sin pedidos ficticios en la base principal; el servidor aislado 8011 se cierra al terminar. Servidor habitual 8000 disponible.
