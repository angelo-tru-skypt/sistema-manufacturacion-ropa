# UrbanStyle RD — demostración textil para Odoo 19 Enterprise

Este addon extiende los modelos nativos de Odoo para una demostración de fabricación textil. Incluye un catálogo filtrable de telas y materiales, calculadora aproximada de consumo por medidas, diseños personalizados con recargo por prenda y registro de especializaciones en las órdenes de fabricación. También prepara fórmulas de materiales, convierte presentaciones de venta a unidades de inventario y calcula precios con materiales, mano de obra y margen. Usa ORM y registros persistentes; no reemplaza Manufactura, Inventario, Compras, Ventas ni Calidad.

Consulta [GUIA_DE_USO.md](GUIA_DE_USO.md) para la guía operativa completa, los perfiles, el recorrido de fabricación y las recomendaciones de solución de problemas.

## Instalación en este entorno

El proyecto Compose local monta `addons/` en `/mnt/extra-addons`, y el archivo `odoo.conf` incluye `/mnt/extra-addons/extra` en `addons_path`. Por eso este módulo se instala desde `addons/extra/urbanstyle_textile_demo`.

1. Inicia el entorno Odoo 19.0 y su base de datos.
2. En Odoo, actualiza la lista de aplicaciones.
3. Instala **UrbanStyle RD - Demo textil**.
4. Asigna a los usuarios uno de los grupos UrbanStyle desde Ajustes > Usuarios.
5. Abre **URBANSTYLE RD > Configuración > Cargar datos de demostración**.

El asistente habilita las rutas y dependencias de operaciones, carga productos, variantes, proveedores, inventario inicial mediante el ajuste estándar, centros, BoM y controles de calidad. También crea una orden de fabricación en borrador para la falda talla M color negro. La orden se puede confirmar en vivo para generar órdenes de trabajo y comprobar el flujo.

La carga se puede repetir: identifica los datos del demo por el marcador UrbanStyle y conserva los registros existentes. No reinicia las existencias cuando se vuelve a ejecutar.

## Aplicaciones y módulos

Dependencias directas declaradas en el manifest:

- `base`, `mail`, `uom`
- `product`, `stock`
- `purchase`, `sale_management`, `sale_mrp`
- `mrp`, `mrp_workorder`
- `quality_control`, `quality_mrp`

Odoo instalará las dependencias transitivas de estos módulos. `mrp_workorder` y `quality_mrp` son las integraciones Enterprise requeridas para órdenes de trabajo, Taller y puntos de control ligados a las operaciones de fabricación.

`point_of_sale` es opcional y no es dependencia del addon. Si ya está instalado, el asistente habilita las prendas terminadas para POS y les asigna la categoría UrbanStyle RD.

## Ejecución de pruebas

Con Odoo y PostgreSQL en ejecución, se pueden ejecutar las pruebas del addon desde el comando habitual del servidor de Odoo con `--test-enable --stop-after-init -i urbanstyle_textile_demo` sobre una base de pruebas.
