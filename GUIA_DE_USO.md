# Guía de uso — UrbanStyle RD

## 1. Para qué sirve

UrbanStyle RD es una capa demostrativa sobre las aplicaciones nativas de Odoo. Productos, variantes, existencias, compras, listas de materiales, órdenes de fabricación, órdenes de trabajo, controles de calidad y ventas se guardan en los modelos normales de Odoo. El addon agrega los campos textiles, un tablero y un asistente que carga registros de ejemplo.

El flujo recomendado es:

1. **Preparar el catálogo:** crear cada prenda, sus variantes y el kit con los materiales y cantidades por prenda; definir las áreas, tiempos y margen.
2. **Comprar insumos:** usar la presentación indicada por cada suplidor (yardas, conos, docenas o unidades) y recibir materiales con inspección de entrada. Odoo convierte la recepción a la unidad base del inventario.
3. **Fabricar:** abrir una orden, seleccionar la prenda y revisar la fórmula que se carga automáticamente. Ajustar el lote y, si hace falta, sus cantidades de componentes antes de reservarlos.
4. **Registrar el trabajo:** completar las operaciones en sus áreas y resolver los controles de calidad de cada etapa.
5. **Cerrar producción:** validar la orden para registrar las prendas terminadas en inventario y el consumo de materiales.
6. **Vender:** seleccionar la variante y la presentación (unidad, paquete o caja). Confirmar la orden reserva stock; validar la entrega descuenta las unidades del inventario.
7. **Mantener costos:** actualizar los costos de materiales, tiempos y centros de trabajo; el precio de venta se recalcula con el margen configurado mientras la actualización automática siga activa.

La carga inicial crea stock de materias primas mediante un ajuste de inventario estándar, pero no crea una orden de compra ni una recepción. Estas se pueden crear en vivo desde Odoo.

## 2. Requisitos y acceso

El módulo principal es `urbanstyle_textile_demo`. Declara como dependencias `base`, `mail`, `product`, `uom`, `stock`, `purchase`, `sale_management`, `sale_mrp`, `mrp`, `mrp_workorder`, `quality_control` y `quality_mrp`. `sale_mrp` conecta las líneas de venta con sus órdenes de fabricación para trasladar los datos de personalización. Odoo instala las dependencias al instalar el módulo. `point_of_sale` es opcional.

Después de instalarlo, asigna grupos en **Ajustes → Usuarios y compañías → Usuarios → [usuario] → Derechos de acceso → UrbanStyle RD**. Guarda y vuelve a cargar Odoo para que se actualice el menú.

| Grupo UrbanStyle | Uso previsto |
| --- | --- |
| Administrador UrbanStyle | Configuración, carga demo, fabricación, inventario, calidad, compras y ventas. Es el único grupo con acceso al asistente y al menú Ventas UrbanStyle. |
| Responsable de producción | BoM, operaciones, centros de trabajo y órdenes de fabricación. |
| Operario | Órdenes de trabajo y Taller (Shop Floor), con acceso operativo a fabricación y calidad. |
| Responsable de calidad | Comprobaciones y puntos de control, además de consulta de fabricación. |
| Almacén | Inventario, proveedores y compras. |

Los grupos heredan los permisos nativos correspondientes de Odoo; siguen aplicándose las reglas normales de acceso de la base.

## 3. Cargar la demostración

1. Abre **URBANSTYLE RD → Configuración → Cargar datos de demostración**.
2. Pulsa **Cargar datos de demostración** y espera el aviso con el resumen de registros creados y existentes.
3. Si el asistente indica que no hay almacén, crea primero un almacén para la compañía activa. También deben estar disponibles las unidades estándar **Metro** y **Unidad**.
4. Abre el **Panel de control**. Desde ahí puedes entrar a indicadores, abrir Taller o volver a cargar la demostración.

El asistente habilita las unidades de medida y las dependencias entre operaciones, prepara el catálogo y sus variantes, carga el stock inicial, crea los centros y deja kits y operaciones de demostración para las prendas. También deja una orden de fabricación de falda en borrador.

### Datos incluidos

**Proveedores:** Textiles del Caribe, Distribuidora Textil RD y Accesorios y Confecciones.

**Materias primas** (stock inicial y umbral de stock bajo):

| Producto | Unidad de inventario | Unidad de compra de ejemplo | Stock inicial | Umbral |
| --- | --- | --- | ---: | ---: |
| Tela de poliéster | m | yarda | 240 | 60 |
| Tela de algodón | m | yarda | 180 | 45 |
| Tela de mezclilla (denim) | m | yarda | 180 | 45 |
| Hilo de costura | m | cono de 600 yd | 9.000 | 2.000 |
| Cierres | unidad | unidad | 400 | 80 |
| Botones | unidad | docena | 1.600 | 300 |
| Entretela | m | yarda | 140 | 35 |
| Etiquetas de marca | unidad | unidad | 700 | 150 |

### Medidas prácticas para materiales textiles en RD

La tela se cotiza habitualmente por **yarda**; la anchura del rollo se informa aparte en pulgadas. En Odoo, conviene llevar la tela en **metros** para controlar cortes y consumos con decimales, y comprarla en yardas: una yarda equivale a **0,9144 m**. El campo **Ancho de tela (pulgadas)** conserva la especificación del rollo sin confundir anchura con longitud de inventario.

El hilo para costura industrial suele adquirirse por **cono**, pero su longitud cambia según proveedor y referencia. Se controla el inventario y la receta en metros; la unidad de compra debe indicar el metraje real del cono. El ejemplo de UrbanStyle usa **600 yardas por cono** (548,64 m), una presentación que aparece en una guía de costos de la DGCP. Confirma siempre el metraje de la etiqueta del proveedor antes de usar esa conversión.

El catálogo permite registrar composición, textura o tipo de tejido, color, peso en g/m², utilización recomendada y ancho del rollo en pulgadas. Las especificaciones precargadas de las telas de demostración son ejemplos; confirma los datos con cada proveedor antes de utilizarlos en compras o producción.

Los botones pueden cotizarse por **unidad** o por una presentación comercial como **docena**, gruesa o caja; se consumen por **unidad**. El ejemplo usa docena para compra e inventario unitario. Registra el costo y la presentación de cada proveedor.

Estas son recomendaciones prácticas, no una norma única para todos los suplidores: los documentos de compras públicas dominicanos muestran telas por yardas, conos de hilo y botones por docena; el negocio puede configurar cada referencia según su proveedor. Fuentes de referencia: [guía de costos para MIPYMES de la DGCP](https://www.dgcp.gob.do/new_dgcp/documentos/fomen/Guia%20sobre%20como%20venderle%20al%20Estado.pdf), [ejemplo dominicano de compra de telas, conos y botones](https://comunidad.comprasdominicana.gob.do/Public/Tendering/OpportunityDetail/Index?noticeUID=DO1.NTC.660051) y [equivalencia yarda/metro en Odoo 19](https://www.odoo.com/documentation/19.0/es/applications/inventory_and_mrp/inventory/product_management/configure/uom.html).

**Prendas:** Falda plisada clásica, Camiseta básica, Pantalón recto y Jean clásico. Cada plantilla tiene variantes nativas de talla **XS, S, M, L, XL** y color **Negro, Blanco, Beige, Azul**. Cada prenda incluye un kit y operaciones de inicio que se pueden editar para ajustarlos al patrón real. Las cantidades y tiempos son ejemplos demostrativos, no una ficha técnica de producción aprobada. Las unidades de venta se crean por defecto como **paquete de 10** y **caja de 40**, y el negocio puede definir otras cantidades. La orden de fabricación de ejemplo usa la falda **M / Negro**.

**Centros de trabajo:** Área de corte, Área de plisado, Área de costura, Área de bordado, Área de acabados y Área de inspección. Cada uno tiene tiempos, eficiencia, capacidad y costo por hora configurados y se puede editar.

**Kits de inicio por prenda:**

- **Falda plisada clásica:** 1,60 m de poliéster, 60 m de hilo, 1 cierre, 0,20 m de entretela y 1 etiqueta.
- **Camiseta básica:** 1,25 m de algodón, 45 m de hilo y 1 etiqueta.
- **Pantalón recto:** 1,65 m de algodón, 65 m de hilo, 1 cierre, 1 botón, 0,15 m de entretela y 1 etiqueta.
- **Jean clásico:** 1,80 m de denim, 80 m de hilo, 1 cierre, 1 botón, 0,25 m de entretela y 1 etiqueta.

Confirma los consumos y tiempos con el patrón y el método de producción del negocio antes de usar los precios calculados en ventas reales.

**Operaciones en secuencia:**

| Orden | Operación | Centro de trabajo | Tiempo de ciclo | Control de calidad |
| ---: | --- | --- | ---: | --- |
| 1 | Inspección inicial de tela | Área de inspección | 6 min | — |
| 2 | Extendido y corte | Área de corte | 18 min | Después del corte |
| 3 | Elaboración de pliegues | Área de plisado | 28 min | Después del plisado |
| 4 | Costura y confección | Área de costura | 42 min | Después de la confección |
| 5 | Bordado o personalización | Área de bordado | 16 min | — |
| 6 | Planchado y acabados | Área de acabados | 14 min | — |
| 7 | Inspección final y empaque | Área de inspección | 10 min | Antes del almacenamiento final |

La operación siguiente queda bloqueada hasta completar la anterior. La tela de algodón y los botones están en el catálogo demo, pero no forman parte de esta BoM de la falda.

En la operación de plisado se precargan pliegues tipo tabla, ancho 2,5 cm, distancia 1,5 cm, 24 pliegues, tela de poliéster y fijación con vapor industrial. Las instrucciones técnicas se muestran en la orden de trabajo y en Taller.

**Calidad:** hay controles después del corte, plisado y confección, antes del almacenamiento final, y un punto de inspección de materias primas para las recepciones.

## 4. Recorrido recomendado: fabricar una falda

1. En **URBANSTYLE RD → Órdenes de fabricación**, abre la orden de ejemplo en borrador.
2. Revisa producto, cantidad y BoM. Para crear otra, inicia una orden nueva y selecciona una variante de prenda.
3. Confirma la orden. Odoo genera órdenes de trabajo a partir de las operaciones de la BoM. Si hace falta, usa **Comprobar disponibilidad** para reservar componentes.
4. Abre **URBANSTYLE RD → Órdenes de trabajo** o pulsa **Abrir Taller (Shop Floor)** desde el tablero.
5. El operario inicia el trabajo, consulta las instrucciones del centro y completa cada operación. En **Elaboración de pliegues** revisa las medidas e instrucciones; los parámetros se copian a la orden de trabajo al generarla.
6. En las etapas con control, registra el resultado. Una comprobación pendiente puede impedir continuar o cerrar la producción hasta que se resuelva.
7. Completa las operaciones y cierra la orden de fabricación. La producción registrada se refleja en las existencias de la variante fabricada.

Los cambios posteriores en una operación de BoM no alteran retroactivamente las órdenes de trabajo ya creadas. Para probar nuevos parámetros, crea una nueva orden de fabricación.

## 5. Compras y recepción con calidad

1. En **Compras**, crea una solicitud de presupuesto y selecciona uno de los proveedores.
2. Añade las materias primas, cantidades y unidades. Los proveedores demo proponen yardas para telas y entretela, un cono de hilo de 600 yardas, docenas para botones y unidades para cierres y etiquetas. Cada proveedor puede usar su propia unidad de compra; la unidad de inventario sigue siendo metros para tejidos/hilo y unidades para accesorios.
3. Confirma la compra y abre la recepción generada por Odoo.
4. En la recepción, completa las comprobaciones de calidad que aparezcan para las materias primas y valida la transferencia cuando corresponda.

La recepción convierte automáticamente la cantidad comprada a la unidad de inventario del producto. Por ejemplo, recibir 2 yardas suma 1,8288 m de tela; recibir un cono del ejemplo suma 548,64 m de hilo; recibir una docena suma 12 botones. Ajusta la unidad del proveedor si el rollo, cono, caja o docena tiene otra cantidad. El asistente crea el punto de control, pero no simula ni valida compras. Volver a cargar la demo no repone cantidades consumidas; usa una compra o un ajuste de inventario de Odoo.

## 6. Controles de calidad y defectos

En **Control de calidad → Comprobaciones** se consultan los registros generados; en **Puntos de control** se editan las reglas. Las comprobaciones de proceso se asocian a operaciones de la BoM y las de entrada al tipo de transferencia de recepción.

Marca **Aprobado** o **Rechazado** y registra observaciones según el flujo nativo de Calidad. Si una pieza falla, la marca de rechazo no crea por sí sola un registro de desecho personalizado de UrbanStyle. Gestiona la alerta, retrabajo o desecho con las herramientas estándar de Calidad e Inventario y los permisos/configuración de tu base.

## 7. Inventario y ventas

- **Inventario:** el menú UrbanStyle abre las existencias. **Productos en stock** muestra las variantes textiles y prendas con cantidad disponible mayor que cero. Las materias primas tienen un umbral propio; al bajar de él, el tablero las cuenta como stock bajo. La cantidad disponible se consulta en la compañía activa.
- **Ventas:** en una línea de cotización elige la presentación en el campo Unidad: unidad, paquete o caja. La cantidad se convierte a unidades base; vender 2 cajas de 40 genera una demanda de 80 prendas. Al validar la entrega, Odoo descuenta esa cantidad del inventario. Confirmar una cotización reserva la demanda según las reglas de stock; la existencia física se reduce al validar la salida. La carga de demostración activa las unidades de medida para que esas presentaciones estén disponibles en ventas.
- **Precio:** el precio unitario se actualiza con costo de materiales + mano de obra estimada en cada centro de trabajo + margen. El margen inicial es 30% sobre el costo y se puede cambiar por prenda en **Fabricación**. La materia prima se costea con su campo **Costo unitario** (costo estándar); actualízalo cuando cambie el costo que quieres usar en la receta. Si alguien edita manualmente el precio de venta, se desactiva su actualización automática para esa prenda.
- **Punto de Venta (opcional):** instala `point_of_sale` antes de ejecutar el asistente. Si está instalado, el asistente habilita las prendas terminadas para POS y les asigna la categoría **UrbanStyle RD**. Si se instala POS más tarde, vuelve a ejecutar el asistente.

## 8. Qué muestra el tablero

Los indicadores se calculan consultando los registros de la compañía activa:

- Órdenes de fabricación confirmadas, en producción y completadas.
- Unidades producidas en órdenes completadas.
- Comprobaciones de calidad pendientes.
- Materias primas por debajo del umbral configurado.
- Unidades disponibles de prendas terminadas.

Pulsa cada indicador para abrir los registros relacionados. Los valores pueden cambiar después de confirmar una orden, registrar producción, completar una calidad, recibir materiales o validar una venta/entrega.

## 9. Crear y mantener registros en vivo

Las opciones **Productos textiles** y **Materias primas** abren fichas enfocadas en el flujo UrbanStyle. Al crear desde cada lista, el producto queda clasificado automáticamente como prenda o materia prima y se configura para controlar existencias. La ficha muestra solo los datos de identificación, inventario, compra, fabricación, variantes y venta que aplican a esa clase de artículo. Las variantes de talla y color se administran en **Variantes**. En materias primas, registra el costo unitario, unidad base, existencia mínima y proveedores; selecciona también la unidad de compra en la fila de cada suplidor cuando sus presentaciones sean distintas.

Al crear una prenda desde **Productos textiles**, el sistema prepara su kit automáticamente. Abre **Fabricación**, entra al kit y define los materiales, la cantidad por prenda y la unidad de consumo; después añade operaciones con centro de trabajo y duración. El kit debe incluir al menos un material y una operación válida. No se puede confirmar una orden de fabricación ni una venta UrbanStyle con un kit incompleto. Para el precio automático, cada centro incluido en las operaciones debe tener un costo por hora mayor que cero. Al crear una orden de fabricación y seleccionar la prenda, Odoo propone automáticamente el kit y escala las cantidades al lote.

El precio se actualiza al cambiar la cantidad o el costo unitario de un material, las operaciones/tiempos o el costo por hora de un área. Los tiempos se estiman con la duración planificada de las operaciones; registra los costos por hora de corte, costura, acabados y las demás áreas en **Centros de trabajo**. El cálculo es **precio = (materiales + mano de obra estimada) × (1 + margen / 100)**. El margen se aplica como recargo sobre el costo, no incluye impuestos, gastos financieros ni descuentos comerciales. El precio de compra registrado en la fila del suplidor es una referencia de compra; el cálculo utiliza el **Costo unitario** de inventario de cada materia prima.

Define las presentaciones de venta en **Unidades por paquete** y **Unidades por caja**. La unidad base de la prenda debe ser **Unidad**, es decir, una prenda individual; por defecto se crean paquete x10 y caja x40. La caja debe ser múltiplo del paquete para mantener una configuración ordenada. Los valores aplican a todas las variantes del mismo producto; cada producto puede tener sus propios tamaños de paquete y caja.

Producción puede crear y editar BoM, centros, operaciones y órdenes desde los menús UrbanStyle. En una operación, activa **¿Es operación de plisado?** para mostrar las especificaciones textiles. Los formularios normales de Odoo conservan sus acciones estándar para guardar, archivar y consultar registros.

## 10. Calculadora textil y personalizaciones

### Estimar consumo de tela

1. Abre **URBANSTYLE RD → Calculadora textil**.
2. Filtra por composición, textura, color, utilización y un rango de peso en g/m²; luego selecciona una tela compatible del catálogo.
3. Indica cantidad de piezas, largo y ancho por pieza en centímetros, y el porcentaje de desperdicio. La ficha de la tela debe tener informado su ancho de rollo en pulgadas.
4. El asistente calcula la superficie requerida y los metros lineales aproximados: suma el área rectangular de las piezas, aplica el desperdicio y divide entre el ancho convertido a metros.

La estimación no reemplaza el patronaje ni la disposición de corte. Curvas, márgenes de costura, tallas, encogimiento y orientación de las piezas pueden cambiar el consumo real; valida el resultado con el patrón antes de comprar o fabricar.

### Diseños personalizados y órdenes de fabricación

1. En **URBANSTYLE RD → Personalización → Especializaciones**, revisa o crea las capacidades disponibles, como serigrafía, sublimación, vinilo, bordado o aplicaciones.
2. En **Diseños y estampados**, registra cada diseño con técnica, muestra, especializaciones requeridas y recargo por prenda.
3. Al preparar una cotización, elige el diseño solicitado en la línea de la prenda. El recargo se suma al precio unitario por cada prenda, se convierte a la moneda de la venta y aparece en la descripción de la línea. Las especializaciones del diseño se proponen automáticamente; pueden ajustarse junto con las instrucciones.
4. Cuando se crea una orden de fabricación desde esa línea de venta, el diseño, las especializaciones, las instrucciones y el recargo por prenda se copian a la pestaña **Personalización**. Las órdenes parciales conservan estos datos. En órdenes manuales, se pueden registrar directamente en esa pestaña.

## 11. Cómo evita duplicados el asistente

El asistente identifica datos de demostración con el marcador UrbanStyle y, en productos, también usa referencias internas. Si existe un registro demo, lo conserva; no reescribe el catálogo existente ni reinicia el stock inicial. Si una referencia interna ya pertenece a un artículo manual, el artículo demo usa una referencia alternativa con sufijo `-DEMO`. Si ya hay atributos incompatibles llamados **Talla** o **Color**, el asistente usa atributos con sufijo **(UrbanStyle RD)** para no modificarlos.

La carga es repetible para completar lo que falte, pero no es una herramienta para restablecer la base. Para reponer inventario o corregir un registro existente, edítalo mediante Odoo.

## 12. Solución de problemas

| Síntoma | Qué revisar |
| --- | --- |
| No aparece **URBANSTYLE RD** | Asigna al usuario uno de los grupos UrbanStyle y vuelve a cargar la página. El asistente solo aparece para Administrador UrbanStyle. |
| El asistente dice que falta almacén o unidad | Confirma que la compañía activa tenga un almacén y estén cargadas las unidades Metro y Unidad. |
| La orden está en borrador y no hay órdenes de trabajo | Confirma la orden de fabricación; las operaciones se generan a partir de la BoM al confirmar. |
| La operación siguiente está bloqueada | Completa la operación anterior en secuencia y resuelve sus controles de calidad. |
| El tablero marca stock bajo | Revisa la cantidad disponible y el umbral del producto. El asistente no repone existencias en ejecuciones posteriores. |
| La calculadora no da metros lineales | Selecciona una tela y registra el ancho de rollo en pulgadas en su ficha. |
| No aparece un diseño en la venta | Crea y activa el diseño en **Personalización → Diseños y estampados** y confirma que la línea corresponda a una prenda UrbanStyle. |
| La carga vuelve a mostrar un error de campo `uom_po_id` | Ese campo se quitó del asistente para Odoo 19. Recarga Odoo para que el servidor tome el Python actualizado y vuelve a ejecutar la carga; no reinstales el módulo. |
| No se configura POS | Instala `point_of_sale` y vuelve a ejecutar la carga demo. |

## 13. Módulos instalados

Principal: `urbanstyle_textile_demo`.

Dependencias directas: `base`, `mail`, `product`, `uom`, `stock`, `purchase`, `sale_management`, `sale_mrp`, `mrp`, `mrp_workorder`, `quality_control`, `quality_mrp`.

Opcional: `point_of_sale`.

Odoo resuelve las dependencias declaradas al instalar el módulo. Para las funciones de Taller y los controles asociados a operaciones se requieren `mrp_workorder` y `quality_mrp`.
