# Modulo 2: requisitos recibidos

19 de octubre de 2026. Registro de decisiones del usuario; no es una especificacion tecnica aprobada ni activa pagos.

## Confirmado

- Cuenta obligatoria para comprar.
- Existencias iniciales indicadas por el usuario: 30 de todo. Definir por SKU/variante en la especificacion antes de reservar inventario; no confundir stock con capacidad de fabricacion de piezas cotizadas.
- El comprador envia su diseno por WhatsApp al numero del sitio, en PDF o PNG. Jazmin lo revisa y aprueba.
- Cobro mediante API de Stripe a la cuenta de Jazmin. La cuenta y las claves se proporcionaran despues por un canal de configuracion seguro. Integracion inicial exclusivamente en modo pruebas.
- Stripe cobra solamente despues de que Jazmin apruebe el diseno. Enviar un pedido a revision no debe generar un cobro.
- El envio se calcula dinamicamente y se cobra dentro del sitio junto con la compra. No sustituir este flujo por una cotizacion manual por WhatsApp.
- El sitio ofrece unicamente envio. Una posible recogida se acuerda directamente con Jazmin por WhatsApp, fuera del checkout.
- Politica comercial propuesta: cancelacion dentro de las primeras 24 horas desde realizar el pedido y para montos estrictamente menores a 2,000 MXN. No se ha afirmado su suficiencia legal.
- Despliegue a cargo del usuario, despues de terminar ambos modulos. Gmail real se configura al final del Modulo 2.

## Envios: fuente solicitada

https://jimmygames.store/ consultada el 19 de octubre de 2026. Publica envio nacional gratis para compras mayores a 2,000 MXN, no internacional. Los demas precios son referencias variables por destino, servicio, peso y dimensiones; no hay una tarifa universal que pueda copiarse al checkout.

La aclaracion posterior del usuario prevalece: tarifas dinamicas dentro de la web, sin adoptar la promocion de envio gratis ni habilitar recogida en el checkout.

No copiar direccion, origen postal, embalajes de consolas ni estimaciones de peso de Jimmy Games como datos de JazAr. Hace falta seleccionar el proveedor/API de tarifas y obtener el origen de los envios y los pesos y dimensiones de los paquetes.

## Preguntas abiertas para la especificacion

- Proveedor/API de envio, cuenta comercial, domicilio y codigo postal de origen, cobertura, pesos y dimensiones de paquetes. Definir vigencia y recotizacion de tarifas antes del pago.
- Definir inicio de las 24 horas de cancelacion (creacion del pedido o pago posterior a la aprobacion) y base del limite: subtotal de productos o total pagado con envio; procedimiento y monto de reembolso, tratamiento de pedidos ya en produccion.
- Variantes que comparten existencias, reserva de stock, momento de liberacion y entrega estimada.
- Verificacion y recuperacion de cuenta durante pruebas sin Gmail real.

No crear rutas transaccionales hasta revisar la especificacion y el plan del Modulo 2. La cuenta administrativa local no equivale a una cuenta de comprador.
