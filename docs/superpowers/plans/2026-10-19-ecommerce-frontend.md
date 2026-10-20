# Ecommerce Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir el recorrido visual de tienda sobre el catalogo real, sin activar transacciones.

**Architecture:** Templates Django con vistas GET de lectura y componentes compartidos. Seleccion local en JavaScript, separada de autenticacion, pedidos y pagos pendientes. Paginas de revision de estados disponibles exclusivamente con DEBUG.

**Tech Stack:** Django existente, CSS, JavaScript nativo, Lucide, GSAP existente, unittest Django y Playwright.

**Spec:** `docs/superpowers/specs/2026-10-19-ecommerce-frontend-design.md`, aprobada por el usuario.

## Global Constraints

- No crear cuentas, pedidos, reservas, cotizaciones de transporte, cobros ni reembolsos.
- Precio fijo abre detalle; cotizacion conserva contacto.
- Cuenta obligatoria para comprar cuando se conecte el backend.
- Stripe cobra despues de aprobar Jazmin el diseno enviado por WhatsApp.
- Envio dinamico cobrado dentro de la web; sin recogida ni envio gratis supuesto.
- localStorage guarda solamente identificadores y cantidades, nunca credenciales ni datos personales.
- Conservar identidad actual, reduced-motion, teclado y objetivos tactiles de al menos 44 px.
- Quitar etiquetas publicas de demo sin fingir disponibilidad de integraciones.
- No desplegar, configurar Gmail ni modificar stock en esta entrega.
- Leer skills obligatorias al ejecutar; aislar trabajo segun using-git-worktrees antes de implementar.

## Review Focus

- localStorage bloqueado o JSON malformado: seleccion en memoria y mensaje recuperable, sin pagina rota (tarea 2).
- Producto retirado o convertido a cotizacion tras guardarlo: excluirlo y avisar (tarea 2).
- URL directa y POST en pantallas sin backend: ningun efecto ni exito ficticio; fixtures inaccesibles con DEBUG=False (tarea 3).
- Vista estrecha, altura reducida y zoom: encabezado, dialogo y resumen no ocultan controles (tarea 5).
- Texto del catalogo con caracteres HTML o URL maliciosa en almacenamiento: render seguro sin innerHTML con datos del usuario (tareas 1 y 2).

## Mapa de archivos

- `website/store_views.py`: vistas GET de producto, carrito y pantallas comerciales.
- `website/store_presenters.py`: elegibilidad y datos publicos serializables; sin logica transaccional.
- `website/urls.py`: rutas nombradas.
- `templates/store/`: base comercial, detalle, carrito, cuenta, solicitud, pago y revision de estados.
- `templates/includes/site_header.html`: encabezado compartido con anclas absolutas a portada.
- `static/css/store.css`: estilos comerciales acotados; `static/js/store.js`: interacciones DOM.
- `static/js/cart-state.js`: funciones puras para normalizar seleccion y calcular subtotal en centavos.
- `website/test_store.py`, `scripts/test_cart_state.cjs`, `scripts/check_store.cjs`: pruebas.
- `templates/website/home.html`, `templates/includes/product.html`: enlaces y limpieza publica.
- `README.md`, `docs/modulo-2-requisitos.md`: estado real de entrega.

### Tarea 1: detalle real y navegacion compartida

**Interfaces:** `eligible_products() -> QuerySet[Product]` filtra activo, no concepto, fixed y precio no nulo. `product_detail(request, slug) -> HttpResponse` usa ese queryset; nombre de URL `product_detail`. `store_context() -> dict` aporta SiteContent y catalogo publico. No modifica modelos.

- [ ] Crear `website/test_store.py`: `test_fixed_product_detail` verifica 200, precio MXN, nombre escapado e imagen; `test_ineligible_detail_404` cubre inactivo, concepto, quote y sin precio. `test_catalog_links` verifica detalle para fixed y contacto para quote.
- [ ] Ejecutar `.venv/Scripts/python.exe manage.py test website.test_store --noinput`; confirmar fallos por rutas inexistentes.
- [ ] Implementar interfaces en presenters/views, ruta `/productos/<slug>/`, template `templates/store/product_detail.html` y `templates/store/base.html`. Mostrar nota comercial y cantidad; deshabilitar agregar con stock conocido cero. No generar variantes.
- [ ] Extraer encabezado a `templates/includes/site_header.html`, reutilizar en portada y tienda; agregar accesos carrito/cuenta y anclas `{% url 'home' %}#catalogo`. Actualizar enlaces de fichas elegibles sin alterar cotizacion.
- [ ] Crear `store.css` y ampliacion de imagen mediante dialog accesible en `store.js`, cierre Escape y retorno del foco. Reutilizar Lucide local y menu existente sin inicializar animaciones de portada en tienda.
- [ ] Ejecutar pruebas nuevas y existentes; comprobar sin JavaScript que detalle y contacto son legibles.
- [ ] Commit: `feat: add real product detail and shared store navigation`.

### Tarea 2: carrito local recuperable

**Interfaces:** presenters publica lista `{id, name, url, image_url, price_minor, currency, stock}` en `json_script`, siempre desde eligible_products. Precio Decimal convertido a centavos enteros. `normalizeCart(raw, products) -> {items, notices}`, con items `{id, quantity}` unicos. `subtotalMinor(items, products) -> integer`. Exportar funciones para Node y navegador sin dependencias nuevas. Clave local `jazar.cart.v1`.

- [ ] Crear `scripts/test_cart_state.cjs` con node:assert: corrupto produce vacio; id desconocido se elimina; cantidades fraccionarias/negativas/no finitas se rechazan; duplicados se consolidan; cantidad maxima es min(stock,99) si stock conocido y 99 si desconocido; cero stock excluye; dos piezas de 19990 centavos suman 39980; precio guardado adulterado se ignora.
- [ ] Ejecutar `node scripts/test_cart_state.cjs`; confirmar fallo por modulo ausente.
- [ ] Implementar cart-state.js y pruebas hasta PASS. No persistir nombres, precios ni direcciones.
- [ ] Implementar `cart(request) -> HttpResponse`, ruta `/carrito/` nombre `cart`, template `cart.html`. Renderizar nombres con textContent y URLs desde datos del servidor; contador accesible, vacio, subtotal, editar/eliminar y CTA hacia ingreso. Envio pendiente, no total definitivo.
- [ ] Conectar agregar desde detalle, cargar/guardar con try/catch y fallback en memoria. Escuchar evento storage para otra pestana y reconciliar contra catalogo actual al cargar. Mostrar aviso si productos dejan de ser elegibles.
- [ ] Crear `check_store.cjs`: assert agregar/recargar/cambiar/eliminar/vacio; localStorage corrupto y bloqueado no rompen; texto HTML se muestra literal; sin JS se conserva contacto. Ejecutar contra servidor local y confirmar PASS.
- [ ] Commit: `feat: add browser-local shopping selection`.

### Tarea 3: pantallas de cuenta, solicitud y pago

**Interfaces:** vistas GET `sign_in`, `register`, `recover`, `account`, `order_request`, `payment`, `store_review`; nombres de ruta equivalentes. URLs segun especificacion. `store_review` retorna 404 si settings.DEBUG=False, incluso con URLs ya cargadas.

- [ ] Ampliar test_store: `test_store_pages_are_get_only` verifica GET 200 y POST 405 sin creacion de usuarios; `test_review_hidden_in_production` verifica 404 con DEBUG=False; `test_payment_has_no_card_fields` verifica ausencia de inputs de tarjeta y accion de pago habilitada.
- [ ] Ejecutar pruebas y confirmar fallos antes de implementar.
- [ ] Crear templates `sign_in.html`, `register.html`, `recover.html`, `account.html`, `order_request.html`, `payment.html`, `review.html` y rutas. Campos con labels/tipos/autocomplete correctos, formularios sin envio operativo ni captura/persistencia de credenciales. Acciones definitivas deshabilitadas con texto especifico.
- [ ] Solicitud muestra resumen local y direccion no persistida; WhatsApp sin numero de pedido ficticio. Pago muestra bloqueo por aprobacion y envio pendiente. Cuenta sin sesion no muestra usuario inventado.
- [ ] Review usa fixtures en memoria rotulados como ejemplos para estados revision, cambios, aprobado y pendiente de pago; solo en pagina de revision, sin banderas URL que desbloqueen paginas publicas.
- [ ] Probar que teclado y Enter no envian formularios; no hay solicitudes POST ni exito ficticio; atributos disabled y mensajes visibles. Ejecutar suite Django y check_store.
- [ ] Commit: `feat: add account and order interface states without transactions`.

### Tarea 4: presentacion publica sin etiquetas de demo

**Interfaces:** conservar contrato de contact existente y estado local firmado; reemplazar copy publico sin confundir envio local con entrega de correo.

- [ ] Agregar pruebas que aseguren portada sin texto "Demo local" y sin fallback hero-concept, pero con aviso de correo no disponible cuando CONTACT_LOCAL_MODE=True. Confirmacion local no contiene "enviado" ni afirma recepcion por Jazmin.
- [ ] Ejecutar pruebas, confirmar fallo.
- [ ] Inspeccionar `static/images/client/taller.webp` y elegir encuadre legible como fallback real de portada; preservar hero_photo editada por cliente. Actualizar alt y retirar nota conceptual solo al reemplazar imagen.
- [ ] Sustituir aviso de demo por disponibilidad real del correo y contacto WhatsApp. Conservar validaciones, rate limit y ausencia de envio SMTP real. Revisar copys publicos con rg, sin renombrar migraciones, historial ni comandos de compatibilidad.
- [ ] Actualizar pruebas de contacto cuyos textos cambien; ejecutar suite completa.
- [ ] Commit: `fix: replace demo presentation with honest public availability`.

### Tarea 5: verificacion responsive, movimiento y regresiones

**Interfaces:** check_store.cjs reutiliza URL local configurable mediante BASE_URL, por defecto http://127.0.0.1:8000; screenshots en artifacts, fuera de Git.

- [ ] Ampliar check_store para anchos 320,390,768,844,1024,1440,1920 con alturas 600 y 900; assert scrollWidth<=innerWidth, imagenes decodificadas, controles visibles y consola sin errores.
- [ ] Agregar pruebas foco del dialogo, menu Escape, reduced-motion, zoom de texto 200%, resumen largo y contador de dos cifras; confirmar fallos observados antes de corregir.
- [ ] Ajustar solo estilos/componentes responsables, con tracks minmax(0,1fr), dimensiones estables y sin tipografia dependiente de vw. Revisar capturas desktop/movil visualmente, no solo assertions.
- [ ] Leer ui-ux-pro-max vigente y consultar aspectos puntuales; obtener Web Interface Guidelines vigentes y auditar templates/CSS/JS cambiados. Guardar hallazgos y resolucion en `docs/ecommerce-frontend-verificacion.md`.
- [ ] Ejecutar `.venv/Scripts/python.exe manage.py test --noinput`, `node scripts/test_cart_state.cjs`, `node scripts/check_store.cjs` y scripts existentes check_browser, check_client_catalog, check_process, check_hero, check_errors con sus requisitos documentados. NODE_PATH usa runtime instalado, sin instalar dependencias a ciegas.
- [ ] Ejecutar `git diff --check`, revisar diff y documentar resultados reales. Actualizar README y requisitos con limites vigentes; solicitar revision independiente del cambio completo segun skill.
- [ ] Commit: `test: verify responsive storefront and document integration boundaries`.

## Entrega

Mantener servidor local disponible y comunicar URL, rutas y pruebas verificadas. Si el puerto 8000 esta ocupado por otro proceso, no detenerlo sin identificarlo; usar otro puerto. No publicar ni activar cobros. Push de la rama de trabajo solo tras verificar, sin sobrescribir main/master.

El plan requiere revision del usuario y eleccion de ejecucion: directa en esta sesion o mediante subagentes por tarea. Recomendacion: directa, porque templates, estado local y pruebas comparten contratos y no hay integraciones transaccionales en esta entrega.
