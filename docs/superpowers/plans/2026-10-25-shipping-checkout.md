# Shipping and Hosted Checkout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cotizar paquetes agrupados en Envia.com y pagar pedidos aprobados mediante Stripe Checkout alojado, exclusivamente en pruebas.

**Architecture:** Extender orders sin reemplazar sus solicitudes ni cuentas. Separar shipping (empaques, agrupacion, adapter y cotizaciones) de payments (reservas, adapter Stripe y reconciliacion); ambos consumen snapshots del pedido. Las operaciones externas quedan fuera de transacciones de base de datos.

**Tech Stack:** Django 5.2, SQLite local, Python, SDK oficial Stripe, templates Django, CSS existente, Playwright. Sin Celery ni nuevo framework frontend.

**Spec:** docs/superpowers/specs/2026-10-25-shipping-checkout-design.md

Estado: aprobado y ejecutado localmente. Aceptacion externa sandbox pendiente de credenciales. Resultado detallado y decisiones en docs/shipping-checkout-progress.md; los pasos siguientes se conservan como plan original, no como afirmacion de pruebas externas realizadas. Ejecucion directa en carpeta y rama actuales, metodo previamente elegido. No crear worktree ni desplegar.

## Global Constraints

- Cuenta obligatoria; solo personal autorizado aprueba; pagos posteriores a aprobacion.
- Envia sandbox y Stripe test; rechazar claves/eventos live. No comprar guias ni activar dinero real.
- Agrupar por compatibilidad/capacidad/peso; no un paquete por unidad por defecto.
- MXN, destinos Mexico, tarifas desde servidor, sin tarifa ficticia de respaldo.
- Cotizaciones hasta 10 minutos; recotizar antes de Checkout y reconfirmar cambios de total.
- Reserva/sesion de 30 minutos; no liberar solo por reloj local ni por volver desde Stripe.
- No textos de demo/prueba en interfaz publica JazAr; no ocultar indicadores de Stripe.
- Conservar hero y estilos existentes. Gmail, portal propio staff y reembolsos automaticos fuera de este bloque.
- Respaldar SQLite antes de migrar base principal; fixtures y pedidos de pruebas solo en DB aislada.
- Las claves no existen todavia: no declarar recorrido sandbox real verificado usando mocks.

## Review Focus

1. Capacidad valida pero peso excedido: separar cajas, sin perder cantidades (Task 1).
2. Perfil editado con tarifa visible: invalidar la seleccion, sin modificar sesion abierta (Task 2/4).
3. Creacion Stripe con timeout pero sesion existente: misma clave y reserva, sin doble cobro (Task 4).
4. Aprobacion revocada mientras se intenta pagar: solo una transicion debe ganar (Task 3/4).
5. Callback tardio tras expiracion o evento repetido: reconciliar estado canonico y no descontar dos veces (Task 5).

## Mapa de archivos

- Crear shipping/{apps,models,admin,packing,envia,services}.py y shipping/tests/: reglas y API de envio.
- Crear payments/{apps,models,admin,inventory,stripe_gateway,services,views,urls}.py y payments/tests/: pagos y reservas.
- Crear payments/management/commands/reconcile_payments.py: recuperacion operativa.
- Modificar config/settings.py, config/urls.py, requirements.txt, .env.example: integracion segura.
- Modificar orders/services.py, orders/urls.py, orders/admin.py: proteger revision y conectar pantalla pago.
- Modificar website/models.py, website/admin.py y disponibilidad en website/store_presenters.py / orders/quotes.py tras inspeccionar sus contratos: reservas visibles, no sobreventa.
- Crear templates/payments/checkout.html; modificar templates/orders/{detail,list}.html y static/css/orders.css.
- Crear scripts/check_checkout.cjs; actualizar README y docs/shipping-checkout-progress.md.

## Task 1: Empaques editables y agrupacion determinista

**Files:** shipping/apps.py, models.py, admin.py, packing.py, tests/test_packing.py; config/settings.py; migraciones shipping.

**Interfaces:** PackageProfile(code, length_cm, width_cm, height_cm, tare_kg, max_weight_kg, capacity, active, validated_at, validated_by). ProductPacking(product OneToOne, profile FK, protected_unit_weight_kg, capacity_units, validated_at, validated_by). `pack_order(order: Order) -> PackingResult`, con packages JSON-serializables y fingerprint de configuracion; Decimal serializado como cadenas. Cada paquete contiene perfil, dimensiones, peso y composicion product_id/quantity. Errores ValidationError.

- [ ] Escribir tests fallidos: dos productos del mismo perfil comparten una caja; capacidad 4 y 5 unidades de ocupacion 1 producen [4,1]; tara 0.1 + 2 unidades de 0.2 = 0.5kg. Peso fuerza otra caja aunque quede capacidad; perfiles distintos nunca mezclan; input reordenado produce mismo resultado. Rechazar perfil ausente/inactivo, unidad demasiado grande/pesada, pesos no positivos y cantidades invalidas.
- [ ] Ejecutar `.venv/Scripts/python.exe manage.py test shipping.tests.test_packing` y verificar fallo por implementacion ausente.
- [ ] Implementar perfiles con constraints positivos, capacidad entera, trazabilidad y permisos admin. Cambiar campos operativos borra validacion. Agrupar con first-fit decreasing: orden estable (-capacity_units, -weight, product_id), primera caja compatible con espacio/peso, abrir nueva si ninguna admite. No usar volumen como prueba de cabida. Peso bruto calculado con Decimal, no float.
- [ ] Crear comando `seed_shipping_profiles` con dry-run por defecto y `--apply`; perfiles textiles/tazas/voluminosos provisionales, sin inferir compatibilidad solo por nombre. Asignaciones explicitas verificadas contra catalogo existente; dejar sin asignar productos ambiguos. Nunca sobrescribir perfiles/asignaciones editados. Test de idempotencia y preservacion. Documentar valores escogidos y unidades.
- [ ] Ejecutar tests shipping y `manage.py makemigrations --check --dry-run`; verificar PASS y migraciones coherentes. Commit de archivos acotados.

## Task 2: Cotizacion agrupada en Envia

**Files:** shipping/envia.py, services.py, models.py, tests/test_quotes.py, tests/test_envia.py; config/settings.py, .env.example.

**Interfaces:** `quote_rates(origin: dict, destination: dict, packages: list[dict]) -> list[Rate]`; Rate = carrier, service, amount_minor:int, currency:str, provider_reference:str, expires_at opcional. `fetch_order_rates(customer, order_id) -> list[ShippingQuote]`; `refresh_selected_quote(customer, quote_id) -> (ShippingQuote, changed: bool)`. ShippingQuote guarda snapshot, fingerprint, propietario y expiracion.

- [ ] Consultar contrato vigente en docs.envia.com (seguir indice oficial, sin adivinar rutas). Registrar endpoints, campos, unidades, impuestos incluidos y soporte multipaquete en ledger. Fijar fixtures de respuestas anonimizadas basadas en contrato; no afirmar llamada real sin cuenta.
- [ ] Escribir tests fallidos: todas las cajas enviadas juntas; moneda distinta/repuesta incompleta/total ambiguo rechazados; no disponibilidad no ofrece tarifa cero; timeout produce error recuperable. Otra cuenta, pedido sin aprobar o destino fuera de MX rechazados antes de API. Vencimiento min(proveedor, ahora+600s), cambios de perfil invalidan fingerprint.
- [ ] Ejecutar `.venv/Scripts/python.exe manage.py test shipping.tests.test_quotes shipping.tests.test_envia`; verificar RED.
- [ ] Implementar adapter limitado a host sandbox fijo, timeout 10s, parseo estructurado y normalizacion Decimal a centavos. Sin PII/tokens en logs; errores publicos controlados. Si el contrato no proporciona total completo, no ofrecerlo. Rate limit DB por cliente (10 consultas externas/5 minutos), cache privada por fingerprint hasta 60s; recotizacion final ignora cache. Reusar patron de buckets existente, no cache global con PII.
- [ ] Implementar snapshots/fingerprint que incluyen paquetes, origen, destino y configuracion relevante. Tarifas vinculadas al pedido y usuario. Comparar servicio/moneda/importe/configuracion al refrescar y exigir reconfirmacion si cambia. Tests de rate limit, timeout, cache y edicion de perfiles.
- [ ] Ejecutar tests shipping, comprobar ausencia de secrets en diff, commit acotado.

## Task 3: Reserva atomica y proteccion de revision

**Files:** payments/models.py, inventory.py, tests/test_inventory.py, tests/test_concurrency.py; website/models.py, admin.py, store_presenters.py; orders/quotes.py, services.py.

**Interfaces:** Product.reserved_stock entero >=0, con constraint reserved_stock<=stock para stocks definidos; StockReservation(attempt, product, quantity, state held/consumed/released), unico attempt/product. `reserve_order(order_id, quote_id) -> PaymentAttempt`; `consume_reservation(attempt_id)` y `release_reservation(attempt_id)` son funciones internas solo para reconciliacion validada. PaymentAttempt contiene campos de spec y constraint parcial un intento no terminal por pedido, y maximo un paid por pedido.

- [ ] Escribir tests RED: ultimo stock compartido no se reserva dos veces; disponibilidad stock-reserved_stock; reserva de varias lineas revierte completa si falla una; consume resta stock y reserved_stock una sola vez; release solo resta reserved_stock. Stock null no vendible. Admin no permite stock<reserved_stock. Revocacion contra reserva simultanea no permite checkout aprobado obsoleto.
- [ ] Ejecutar `.venv/Scripts/python.exe manage.py test payments.tests.test_inventory`; verificar RED.
- [ ] Implementar contador reservado y filas de auditoria en misma transaccion. Updates condicionales F, orden por product_id, no depender solo de select_for_update en SQLite. Serializar cambios del pedido mediante version CAS usada por orders.services; revalidar aprobacion en la transaccion de reserva. Conflictos de DB retornan error reintentable sin dejar reservas parciales.
- [ ] Integrar disponibilidad en catalogo/validacion sin cambiar el contrato publico de stock fisico admin. Bloquear transiciones de aprobacion con intento creating/open/reconciliation_required o paid; notas siguen permitidas. Tests conservan atribucion de aprobacion.
- [ ] Ejecutar tests orders, website y payments; concurrencia con DB de archivo usando configuracion aislada (extender config/test_orders.py). Comprobar conteos y rollback; commit acotado.

## Task 4: Sesion Stripe alojada y recuperacion de creacion

**Files:** payments/stripe_gateway.py, services.py, tests/test_checkout.py; requirements.txt, config/settings.py, .env.example.

**Interfaces:** `start_checkout(customer, order_id, quote_id) -> CheckoutResult` (redirect_url o quote actualizada para reconfirmar). `create_session(attempt: PaymentAttempt) -> SessionSnapshot`; `retrieve_session(session_id) -> SessionSnapshot`; `expire_session(session_id) -> SessionSnapshot`. SessionSnapshot contiene id, url, status, payment_status, total, currency, livemode, reference, expires_at. API version/SDK fijados tras consultar documentacion oficial.

- [ ] Confirmar contrato actual Stripe: creacion/expiracion (30 minutos), firmas y recuperacion idempotente; fijar version SDK compatible con Python instalado y API version. Registrar version y ejemplos de respuesta en ledger.
- [ ] Escribir tests fallidos: pending/changes/otra cuenta no pagan; total solo servidor; tarifa cambiada devuelve nueva confirmacion sin reserva; doble clic reutiliza intento; timeout conserva reserva y reintenta misma clave/payload; error definitivo libera solo si hay certeza de que no se creo sesion; test key requerida, live rechazada.
- [ ] Ejecutar `.venv/Scripts/python.exe manage.py test payments.tests.test_checkout`; verificar RED.
- [ ] Implementar recotizacion, snapshot inmutable, reserva y payload persistido antes de llamada. Pago unico MXN, tarjetas, expiracion 1800s, sin descuentos ni impuestos automaticos, subtotal historico + envio. Usar idempotency key del intento y payload identico en recuperacion; no recomputar expires_at. URL retorno desde origen configurado, nunca request Host. No retomar creacion desconocida despues de ventana idempotente segura: enviar a reconciliacion manual, mantener reserva.
- [ ] Guardar session id unico y open mediante CAS; si respuesta coincide con intento ya actualizado por webhook, no degradar paid. Si fallo desconocido/DB al guardar, recuperacion por misma clave y referencia; nunca crear una segunda sesion a ciegas. Tests de carrera y cuenta desactivada.
- [ ] Ejecutar tests payments/shipping; commit acotado.

## Task 5: Confirmacion, expiracion y reconciliacion

**Files:** payments/services.py, views.py, urls.py, admin.py, management/commands/reconcile_payments.py; tests/test_webhooks.py, test_reconciliation.py; config/urls.py; orders/admin.py.

**Interfaces:** `reconcile_attempt(attempt_id, *, expire=False) -> PaymentAttempt`; `apply_session_snapshot(attempt_id, snapshot, event_id=None) -> PaymentAttempt`. ProviderEvent guarda event_id unico y processed_at solo tras aplicar efecto. Comando `manage.py reconcile_payments --limit 100`, no bucle infinito.

- [ ] Escribir tests RED: firma incorrecta, payload grande/malformado, livemode, total/moneda/reference equivocada; evento duplicado; webhook antes de persistir session id; estados fuera de orden; paid nunca degrada. Retorno navegador solo no confirma. Sesion expired libera una vez; timeout retiene. Carrera pagar/expirar consulta estado canonico y no marca pagado sin stock consumido.
- [ ] Ejecutar `.venv/Scripts/python.exe manage.py test payments.tests.test_webhooks payments.tests.test_reconciliation`; verificar RED.
- [ ] Implementar endpoint POST webhook exento CSRF pero firmado (raw body, limite de tamano, secret servidor); identificar intento por referencia y verificar sesion/total/entorno via SDK. Aplicar efectos atomicos/evento sin llamadas externas dentro de transaccion. Fallos temporales dejan evento reintentable; mismatches a reconciliation_required con auditoria minima.
- [ ] Implementar comando con resultados sin PII; recuperar creating con misma clave cuando seguro, consultar open y expirar solo tras TTL, conciliar paid/expired. Admin readonly de intentos/reservas/eventos, accion protegida expirar y reconciliar, nunca editar pagado a mano. Permiso payments.reconcile_payment independiente. No implementar reembolsos ni guias.
- [ ] Ejecutar toda suite Django y tests concurrentes de archivo; verificar stock/eventos exactamente una vez; commit acotado.

## Task 6: Checkout responsive y entrega verificable

**Files:** payments/views.py, urls.py, forms.py; orders/urls.py; templates/payments/checkout.html; templates/orders/detail.html, list.html; static/css/orders.css; payments/tests/test_views.py; scripts/check_checkout.cjs; README.md; docs/shipping-checkout-progress.md.

**Interfaces:** mantener name order_payment y ruta /pedido/<uuid>/pago/. GET resumen; POST action quote/select/pay protegido CSRF. Radios con id de cotizacion, nunca importe confiable cliente. Estados revision y pago independientes. customer_required/no-store de cuentas reutilizados.

- [ ] Escribir tests RED de ownership en todas rutas, CSRF, no-store, pedido no aprobado, quote id ajeno, reconfirmacion importe y mensaje de no disponibilidad sin claves. Confirmar que ?success=1 no vuelve paid. No textos de demo/prueba en templates publicos nuevos.
- [ ] Ejecutar `.venv/Scripts/python.exe manage.py test payments.tests.test_views`; verificar RED.
- [ ] Implementar resumen direccion/subtotal/envio/total, radio transportista/servicio y boton Ir al pago. Tras retorno consultar via reconciliacion, mostrar confirmando si aun pendiente; volver desde cancelar no cancela pedido. Formulario funciona sin JS. Usar ui-ux-pro-max para estados/foco y conservar hero y CTA Mis pedidos.
- [ ] Pruebas Playwright en DB aislada: 320,390,844,1440,1920px, teclado, errores, totales largos, reduced motion, sin overflow, doble clic y sin JS. Capturas desktop/movil inspeccionadas. Consultar web-design-guidelines vigente y registrar hallazgos/correcciones. Fakes solo bajo settings de test, nunca una ruta publica de simular pago.
- [ ] Ejecutar `.venv/Scripts/python.exe manage.py test`, `manage.py check`, `manage.py makemigrations --check --dry-run`, `git diff --check`, scripts existentes de cuentas/pedidos/carrito y nuevo check_checkout. Corregir fallos antes de declarar cierre.
- [ ] Respaldar DB principal usando sqlite backup API con nombre nuevo, migrar y aplicar semillas solo autorizadas/provisionales. Verificar no pedidos ficticios ni claves alteradas. Mantener servidor local en 8000, iniciar solo si hace falta.
- [ ] Documentar configuracion de cuentas sandbox, secretos via .env, webhook local y reconciliacion; ejecutar recorrido con Stripe/Envia reales de sandbox cuando haya claves. Si no hay, declarar pendiente esa prueba, no llamar terminado al e-commerce completo. Revision independiente del diff antes de commit/push de implementacion.

## Autorrevision del plan

Cobertura: agrupacion y trazabilidad Task 1; tarifas/cambios Task 2; existencias/revision Task 3; sesion/idempotencia Task 4; confirmacion/expiracion Task 5; interfaz y operacion Task 6. Interfaces compartidas descritas arriba. Las cinco condiciones de Review Focus tienen tests asignados. No se depende de claves para pruebas unitarias, pero si para aceptacion integral sandbox. La compra de guias, politica final de cancelacion y lanzamiento real no se declaran resueltos por este plan.
