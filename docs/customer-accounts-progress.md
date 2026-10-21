# Accounts execution ledger

Plan: docs/superpowers/plans/2026-10-20-customer-accounts.md
Spec and direct execution approved. Current checkout requested by user.
Baseline: 43 tests PASS. Backup: runtime/backups/before-accounts-20261020.sqlite3.
Migration 0001 applied; pre-migration products 91 (including concepts), staff 2.
Ruling: start tests in one accounts/tests.py while suite remains small; split when responsibility warrants it.
Ruling: SQLite lock contention is a recoverable request failure, never a bypass of rate limiting or uniqueness. Row-lock semantics are not assumed on SQLite.
Tasks 1-5 implemented and verified. No merge or deployment performed.

## Uso local

- `/cuenta/registro/`: nombre completo, correo y contrasena; no exige direccion al crear cuenta.
- `/cuenta/ingresar/` y `/cuenta/`: ingreso y nombre editable, correo de solo lectura.
- `/cuenta/direcciones/`: varias direcciones privadas, una predeterminada, confirmacion antes de eliminar.
- `/cuenta/recuperar/`: recuperacion nativa Django. Verificacion y recuperacion caducan en 24 horas.
- `ACCOUNT_ORIGIN` define el origen de los enlaces. Sin variable, DEBUG usa `http://127.0.0.1:8000`; fuera de desarrollo se exige HTTPS y origen configurado.
- Gmail sigue pendiente: con CONTACT_LOCAL_MODE los enlaces se imprimen en la consola, no se entregan correos reales. Ejecutar `python manage.py runserver` en una terminal visible para abrirlos; tratar esos enlaces como secretos.
- Programar diariamente `python manage.py prune_auth_limits` al desplegar. No se ha creado una tarea de sistema.
- Pedidos, envio dinamico, reservas y pagos NO estan implementados en este bloque. Las direcciones futuras del pedido deberan copiarse, no depender del registro editable del cliente.

## Verificacion y revision

67 pruebas Django: identidad, limites, CSRF, propiedad de direcciones, recuperacion, caducidad, sesiones y concurrencia. Se conservaron 91 productos y 2 usuarios staff tras migrar.
Revision independiente: corregidos espacios significativos en contrasenas y respuestas recuperables ante fallos de escritura. Regresiones RED observadas y GREEN en suite completa.
Pruebas de navegador: registro, ingreso, nombre, dos direcciones, cambio de predeterminada, eliminacion, logout y recuperacion; anchos 320, 390, 844, 1440 y 1920. Capturas desktop/movil revisadas.

Revision ui-ux-pro-max y web-design-guidelines (fuente vigente consultada el 21 de octubre):
- `static/css/site.css:155`: reglas globales de nav tapaban el formulario movil; acotadas a #site-nav y protegidas por asercion de navegador.
- `templates/accounts/page.html`: etiquetas, estados vacios, confirmacion destructiva y acciones semanticas revisadas.
- `templates/accounts/fields.html`: errores asociados a campos y foco mediante site.js; contrasenas permiten pegado/autocompletado.
- Sin cambios al hero ni activacion de cobros.

Regresiones: check_store (7 anchos), check_browser (5 anchos y sin JS), check_process (panel de Codex y scroll reversible), check_hero (1920x1080) y check_errors (4 anchos) PASS. Estado puro del carrito PASS. Check Django y migraciones pendientes: sin incidencias. Servidor aislado de pruebas cerrado; servidor local habitual disponible en puerto 8000.
El ajuste de especificidad CSS requirio actualizar tambien la alternativa noscript; se reprodujo el fallo antes de confirmar el nuevo PASS.

## Reproducir navegador sin datos reales

```powershell
python manage.py migrate --settings=config.test_accounts_browser
python manage.py runserver 8011 --settings=config.test_accounts_browser --noreload
# En otra terminal con Playwright y Chrome disponibles:
node scripts/check_accounts.cjs
```

El servidor de prueba usa runtime/accounts-browser.sqlite3 y correo en memoria. Su hasher rapido es SOLO para pruebas: nunca desplegar config.test_accounts_browser. Cerrar ese servidor al terminar.

Desviaciones registradas: tests agrupados en un archivo; concurrencia comprobada con SQLite compartido de Django en memoria, no archivo. La base aislada de navegador si usa archivo. Un commit integrado de implementacion sustituye los commits por tarea del plan.
