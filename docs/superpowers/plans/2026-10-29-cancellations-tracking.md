# Plan: cancelaciones y seguimiento

Goal: completar devolución íntegra elegible y seguimiento privado en Mis pedidos.
Architecture: servicios Django transaccionales, Stripe SDK con idempotencia, webhook canónico, registro administrativo de guía.
Stack: Django, SQLite local/PostgreSQL compatible, Stripe, templates existentes.
Spec: ../specs/2026-10-29-cancellations-tracking.md
Execution: Superpowers executing-plans, ejecución directa en carpeta/rama actual autorizada.

## Restricciones globales
No cobros reales, despliegue, Gmail ni portal administrativo Módulo 3. No publicar secretos. Mantener el pago histórico y el stock consumido. No presentar aceptación API como devolución consumada.

## Tareas
1. RED→GREEN: fecha canónica, límite 24h/2000, solicitud única y recuperación idempotente; migraciones.
2. RED→GREEN: webhook de refund y conciliación administrativa/CLI, rechazo de importes/referencias ajenos.
3. RED→GREEN: registro de guía privado y autorizado, estados y confirmación accesible de cancelación.
4. Suite completa, migraciones, revisión UI, ensayo Stripe sandbox sobre pedido interno existente y documentación.

## Review Focus
- Límite exacto, reloj del proveedor y pedidos históricos sin fecha.
- Timeout tras aceptación de reembolso, duplicados y eventos fuera de orden.
- Propiedad, permisos, CSRF y enlaces de seguimiento.
- Carrera entre solicitud de cancelación y registro de guía; ningún nuevo cobro/restock.
- Diferenciar reembolso pendiente/fallido de confirmado y conservar importe total con envío.

## Evidencia / ledger
- Inicio: HEAD 00abf55, árbol limpio. Reglas comerciales confirmadas en este chat.
- Ruling: no reponer stock automáticamente — personalización puede impedir reutilizar piezas; Jazmin ajusta existencias después de revisar físicamente.
- Ruling: no excluir pedidos en producción/enviados del plazo aprobado — no inventar una condición comercial; la operación debe atender cancelaciones y guías fuera del sitio.
- Tareas 1–3: implementadas; 20 pruebas focalizadas PASS tras observar fallos por funcionalidad ausente. Migraciones payments.0003 y shipping.0003 aplicadas tras respaldo SQLite.
- Final review: review_refunds_tracking (revisor independiente). Un hallazgo P1: devolución inicialmente confirmada podía fallar después por rechazo bancario.
- Final: fixed transición succeeded→failed y conciliación administrativa de confirmados — dos pruebas RED→GREEN; suite posterior 147/147 PASS.
- Tarea 4: devolución de 599.51 MXN sandbox completada mediante interfaz. Evento real recuperado/reproducido dos veces con firma válida, un solo evento persistido. Guía interna guardada por vista admin con historial. Inventario de 92 registros sin cambios frente al respaldo de esta implementación. Evidencia en docs/cancellations-tracking.md.
- Ruling: mantener rama actual y hacer push autorizado, sin fusionar ni desplegar — respeta ejecución directa y entrega local; main/master no reciben este avance automáticamente.
- UI: confirmación accesible, loader, formulario sin JS, controles táctiles y límites de ancho comprobados; seguimiento sin overflow 320/844/1920px, cancelación 390px. No hallazgos menores del revisor pendientes.
- Verificación final: `manage.py test --noinput` → 148/148 PASS (74.65s), incluida concurrencia de cancelaciones; check sin incidencias, migraciones sin diferencias. Documentación operativa actualizada; cuentas QA desactivadas.
