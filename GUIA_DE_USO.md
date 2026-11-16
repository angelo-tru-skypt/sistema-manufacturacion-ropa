# Guía de uso — UrbanStyle RD

## 1. Para qué sirve

UrbanStyle RD es una capa demostrativa sobre las aplicaciones nativas de Odoo. Productos, variantes, existencias, compras, listas de materiales, órdenes de fabricación, órdenes de trabajo, controles de calidad y ventas se guardan en los modelos normales de Odoo. El addon agrega los campos textiles, un tablero y un asistente que carga registros de ejemplo.

El flujo que puedes presentar es:

**Compra y recepción → inspección de entrada → planificación → fabricación por operaciones → controles de calidad → inventario de prendas → venta.**

La carga inicial crea stock de materias primas mediante un ajuste de inventario estándar, pero no crea una orden de compra ni una recepción. Estas se pueden crear en vivo desde Odoo.

## 2. Requisitos y acceso

El módulo principal es `urbanstyle_textile_demo`. Declara como dependencias `base`, `mail`, `product`, `stock`, `purchase`, `sale_management`, `mrp`, `mrp_workorder`, `quality_control` y `quality_mrp`. Odoo instala las dependencias al instalar el módulo. `point_of_sale` es opcional.

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

El asistente habilita rutas y dependencias entre operaciones, prepara el catálogo y sus variantes, carga el stock inicial, crea los centros y la BoM de la falda y deja una orden de fabricación en borrador.

### Datos incluidos

**Proveedores:** Textiles del Caribe, Distribuidora Textil RD y Accesorios y Confecciones.

**Materias primas** (stock inicial y umbral de stock bajo):

| Producto | Unidad | Stock inicial | Umbral |
| --- | --- | ---: | ---: |
| Tela de poliéster | m | 240 | 60 |
| Tela de algodón | m | 180 | 45 |
| Hilo de costura | m | 9.000 | 2.000 |
| Cierres | unidad | 400 | 80 |
| Botones | unidad | 1.600 | 300 |
| Entretela | m | 140 | 35 |
| Etiquetas de marca | unidad | 700 | 150 |

**Prendas:** Falda plisada clásica, Camiseta básica y Pantalón recto. Cada plantilla tiene variantes nativas de talla **XS, S, M, L, XL** y color **Negro, Blanco, Beige, Azul**. La carga asigna precios de venta de 1.890, 890 y 2.190, respectivamente, en la moneda de la compañía. La orden de fabricación de ejemplo usa la falda **M / Negro**.

**Centros de trabajo:** Área de corte, Área de plisado, Área de costura, Área de bordado, Área de acabados y Área de inspección. Cada uno tiene tiempos, eficiencia, capacidad y costo por hora configurados y se puede editar.

**BoM de una Falda plisada clásica:** 1,60 m de tela de poliéster, 60 m de hilo, 1 cierre, 0,20 m de entretela y 1 etiqueta.

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
2. Añade las materias primas, cantidades y unidades. El catálogo usa metros para telas e hilo y unidades para cierres, botones y etiquetas.
3. Confirma la compra y abre la recepción generada por Odoo.
4. En la recepción, completa las comprobaciones de calidad que aparezcan para las materias primas y valida la transferencia cuando corresponda.

La recepción es un flujo nativo: el asistente crea el punto de control, pero no simula ni valida compras. Para aprovisionar los datos de ejemplo sin una compra, usa la existencia inicial cargada. Volver a ejecutar el asistente no repone cantidades consumidas; usa una compra o un ajuste de inventario de Odoo.

## 6. Controles de calidad y defectos

En **Control de calidad → Comprobaciones** se consultan los registros generados; en **Puntos de control** se editan las reglas. Las comprobaciones de proceso se asocian a operaciones de la BoM y las de entrada al tipo de transferencia de recepción.

Marca **Aprobado** o **Rechazado** y registra observaciones según el flujo nativo de Calidad. Si una pieza falla, la marca de rechazo no crea por sí sola un registro de desecho personalizado de UrbanStyle. Gestiona la alerta, retrabajo o desecho con las herramientas estándar de Calidad e Inventario y los permisos/configuración de tu base.

## 7. Inventario y ventas

- **Inventario:** el menú UrbanStyle abre las existencias. Las materias primas tienen un umbral propio; al bajar de él, el tablero las cuenta como stock bajo. La cantidad disponible se consulta en la compañía activa.
- **Ventas:** el administrador puede crear una cotización con la variante deseada, confirmarla y procesar la entrega desde el flujo estándar de Ventas e Inventario.
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

Las opciones **Productos textiles** y **Materias primas** usan los formularios normales de producto. Para que un producto nuevo aparezca en esas listas, activa **Prenda terminada UrbanStyle** o **Materia prima textil**; para los insumos, define además la existencia mínima. Las variantes de talla y color se administran desde los atributos nativos del producto.

Producción puede crear y editar BoM, centros, operaciones y órdenes desde los menús UrbanStyle. En una operación, activa **¿Es operación de plisado?** para mostrar las especificaciones textiles. Los formularios normales de Odoo conservan sus acciones estándar para guardar, archivar y consultar registros.

## 10. Cómo evita duplicados el asistente

El asistente identifica datos de demostración con el marcador UrbanStyle y, en productos, también usa referencias internas. Si existe un registro demo, lo conserva; no reescribe el catálogo existente ni reinicia el stock inicial. Si una referencia interna ya pertenece a un artículo manual, el artículo demo usa una referencia alternativa con sufijo `-DEMO`. Si ya hay atributos incompatibles llamados **Talla** o **Color**, el asistente usa atributos con sufijo **(UrbanStyle RD)** para no modificarlos.

La carga es repetible para completar lo que falte, pero no es una herramienta para restablecer la base. Para reponer inventario o corregir un registro existente, edítalo mediante Odoo.

## 11. Solución de problemas

| Síntoma | Qué revisar |
| --- | --- |
| No aparece **URBANSTYLE RD** | Asigna al usuario uno de los grupos UrbanStyle y vuelve a cargar la página. El asistente solo aparece para Administrador UrbanStyle. |
| El asistente dice que falta almacén o unidad | Confirma que la compañía activa tenga un almacén y estén cargadas las unidades Metro y Unidad. |
| La orden está en borrador y no hay órdenes de trabajo | Confirma la orden de fabricación; las operaciones se generan a partir de la BoM al confirmar. |
| La operación siguiente está bloqueada | Completa la operación anterior en secuencia y resuelve sus controles de calidad. |
| El tablero marca stock bajo | Revisa la cantidad disponible y el umbral del producto. El asistente no repone existencias en ejecuciones posteriores. |
| La carga vuelve a mostrar un error de campo `uom_po_id` | Ese campo se quitó del asistente para Odoo 19. Recarga Odoo para que el servidor tome el Python actualizado y vuelve a ejecutar la carga; no reinstales el módulo. |
| No se configura POS | Instala `point_of_sale` y vuelve a ejecutar la carga demo. |

## 12. Módulos instalados

Principal: `urbanstyle_textile_demo`.

  Dependencias directas: `base`, `mail`, `product`, `stock`, `purchase`, `sale_management`, `mrp`, `mrp_workorder`, `quality_control`, `quality_mrp`.

Opcional: `point_of_sale`.

Odoo resuelve las dependencias declaradas al instalar el módulo. Para las funciones de Taller y los controles asociados a operaciones se requieren `mrp_workorder` y `quality_mrp`.
