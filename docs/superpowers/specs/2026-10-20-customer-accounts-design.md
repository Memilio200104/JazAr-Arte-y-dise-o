# Cuentas de comprador y direcciones

20 de octubre de 2026. Flujo comercial aprobado en conversacion; esta especificacion tecnica queda pendiente de revision del usuario antes del plan de implementacion.

## Objetivo

Conectar las pantallas existentes de cuenta a Django para permitir registro, ingreso, cierre de sesion, recuperacion de contrasena y administracion de direcciones propias. No implementar pedidos, inventario transaccional, envio ni Stripe en este bloque.

## Decisiones del usuario

- Acceso exclusivamente con correo y contrasena, sin nombre de usuario visible ni Google.
- Registro con nombre completo, correo, contrasena y confirmacion.
- La direccion no es obligatoria para registrarse: se puede agregar desde Mi cuenta o al preparar el primer pedido, en el bloque posterior de pedidos.
- Varias direcciones guardadas y una predeterminada.
- El destinatario puede ser distinto del comprador.
- Cada pedido futuro conservara una copia de la direccion usada; editar el perfil no modificara pedidos anteriores.
- Gmail real se configura al final del Modulo 2. No desplegar aun.

## Arquitectura propuesta

Mantener django.contrib.auth, sesiones y el usuario administrativo existente. Agregar una app accounts con CustomerProfile y ShippingAddress; no sustituir AUTH_USER_MODEL ni reiniciar migraciones o base de datos.

CustomerProfile tendra relacion uno-a-uno con el usuario, nombre completo (150 caracteres), correo canonico unico (254 caracteres) y verificacion de correo. El username interno sera un identificador aleatorio opaco, nunca un campo solicitado al comprador. El email del usuario se mantendra sincronizado mediante el servicio de alta. No permitir cambio de correo desde esta primera interfaz.

Una alternativa es cambiar ahora el modelo de usuario: requiere migrar las relaciones de auth/admin y aporta riesgo innecesario. Otra es incorporar un paquete de identidad completo: util para proveedores sociales, pero fuera del alcance confirmado. Recomendacion: componentes nativos de Django y perfiles separados, con responsabilidades acotadas.

Normalizar correo con strip y minusculas, validar con EmailField y aplicar unicidad en base de datos, no solo en formulario. No eliminar puntos ni sufijos con +. Gestionar altas concurrentes en transaccion. No enlazar automaticamente un registro nuevo a usuarios existentes por coincidencia de correo; correos ya usados por el administrador no se convierten en cuentas de comprador.

El ingreso de compradores usara un backend limitado a CustomerProfile, usuario activo y contrasena valida. El administrador conserva su backend y su ruta actuales. Un comprador nunca recibe is_staff o is_superuser. Las vistas de cuenta requieren perfil de comprador ademas de sesion autenticada.

## Flujos

### Registro e ingreso

Reutilizar rutas y estilo actuales. Formularios POST con CSRF, validadores de contrasena de Django y errores junto a los campos. No guardar contrasenas en logs, navegador ni perfil; utilizar set_password y authenticate/login.

Crear perfil y usuario atomicamente. Al registrarse, abrir la cuenta y mostrar el estado de verificacion pendiente. Se puede guardar una direccion sin verificar; el futuro envio de pedidos requerira correo verificado. No considerar que una cuenta esta verificada por registrarse o por estar en DEBUG.

Ingreso con mensaje generico ante correo o contrasena incorrectos. Redirecciones next solo a rutas locales permitidas. Logout exclusivamente POST. Paginas privadas sin cache compartida, ni datos personales en URLs.

### Verificacion y recuperacion

Verificacion mediante enlace firmado, limitado al usuario y al correo vigente, con caducidad de 24 horas y estado que impide reutilizacion. El GET presenta confirmacion; un POST con CSRF completa la verificacion para evitar que un escaner de correo consuma el enlace automaticamente.

Recuperacion mediante vistas/tokens nativos de Django, limitando destinatarios a perfiles de comprador activos. Respuesta generica tanto si existe el correo como si no. El cambio exitoso invalida el token y las sesiones anteriores segun el comportamiento de Django; no iniciar sesion automaticamente.

En local, los correos se generan con el backend de consola existente; los enlaces se consultan en la terminal del servidor, no se muestran en una pagina publica. Probar este flujo con cuentas ficticias. Los tokens son secretos temporales: no copiarlos a documentacion ni Git. El entorno no local utiliza SMTP cuando se configure; no declarar correo entregado si falla el transporte.

### Mi cuenta

Mostrar nombre, correo, estado de verificacion, acceso a direcciones y cierre de sesion. Permitir editar nombre completo. No mostrar pedidos ficticios; indicar estado vacio mientras no exista el modulo de pedidos. El carrito local se conserva, pero todavia no se sincroniza entre dispositivos ni se convierte en pedido.

### Direcciones

ShippingAddress pertenece a CustomerProfile y contiene: destinatario (150), telefono (32), calle (150), numero exterior (20), interior opcional (20), colonia (100), codigo postal (5), municipio/alcaldia (100), estado (100), referencias opcionales (300) y etiqueta opcional (40). Pais inicial Mexico, explicito en pantalla; no implica haber confirmado cobertura de paqueterias.

Codigo postal con cinco digitos; telefono acepta formato habitual con +, espacios y guiones, valida longitud de digitos sin afirmar que el numero existe. Campos requeridos con limites de longitud y normalizacion de espacios. No inventar validacion geografia/paqueteria: se integrara con el proveedor elegido despues.

El perfil apunta a una direccion predeterminada propia, evitando multiples flags simultaneos. La primera direccion se vuelve predeterminada; crear otra no reemplaza la eleccion sin accion expresa. Si se elimina la predeterminada, elegir la mas antigua restante, o ninguna si no quedan. Modificaciones de predeterminada con transaccion y control de propiedad.

Listar, crear, editar y eliminar solo direcciones del usuario autenticado. Obtener una direccion ajena por id devuelve 404 sin revelar datos. Eliminacion con pantalla de confirmacion y POST. No almacenar direcciones en localStorage. Formularios conservan datos validos cuando hay errores.

## Protecciones y errores

Limites de intentos con almacenamiento compartido entre workers para ingreso (por IP y correo), registro (por IP), recuperacion y reenvio (por IP y correo). No usar bloqueos permanentes de cuenta. Claves derivadas con HMAC, sin email/IP en nombres de archivos o mensajes. Definir valores y limpieza en el plan; responder 429 con Retry-After sin revelar si existe el usuario. No confiar en X-Forwarded-For salvo proxy expresamente configurado.

Un fallo al enviar correo deja la cuenta sin verificar y permite reintento limitado; no pierde direcciones ni habilita compras. Si falla persistencia, mostrar error recuperable sin detalles internos. Capturar excepciones esperadas, no silenciar fallos generales.

Respaldar SQLite antes de aplicar migraciones locales. No cambiar contrasena ni permisos de jazar_admin, ni sobrescribir ediciones del catalogo.

## UI y pruebas

Conservar fondo original del hero, tipografia, colores y navegacion existentes. Activar solo formularios realmente conectados. Mantener etiquetas, autocomplete, foco visible, errores asociados, mensajes de estado y confirmacion de eliminacion. Aplicar ui-ux-pro-max y revisar web-design-guidelines antes de cerrar.

Pruebas: registro y normalizacion, unicidad concurrente, contrasenas invalidas, autenticacion y logout/CSRF, next externo rechazado, perfiles privados, direccion ajena 404, cambios de predeterminada y eliminacion, tokens expirados/reutilizados, recuperacion generica, aislamiento de admin, limites y fallo de correo. Pruebas SMTP con backend locmem, no envio real.

Navegador: registro con usuario ficticio, ingreso, editar nombre, direcciones, errores, logout; movil 320/390, panel 844 y escritorio 1440/1920. Comprobar teclado y no regresion de tienda, hero y proceso. No guardar credenciales de pruebas en artefactos.

## Fuera de alcance

Google/social login, cambiar correo, borrar cuenta, pagos, tarifas, pedidos y sus cancelaciones, reservas de stock, aplicacion de existencias iniciales, backend del carrito y despliegue. La copia inmutable de direccion se implementara con Order en el siguiente bloque, no mediante tablas de pedidos vacias en esta etapa.

## Aprobacion

Tras revisar esta especificacion, crear el plan concreto con pruebas y migraciones. Se conserva la preferencia del usuario por ejecucion directa en la carpeta y rama actuales; no crear otro worktree ni pedir de nuevo esa eleccion.
