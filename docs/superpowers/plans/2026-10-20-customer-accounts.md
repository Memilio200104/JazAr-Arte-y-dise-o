# Customer Accounts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax for tracking. Direct execution in the existing checkout is already selected.

**Goal:** Activar cuentas de comprador y direcciones privadas sobre las pantallas actuales.

**Architecture:** Nueva app accounts sobre django.contrib.auth, sin cambiar AUTH_USER_MODEL. Servicios transaccionales para perfiles/direcciones; vistas y formularios separados de las pantallas comerciales no conectadas. Sin pedidos, cobros ni envio.

**Tech Stack:** Django 5.2 existente, SQLite, templates, CSS y JavaScript actuales, unittest y Playwright. Sin proveedor externo de identidad.

**Spec:** `docs/superpowers/specs/2026-10-20-customer-accounts-design.md`, aprobada por el usuario.

## Global Constraints

- Correo y contrasena; nombre completo al registrarse, direcciones opcionales inicialmente.
- Mantener administrador y catalogo existentes, sin reiniciar migraciones.
- Contrasenas exclusivamente mediante Django; ninguna credencial o direccion en localStorage.
- Comprador sin privilegios administrativos; todas las direcciones limitadas al propietario.
- Gmail real diferido. Usar consola en local y locmem en tests, sin afirmar entrega real.
- Correo pendiente de verificacion no impide guardar direcciones; pedidos futuros requeriran verificacion.
- No implementar Order, Stripe, stock transaccional, transportistas ni despliegue.
- Hero original intacto. Revisar interfaz con ui-ux-pro-max y web-design-guidelines.
- Respaldo local de SQLite antes de migrar; no guardar respaldo en Git.

## Review Focus

- Altas concurrentes con correo equivalente: una sola identidad y ningun usuario huerfano (tarea 1).
- Identificador ajeno o usuario admin sin perfil: no mostrar/modificar datos de comprador (tareas 2 y 4).
- Enlace expirado, consumido o abierto por escaner: no verificar ni restablecer sin el flujo correcto (tarea 3).
- Redireccion next externa o POST sin CSRF: bloquear, sin fuga de sesion (tarea 2).
- SMTP y almacenamiento de limites fallan: error recuperable sin confirmar entrega ni saltarse protecciones (tareas 2 y 3).

## Archivos y contratos

- `accounts/models.py`: CustomerProfile, ShippingAddress, AuthAttemptBucket.
- `accounts/services.py`: altas, normalizacion y operaciones atomicas de direccion.
- `accounts/backends.py`: CustomerEmailBackend, limitado a usuarios con perfil activo.
- `accounts/forms.py`: registro, ingreso, nombre, direccion y recuperacion acotada a compradores.
- `accounts/views.py`, `accounts/urls.py`: HTTP, permisos y redirecciones.
- `accounts/tokens.py`, `accounts/mail.py`: verificacion firmada y correo; recuperar contrasena reutiliza tokens/vistas Django.
- `accounts/limits.py`: limites por IP y correo con claves HMAC y persistencia SQLite.
- `templates/accounts/`: formularios y correos, extendiendo store/base.html.
- `accounts/tests/`: test_models, test_auth, test_addresses, test_email y test_limits.
- `scripts/check_accounts.cjs`: pruebas de navegador con datos ficticios en base temporal.
- Modificar `config/settings.py`, `website/urls.py`, `templates/includes/site_header.html`, CSS de tienda y pruebas antiguas afectadas; no mezclar logica de cuentas en store_views.

### Task 1: perfiles y persistencia

**Interfaces:** `normalize_email(value: str) -> str`; `register_customer(full_name, email, password) -> CustomerProfile`; `CustomerProfile.user` OneToOne, `email` unico normalizado, `full_name` max150, `email_verified_at` nullable, `default_address` FK nullable SET_NULL. ShippingAddress FK customer y campos/longitudes de la especificacion. AuthAttemptBucket: key HMAC unico, started_at y count.

- [ ] Escribir tests: normalize_email(' A+tag@EXAMPLE.COM ') == 'a+tag@example.com'; alta crea un usuario con check_password=True y ambos privilegios False; correo equivalente falla sin aumentar conteo de usuarios; correo administrativo no se apropia; direccion no es obligatoria.
- [ ] Ejecutar `.venv/Scripts/python.exe manage.py test accounts.tests.test_models --noinput`; observar RED antes de implementar.
- [ ] Crear app, modelos, servicio atomico y migraciones. Username interno uuid aleatorio, perfil y usuario en la misma transaccion. Unicidad de email canonico en base; atrapar IntegrityError fuera del bloque atomic. No permitir editar correo del perfil por admin sin servicio sincronizador: campos email/user de solo lectura.
- [ ] Probar con TransactionTestCase altas concurrentes sobre base de prueba de archivo: exactamente un perfil y ningun usuario huerfano; manejar contencion SQLite con respuesta reintentable, no un 500 silencioso.
- [ ] Ejecutar pruebas GREEN; respaldar runtime/db.sqlite3 con sqlite backup API mediante manage.py shell; migrar y comprobar que catalogo y admin conservan sus conteos y permisos sin imprimir datos personales.
- [ ] Commit: `feat: add customer profiles and shipping address persistence`.

### Task 2: registro, ingreso y cuenta privada

**Interfaces:** CustomerEmailBackend.authenticate(request, email=None, password=None, **kwargs); `consume_limits(action, ip, email='') -> (allowed: bool, retry_after: int)`. Ventana 900 segundos: login 30/IP y 10/correo; registro 5/IP; recovery 10/IP y 3/correo; verify 10/IP y 3/correo. HMAC con SECRET_KEY y separacion por accion. Aplicar a intentos, no solo fallos.

- [ ] Tests RED de registro/ingreso, usuario inactivo, perfil ausente, logout POST, POST CSRF, next=https://example.org rechazado, nombres escapados y cuenta ajena no accesible. Tests de limite con reloj controlado: intento N permitido, N+1 devuelve 429, Retry-After positivo, ventana expirada permite, fallo de persistencia devuelve 503.
- [ ] Crear forms basados en validadores Django, backend y vistas para rutas existentes de ingreso/registro/cuenta. Backend administrativo se mantiene; el formulario de comprador verifica perfil incluso si otro backend pudiera autenticar. Registro no acepta flags de privilegio del cliente. Mantener tiempo de hash razonablemente uniforme para correo inexistente.
- [ ] Implementar limites con actualizacion atomica condicional de contador; colisiones de creacion manejadas sin perder incrementos. Limpiar buckets anteriores a 24 horas mediante comando `prune_auth_limits`; documentar ejecucion diaria futura. No reutilizar el limite de contacto ni aceptar cabeceras proxy sin configuracion expresa.
- [ ] Formularios Django POST con errores de campo, foco en resumen, mensajes genericos y campos password nunca repoblados. Cuenta muestra nombre editable y correo solo lectura; logout CSRF. Redirecciones next solo rutas relativas locales, sin esquemas ni doble barra.
- [ ] Marcar paginas privadas no-store. Reemplazar rutas GET-only de cuenta en website/urls.py por accounts.urls; conservar tienda y pagos inactivos. Actualizar test_store para el nuevo contrato, no borrar sus comprobaciones de ausencia de pagos.
- [ ] Ejecutar tests accounts y suite completa GREEN; commit `feat: connect customer registration and email login`.

### Task 3: verificacion y recuperacion

**Interfaces:** `make_verification_token(profile) -> str`, `verify_email(profile, token) -> bool` con TimestampSigner y salt propio, pk/email y marca de version ligada al estado. TTL 86400 segundos. Enlace GET solo presenta formulario; POST CSRF valida y establece verified_at una vez. Password reset nativo, PASSWORD_RESET_TIMEOUT=86400.

- [ ] Tests RED con locmem: correo generado, cuenta pendiente, GET no verifica, POST verifica, enlace expirado/reutilizado/correo distinto falla; reset para desconocido muestra la misma respuesta, admin sin perfil no recibe reset de comprador; token consumido no sirve, sesiones antiguas quedan invalidadas tras cambio.
- [ ] Implementar correo de verificacion, reenvio limitado y templates de email con enlaces construidos desde origen configurado seguro, nunca desde un next del cliente. En local permitir origen http://127.0.0.1:8000; produccion exige origen HTTPS configurado. No incluir tokens en respuestas HTML de diagnostico.
- [ ] Adaptar PasswordResetForm.get_users para perfiles activos y correo canonico; reutilizar vistas/tokens de Django con templates de JazAr y CSRF. No iniciar sesion automaticamente tras reset.
- [ ] Ante fallo de correo mantener cuenta pendiente y permitir reenvio; errores genericos no exponen existencia de destinatarios. En consola no afirmar correo entregado. No tocar credenciales SMTP ni activar Gmail.
- [ ] Ejecutar tests GREEN incluyendo fallo de transporte y limites; commit `feat: add email verification and password recovery`.

### Task 4: direcciones guardadas

**Interfaces:** `save_address(customer, cleaned_data, address_id=None) -> ShippingAddress`; `set_default_address(customer, address_id) -> None`; `delete_address(customer, address_id) -> None`. Todas limitan queryset al customer y usan transacciones. Primera direccion predeterminada; eliminar predeterminada elige menor pk restante.

- [ ] Tests RED: comprador A no lee/edita/elimina direccion B; primer alta predeterminada, segunda no reemplaza, cambio explicito funciona, borrar predeterminada elige restante y ultima deja null; CSRF y GET nunca eliminan; codigo postal '01234' conserva cero y '1234' falla.
- [ ] Crear rutas `/cuenta/direcciones/`, `nueva/`, `<int:pk>/editar/`, `<int:pk>/eliminar/`, `<int:pk>/predeterminada/`. Decorador de comprador para todas; admin sin perfil no accede como cliente. Eliminacion con confirmacion GET y accion POST.
- [ ] Formulario con destinatario, telefono, calle/numeros, colonia, CP, municipio, estado, referencias y etiqueta; pais Mexico visible. Telefono valida 10 a 15 digitos permitiendo +, espacios, guiones y parentesis. No afirmar direccion validada por transportista.
- [ ] Templates con etiquetas/autocomplete, errores, estado vacio, direccion predeterminada identificada en texto, acciones accesibles y retorno a cuenta. Nada de direcciones en localStorage.
- [ ] Tests GREEN y commit `feat: add private customer address book`.

### Task 5: integracion y cierre

- [ ] Crear check_accounts.cjs sobre servidor con base temporal y email locmem/consola: alta ficticia, ingreso, editar nombre, crear dos direcciones, predeterminada, eliminar, logout, recuperar y validar errores. No usar cuentas del propietario ni modificar datos reales; cerrar servidor temporal al terminar.
- [ ] Pruebas de navegador en 320,390,844,1440,1920: sin overflow, teclado/foco, errores, fotos y encabezado. Revisar capturas y corregir regresiones con pruebas antes de cambios.
- [ ] Revisar con ui-ux-pro-max y web-design-guidelines vigentes. Mantener hero original y CTA de pago deshabilitado; sin pedidos simulados.
- [ ] Ejecutar suite Django completa, pruebas Node de carrito y scripts check_store/check_browser/check_process/check_hero/check_errors. Ajustar check_store: paginas de cuenta anonima redirigen a ingreso; no esperar ausencia de endpoints POST ahora autorizados.
- [ ] Ejecutar manage.py check, makemigrations --check --dry-run y git diff --check. Obtener revision independiente final segun executing-plans; corregir hallazgos importantes con RED/GREEN.
- [ ] Actualizar README y estado del Modulo 2 con rutas, pruebas, limite de Gmail y comando de limpieza. Commit `test: verify customer account and address workflows`. No fusionar ni desplegar; push en rama existente tras verificacion.

## Handoff

Plan pendiente de revision del usuario. Metodo ya elegido: ejecucion directa en la carpeta actual, con revision independiente al final. No volver a preguntar por metodo ni worktree.
