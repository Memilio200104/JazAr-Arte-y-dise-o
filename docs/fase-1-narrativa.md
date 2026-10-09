# JazAr Arte y Diseño: narrativa y contenidos de fase 1

Estado: propuesta conceptual para revisión. No constituye una promesa comercial aprobada ni una implementación del sitio.

## Brief y alcance

JazAr Arte y Diseño, de Jazmin Zarate, vende prendas, regalos y textiles personalizados mediante sublimación, DTF, impresión 3D y personalización general. El sitio debe presentar su trabajo con alto impacto visual y convertir interés en consultas de proyectos. Su diferenciador propuesto es el criterio de una diseñadora gráfica aplicado a objetos reales: composición, color, legibilidad y elección de técnica.

El encargo corresponde a un proyecto arquitectónico nuevo. Esta fase entrega narrativa, textos y estructura conceptual; el usuario ya solicitó esos documentos. Las decisiones finales de marca, promesas comerciales y fotografías se validarán antes de publicar el sitio.

Requisitos preservados: hero con Jazmin, catálogo, paquetes y promociones, proceso creativo y contacto; identidad compatible con Facebook; calidad visual inspirada en Apple AirPods, Noomo, Lusion y Moooi; interacción y animación por scroll; experiencia responsiva. La implementación utilizará Django, Docker Compose, Nginx, Gunicorn y Certbot. El contacto se enviará con Django por SMTP a Gmail, sin automatizadores externos. Las imágenes de alta calidad llegarán después.

Referencia de marca observada en la captura de Facebook proporcionada por el usuario: logotipo de apariencia volumétrica en cian eléctrico y azul, acentos magenta y amarillo neón sobre un fondo de ladrillo morado. Su texto público dice: "Te ofrecemos productos personalizados para hacer regalos creativos para tu familia y amigos." Esta evidencia respalda una narrativa cercana alrededor de los regalos y una identidad gráfica expresiva; la captura no sustituye los archivos originales del logo para producción.

Supuestos de trabajo: la conversión principal será una solicitud de cotización, no un pago en línea. Los regalos para familia y amigos están respaldados por la comunicación actual visible en la captura. Las piezas para marcas, equipos o eventos son una ampliación comercial propuesta, no una afirmación sobre la clientela actual. No se suponen existencias, cobertura geográfica, tiempos, mínimos de compra ni rangos de precio.

## Tres enfoques posibles

| Enfoque | Relato | Ventaja | Riesgo |
| --- | --- | --- | --- |
| Diseño con intención, recomendado | Una idea toma forma mediante decisiones de una diseñadora gráfica. | Hace visible el valor de Jazmin y conecta todas las técnicas en un mismo negocio. | Requiere mostrar proyectos reales y explicar decisiones concretas. |
| Regalos que cuentan algo | Una persona, una ocasión y una pieza que expresa un vínculo. | Tiene cercanía emocional y funciona para regalos. | Puede reducir la percepción del trabajo para marcas y equipos. |
| Taller de posibilidades | Un recorrido de materiales, técnicas y transformaciones. | Da espacio a la impresión 3D y a una interacción visual ambiciosa. | La tecnología puede desplazar el protagonismo del diseño y confundir al comprador. |

Recomendación: utilizar Diseño con intención como hilo central; incorporar la emoción en los ejemplos de regalos y las técnicas como respuesta a una necesidad. El visitante debe poder identificar qué puede encargar sin conocer la diferencia entre sublimación y DTF.

## Narrativa del recorrido

1. Reconocer: JazAr hace piezas personalizadas y detrás está Jazmin, diseñadora gráfica.
2. Imaginar: encontrar una prenda, un regalo, un textil o una pieza 3D para una intención concreta.
3. Elegir: explorar una pieza individual o una propuesta coordinada mediante paquetes.
4. Comprender: ver cómo se toman decisiones y cómo participa el cliente antes de producir.
5. Conversar: explicar el proyecto y enviar una solicitud de cotización.

La confianza se construirá con fotografías reales, detalles de acabados y casos que expliquen una decisión visual. No usaremos superlativos como "la mejor del mercado", testimonios inventados, cifras sin evidencia ni garantías de durabilidad o entrega sin confirmar. La calidad se debe poder observar.

## Copies principales

### Hero e introducción

- H1: **JazAr Arte y Diseño**
- Frase principal: **Tu idea merece un buen diseño.**
- Texto: "Prendas, regalos y piezas personalizadas con el criterio de Jazmin Zarate, diseñadora gráfica. Color, composición y detalles para darle forma a lo que quieres expresar."
- CTA principal: **Cotizar mi idea**.
- CTA secundario: **Explora las piezas**.
- Introducción de Jazmin: "Soy Jazmin Zarate, diseñadora gráfica detrás de JazAr. Mi propuesta es ayudarte a transformar una idea en una pieza que tenga sentido para ti: desde cómo se ve hasta cómo se adapta al material."

El texto en primera persona queda propuesto para revisión de Jazmin. La marca será visible en el primer viewport; la presentación personal tendrá espacio propio dentro de la introducción y una fotografía real cuando esté disponible.

### Catálogo

- Título: **Encuentra dónde poner tu idea.**
- Bajada: "Una prenda para tu equipo. Un regalo para alguien especial. Una pieza que haga visible tu marca."
- Organización principal orientada al comprador: **Prendas**, **Regalos**, **Textiles** y **Piezas 3D**. Las técnicas serán etiquetas o filtros complementarios.
- Sublimación: "Color y gráfica en piezas compatibles con sublimación. Elegimos el soporte según tu proyecto."
- DTF: "Gráficos para prendas y textiles, con una propuesta adaptada al formato y al material."
- Impresión 3D: "Ideas que toman volumen. Exploramos forma, escala y acabado según el uso de la pieza."
- Personalización general: "¿Tu proyecto combina varias piezas? Podemos plantearlo como un conjunto."
- CTA por pieza: **Quiero algo así**. Lleva al contacto con la pieza o categoría seleccionada, sin enviar el formulario automáticamente.

Cada proyecto publicado deberá identificar producto, técnica y una decisión de diseño. Por ejemplo: "Ajustamos la composición para que el nombre se lea en el área disponible"; este texto solo se usará si describe lo que realmente se hizo. Hasta contar con fotografías, los espacios reservados se identificarán internamente como referencias de composición y no como trabajos vendidos.

### Paquetes y promociones

- Título: **Una idea. Varias formas de hacerla tuya.**
- Bajada: "Podemos reunir distintas piezas bajo una misma propuesta visual."
- **Un regalo con intención:** composición propuesta para una pieza principal y un complemento compatible. CTA: **Cotiza tu regalo**.
- **Tu equipo, con identidad:** composición propuesta para prendas con un diseño compartido y variantes de nombres cuando la técnica lo permita. CTA: **Cotiza para tu equipo**.
- **Tu marca, en cada detalle:** composición propuesta para varias piezas que mantengan una misma identidad visual. CTA: **Cotiza para tu marca**.

Estos nombres y composiciones son propuestas comerciales, sujetas a validación de Jazmin. No se publicarán como paquetes disponibles hasta confirmar componentes, personalización incluida, cantidades, costos y condiciones. Las promociones solo se mostrarán cuando exista una oferta real, con vigencia, inclusiones y restricciones claras. En ausencia de promoción, esta sección conserva los paquetes aprobados sin descuentos ficticios ni contadores de urgencia.

### Proceso creativo

- Título: **De tu idea a una pieza con intención.**
- Bajada: "Así proponemos trabajar contigo para que cada decisión tenga sentido."
- Cierre: **Empecemos por lo que tienes en mente.**

### Contacto

- Título: **Cuéntame qué quieres crear.**
- Bajada: "Comparte la idea, la cantidad aproximada y la fecha en que la necesitas. Jazmin podrá revisar las posibilidades de tu proyecto."
- Campos propuestos: nombre, correo, tipo de pieza, cantidad aproximada, fecha deseada opcional y descripción de la idea. La categoría puede incluir "Aún no lo sé". Cantidad y fecha no representan una confirmación de disponibilidad.
- CTA: **Enviar mi idea**.
- Confirmación, solo tras aceptación del mensaje por el servidor SMTP: "Tu solicitud se envió. Gracias por compartir tu idea con JazAr."
- Error: "No pudimos enviar tu solicitud. Tus datos siguen aquí para que puedas intentarlo de nuevo."

El remitente técnico será una cuenta autorizada; el correo del visitante se usará como Reply-To. La recepción en bandeja de entrada no se promete solo porque SMTP acepte el envío. El formulario se implementará con validación en servidor, protección CSRF y controles contra abuso. La cuenta Gmail de destino y su configuración siguen pendientes de proporcionar.

## Proceso creativo: estructura conceptual

Flujo propuesto de cinco etapas, pendiente de confirmar con la operación real del taller. Cada etapa debe tener un mensaje breve, una decisión visible y un resultado comprensible; los detalles podrán abrirse por interacción sin exigir animaciones para leerlos.

| Etapa | Copy | Participación del cliente | Resultado y evidencia visual |
| --- | --- | --- | --- |
| 01. Idea: escuchamos | "Qué quieres expresar, para quién y para cuándo." | Comparte uso, referencias, cantidad y fecha deseada. | Un brief breve. Visual: referencias y palabras clave que se ordenan alrededor del objeto. |
| 02. Propuesta: definimos y diseñamos | "Damos forma a tu idea con el material, la técnica y la composición adecuados." | Revisa opciones de pieza, alcance y cotización, y aporta referencias para desarrollar la propuesta visual. | Propuesta de producto, técnica y diseño. Visual: cambio entre soportes y boceto que se transforma en una previsualización, identificada como representación. |
| 03. Aprobación: revisamos contigo | "Revisamos los detalles contigo antes de producir." | Solicita los ajustes incluidos en el alcance y aprueba explícitamente la versión final y las condiciones. | Diseño y condiciones aprobados antes de iniciar producción. Visual: composición detenida para inspeccionar nombre, color, ubicación y escala. |
| 04. Producción: lo llevamos al material | "La propuesta aprobada pasa de la pantalla a una pieza real." | Recibe las comunicaciones necesarias sobre el proyecto acordado. | Producción y revisión del resultado conforme a lo aprobado. Visual: fotografía o video real del proceso cuando se disponga. |
| 05. Entrega: lista para su historia | "Una pieza para usar, regalar o hacer visible tu marca." | Recibe según la modalidad acordada. | Pieza final y, cuando corresponda, indicaciones de cuidado. Visual: vista del producto completo y detalle de acabado. |

La animación debe seguir una sola idea reconocible a través del recorrido, para mostrar transformación y continuidad. La interacción técnica, distancias, disparadores y adaptación móvil se detallan en la propuesta UI/UX. Se mantendrá la secuencia textual completa para teclado, lectores de pantalla, movimiento reducido y dispositivos que no puedan ejecutar efectos avanzados.

## Evidencias y decisiones pendientes

- Validar con Jazmin el tono en primera persona, la secuencia operativa, las revisiones incluidas y las condiciones de aprobación para producir.
- Confirmar catálogo disponible, materiales, paquetes, promociones reales, fechas, cantidades, entregas y cobertura.
- Obtener los archivos originales del logo y sus variantes para producción. La referencia visual de Facebook ya se observó en la captura proporcionada por el usuario; los valores exactos de color y las reglas de uso siguen pendientes de validar con Jazmin.
- Recibir fotografías de productos, detalles, procesos y, si Jazmin lo autoriza, retrato. Usar las imágenes posteriores como evidencia real del trabajo.
- Definir correo Gmail de destino, dominio y contenido del aviso de privacidad para publicar el formulario.

## Criterios de aceptación editorial

Al leer el primer viewport, el visitante identifica la marca, los productos y a la diseñadora. El catálogo se puede explorar por necesidad sin dominar las técnicas. Cada promesa tiene un fundamento verificable. Los cinco apartados del encargo están presentes y cada CTA conduce a una acción coherente. El texto sigue siendo comprensible aunque las animaciones estén desactivadas.
