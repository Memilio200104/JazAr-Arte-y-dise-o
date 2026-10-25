# Modulo 2: requisitos recibidos

19 de octubre de 2026. Registro de decisiones del usuario; no es una especificacion tecnica aprobada ni activa pagos.

## Confirmado

- Cuenta obligatoria para comprar.
- Existencias iniciales confirmadas: 30 unidades por producto en total, compartidas entre sus tallas/colores; no 30 por variante. Esta decision no modifica aun la base ni implica reponer automaticamente inventario. No confundir stock con capacidad de fabricacion de piezas cotizadas.
- El comprador envia su diseno por WhatsApp al numero del sitio, en PDF o PNG. Jazmin lo revisa y aprueba.
- Cobro mediante API de Stripe a la cuenta de Jazmin. La cuenta y las claves se proporcionaran despues por un canal de configuracion seguro. Integracion inicial exclusivamente en modo pruebas.
- Stripe cobra solamente despues de que Jazmin apruebe el diseno. Enviar un pedido a revision no debe generar un cobro.
- El envio se calcula dinamicamente y se cobra dentro del sitio junto con la compra. No sustituir este flujo por una cotizacion manual por WhatsApp.
- El sitio ofrece unicamente envio. Una posible recogida se acuerda directamente con Jazmin por WhatsApp, fuera del checkout.
- Politica comercial propuesta: cancelacion dentro de las primeras 24 horas desde realizar el pedido y para montos estrictamente menores a 2,000 MXN. No se ha afirmado su suficiencia legal.
- Despliegue a cargo del usuario. El acuerdo previo era terminar ambos modulos antes de desplegar; la incorporacion del Modulo 3 no establece una nueva fecha de despliegue. Gmail y las alertas operativas pasan al Modulo 3 por la aclaracion posterior.

## Modulo 3: alcance solicitado posteriormente

- Jazmin debe poder ver todos los pedidos y registrar su aprobacion despues de revisar el diseno por WhatsApp. La aprobacion registrada en el sitio sera requisito para permitir el pago; un mensaje de WhatsApp no cambia estados automaticamente.
- Cuenta administrativa con permisos para gestionar productos, existencias y usuarios (incluido bloqueo), ademas de pedidos. En Modulo 3 estas operaciones se haran desde una interfaz propia del sitio, sin necesidad de entrar al Django admin. No conceder estos permisos a compradores.
- Avisos por Gmail: nuevos pedidos para Jazmin, aprobacion del diseno, solicitud de cambios y cambios de estado para el cliente, entre otras alertas por especificar.
- Modulo 2: aprobado usar Django Admin para que exclusivamente Jazmin/personal autorizado marque "Diseno revisado y aprobado por Jazmin". Registrar quien aprueba y cuando; el comprador no puede aprobar. El servidor debe impedir el pago sin aprobacion. La interfaz propia con control animado y las notificaciones quedan en Modulo 3.
- La eliminacion de productos con historial de compra requiere conservar las referencias del pedido; proponer archivado en vez de destruir el historial.

## Envios: fuente solicitada

https://jimmygames.store/ consultada el 19 de octubre de 2026. Publica envio nacional gratis para compras mayores a 2,000 MXN, no internacional. Los demas precios son referencias variables por destino, servicio, peso y dimensiones; no hay una tarifa universal que pueda copiarse al checkout.

La aclaracion posterior del usuario prevalece: tarifas dinamicas dentro de la web, sin adoptar la promocion de envio gratis ni habilitar recogida en el checkout.

No copiar direccion, origen postal, embalajes de consolas ni estimaciones de peso de Jimmy Games como datos de JazAr.

### Confirmaciones del 25 de octubre de 2026

- El usuario eligio comenzar con Envia.com. La integracion inicial sera de pruebas; no hay cuenta ni credenciales configuradas todavia.
- Origen proporcionado por el usuario: 2a Privada de Aconitos, numero 729, manzana K7, lote 16, Villa de las Flores, Coacalco, Estado de Mexico, Mexico. Codigo postal confirmado: 55710.
- El origen queda registrado como requisito, no como configuracion operativa ni validacion del domicilio por el proveedor.
- Pendiente obtener pesos y dimensiones de los paquetes ya embalados; no usar valores inventados para cotizaciones reales.
- Autorizado definir empaques, pesos y dimensiones provisionales para desarrollar y probar; Jazmin proporcionara los definitivos antes de activar ventas reales. Propuesta: perfiles editables desde Django Admin.
- Los datos provisionales no deben impedir probar el flujo completo de Stripe en modo pruebas, sin dinero real. Su validacion sera requisito para activar cobros reales, no para las pruebas.
- La interfaz publica de JazAr no mostrara etiquetas de demo ni avisos de prueba. El estado provisional se identificara internamente en administracion; no ocultar los indicadores propios de pruebas de Stripe.
- Stripe Checkout alojado elegido: redirigir a la pagina de Stripe y volver al pedido.
- El usuario aprueba el diseno de envios/pago con esta correccion: agrupar productos compatibles en cajas compartidas por envio, no cotizar automaticamente un paquete por unidad. Se permiten varias cajas cuando capacidad, peso o proteccion lo requieren. Pesos y capacidades provisionales se validaran antes de ventas reales.

## Preguntas abiertas para la especificacion

- Cuenta de pruebas de Envia.com, credenciales, validacion del origen por el proveedor, cobertura, pesos y dimensiones de paquetes. Definir vigencia y recotizacion de tarifas antes del pago.
- Definir inicio de las 24 horas de cancelacion (creacion del pedido o pago posterior a la aprobacion) y base del limite: subtotal de productos o total pagado con envio; procedimiento y monto de reembolso, tratamiento de pedidos ya en produccion.
- Reserva de stock, momento de liberacion y entrega estimada. Las variantes comparten las 30 unidades del producto.
- Verificacion y recuperacion de cuenta durante pruebas sin Gmail real.

Cuentas y solicitudes de pedido implementadas con especificaciones y planes aprobados en docs/superpowers. La revision administrativa no realiza cobros. Envio, reservas y Stripe siguen pendientes de su bloque; el panel propio del sitio y Gmail pertenecen al Modulo 3. La cuenta administrativa local no equivale a una cuenta de comprador.
