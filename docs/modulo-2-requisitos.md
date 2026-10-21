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

No copiar direccion, origen postal, embalajes de consolas ni estimaciones de peso de Jimmy Games como datos de JazAr. Hace falta seleccionar el proveedor/API de tarifas y obtener el origen de los envios y los pesos y dimensiones de los paquetes.

## Preguntas abiertas para la especificacion

- Proveedor/API de envio, cuenta comercial, domicilio y codigo postal de origen, cobertura, pesos y dimensiones de paquetes. Definir vigencia y recotizacion de tarifas antes del pago.
- Definir inicio de las 24 horas de cancelacion (creacion del pedido o pago posterior a la aprobacion) y base del limite: subtotal de productos o total pagado con envio; procedimiento y monto de reembolso, tratamiento de pedidos ya en produccion.
- Reserva de stock, momento de liberacion y entrega estimada. Las variantes comparten las 30 unidades del producto.
- Verificacion y recuperacion de cuenta durante pruebas sin Gmail real.

Frontend aprobado e implementado por separado: paginas GET de lectura y seleccion local, sin rutas transaccionales. Especificacion y plan en docs/superpowers. El backend sigue pendiente de su especificacion. La cuenta administrativa local no equivale a una cuenta de comprador.
