# Modulo 2: requisitos recibidos

19 de octubre de 2026. Registro de decisiones del usuario; no es una especificacion tecnica aprobada ni activa pagos.

## Confirmado

- Cuenta obligatoria para comprar.
- Existencias iniciales indicadas por el usuario: 30 de todo. Definir por SKU/variante en la especificacion antes de reservar inventario; no confundir stock con capacidad de fabricacion de piezas cotizadas.
- El comprador envia su diseno por WhatsApp al numero del sitio, en PDF o PNG. Jazmin lo revisa y aprueba.
- Cobro mediante API de Stripe a la cuenta de Jazmin. La cuenta y las claves se proporcionaran despues por un canal de configuracion seguro. Integracion inicial exclusivamente en modo pruebas.
- Politica comercial propuesta: cancelacion dentro de las primeras 24 horas desde realizar el pedido y para montos estrictamente menores a 2,000 MXN. No se ha afirmado su suficiencia legal.
- Despliegue a cargo del usuario, despues de terminar ambos modulos. Gmail real se configura al final del Modulo 2.

## Envios: fuente solicitada

https://jimmygames.store/ consultada el 19 de octubre de 2026. Publica envio nacional gratis para compras mayores a 2,000 MXN, no internacional. Los demas precios son referencias variables por destino, servicio, peso y dimensiones; no hay una tarifa universal que pueda copiarse al checkout.

No copiar direccion, origen postal, embalajes de consolas ni estimaciones de peso de Jimmy Games como datos de JazAr. Pendiente confirmar recogida, domicilio de JazAr y cotizacion del envio antes del pago.

## Preguntas abiertas para la especificacion

- Cobro al crear el pedido o despues de aprobar diseno y costo de envio.
- Confirmar promocion nacional, costo/domicilio de recogida y cobertura de envios.
- Definir base del limite de cancelacion: subtotal de productos o total pagado con envio; procedimiento y monto de reembolso, tratamiento de pedidos ya en produccion.
- Variantes que comparten existencias, reserva de stock, momento de liberacion y entrega estimada.
- Verificacion y recuperacion de cuenta durante pruebas sin Gmail real.

No crear rutas transaccionales hasta revisar la especificacion y el plan del Modulo 2. La cuenta administrativa local no equivale a una cuenta de comprador.
