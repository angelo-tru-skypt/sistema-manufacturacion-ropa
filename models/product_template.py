from math import ceil

from odoo import Command, api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_urbanstyle_demo = fields.Boolean(
        string="Dato de demostración UrbanStyle RD",
        default=False,
        copy=False,
        index=True,
    )
    urbanstyle_is_raw_material = fields.Boolean(
        string="Materia prima textil",
        default=False,
        help="Identifica los insumos del catálogo demostrativo UrbanStyle RD.",
    )
    urbanstyle_is_finished_product = fields.Boolean(
        string="Prenda terminada UrbanStyle",
        default=False,
        help="Incluye la prenda en el catálogo textil. Lleva su inventario en prendas individuales; los paquetes y cajas se convierten a esa unidad.",
    )
    urbanstyle_material_kind = fields.Selection(
        [
            ("fabric", "Tela o tejido"),
            ("thread", "Hilo"),
            ("button", "Botón"),
            ("accessory", "Accesorio"),
            ("other", "Otro material"),
        ],
        string="Tipo de material textil",
        default="other",
    )
    urbanstyle_fabric_width_in = fields.Float(
        string="Ancho de tela (pulgadas)",
        digits=(16, 2),
        help="El ancho se registra en pulgadas; el inventario de tela se controla por longitud.",
    )
    urbanstyle_min_stock = fields.Float(
        string="Existencia mínima UrbanStyle",
        digits="Product Unit",
        default=0.0,
        help="Umbral utilizado por el panel UrbanStyle para señalar existencias bajas.",
    )
    urbanstyle_low_stock = fields.Boolean(
        string="Existencia baja UrbanStyle",
        compute="_compute_urbanstyle_low_stock",
        search="_search_urbanstyle_low_stock",
    )
    urbanstyle_kit_bom_ids = fields.One2many(
        "mrp.bom",
        "product_tmpl_id",
        string="Kits de materiales",
        domain=[("urbanstyle_is_material_kit", "=", True), ("type", "=", "normal")],
    )
    urbanstyle_auto_price = fields.Boolean(
        string="Actualizar precio automáticamente",
        default=True,
        help="Actualiza el precio de venta cuando cambian la receta, sus costos, los tiempos de operación o el margen.",
    )
    urbanstyle_margin_pct = fields.Float(
        string="Margen de ganancia sobre costo (%)",
        default=30.0,
        digits=(16, 2),
        help="Se aplica como recargo sobre el costo total estimado de materiales y mano de obra.",
    )
    urbanstyle_material_cost = fields.Monetary(
        string="Costo de materiales por unidad",
        compute="_compute_urbanstyle_costs",
        currency_field="cost_currency_id",
    )
    urbanstyle_labor_cost = fields.Monetary(
        string="Mano de obra por unidad",
        compute="_compute_urbanstyle_costs",
        currency_field="cost_currency_id",
    )
    urbanstyle_unit_cost = fields.Monetary(
        string="Costo total por unidad",
        compute="_compute_urbanstyle_costs",
        currency_field="cost_currency_id",
    )
    urbanstyle_calculated_sale_price = fields.Monetary(
        string="Precio de venta calculado",
        compute="_compute_urbanstyle_costs",
        currency_field="currency_id",
    )
    urbanstyle_pack_quantity = fields.Integer(
        string="Unidades por paquete",
        default=10,
        help="Cantidad de prendas individuales por paquete. La unidad de inventario del producto debe ser una prenda.",
    )
    urbanstyle_box_quantity = fields.Integer(
        string="Unidades por caja",
        default=40,
        help="Cantidad de prendas individuales por caja. La unidad de inventario del producto debe ser una prenda.",
    )
    urbanstyle_pack_uom_id = fields.Many2one("uom.uom", string="Unidad paquete", copy=False, readonly=True)
    urbanstyle_box_uom_id = fields.Many2one("uom.uom", string="Unidad caja", copy=False, readonly=True)

    @api.depends(
        "urbanstyle_margin_pct",
        "urbanstyle_kit_bom_ids.product_qty",
        "urbanstyle_kit_bom_ids.product_uom_id",
        "urbanstyle_kit_bom_ids.bom_line_ids.product_qty",
        "urbanstyle_kit_bom_ids.bom_line_ids.product_uom_id",
        "urbanstyle_kit_bom_ids.bom_line_ids.product_id.uom_id",
        "urbanstyle_kit_bom_ids.bom_line_ids.product_id.standard_price",
        "urbanstyle_kit_bom_ids.operation_ids.time_cycle",
        "urbanstyle_kit_bom_ids.operation_ids.workcenter_id.costs_hour",
        "urbanstyle_kit_bom_ids.operation_ids.workcenter_id.time_efficiency",
        "urbanstyle_kit_bom_ids.operation_ids.workcenter_id.time_start",
        "urbanstyle_kit_bom_ids.operation_ids.workcenter_id.time_stop",
        "urbanstyle_kit_bom_ids.operation_ids.workcenter_id.capacity_ids.capacity",
        "urbanstyle_kit_bom_ids.operation_ids.workcenter_id.capacity_ids.product_id",
        "urbanstyle_kit_bom_ids.operation_ids.workcenter_id.capacity_ids.product_uom_id",
        "urbanstyle_kit_bom_ids.operation_ids.workcenter_id.capacity_ids.time_start",
        "urbanstyle_kit_bom_ids.operation_ids.workcenter_id.capacity_ids.time_stop",
    )
    @api.depends_context("company")
    def _compute_urbanstyle_costs(self):
        for template in self:
            material_cost, labor_cost = template._urbanstyle_get_unit_costs()
            unit_cost = material_cost + labor_cost
            template.urbanstyle_material_cost = material_cost
            template.urbanstyle_labor_cost = labor_cost
            template.urbanstyle_unit_cost = unit_cost
            template.urbanstyle_calculated_sale_price = unit_cost * (1 + template.urbanstyle_margin_pct / 100.0)

    def _urbanstyle_get_unit_costs(self):
        self.ensure_one()
        bom = self.urbanstyle_kit_bom_ids[:1]
        if not bom or not bom.product_qty:
            return 0.0, 0.0

        material_cost = 0.0
        for line in bom.bom_line_ids:
            if not line.product_id or not line.product_uom_id:
                continue
            quantity = line.product_uom_id._compute_quantity(
                line.product_qty,
                line.product_id.uom_id,
                round=False,
            )
            material_cost += quantity * line.product_id.with_company(bom.company_id or self.env.company).standard_price

        labor_cost = 0.0
        product = self.product_variant_id
        for operation in bom.operation_ids:
            workcenter = operation.workcenter_id
            if not workcenter:
                continue
            capacity, setup, cleanup = workcenter._get_capacity(
                product,
                bom.product_uom_id,
                bom.product_qty,
            )
            capacity = capacity or 1.0
            cycles = max(1, ceil(bom.product_qty / capacity))
            efficiency = workcenter.time_efficiency or 100.0
            expected_minutes = setup + cleanup + cycles * operation.time_cycle * 100.0 / efficiency
            labor_cost += expected_minutes / 60.0 * workcenter.costs_hour

        produced_quantity = bom.product_uom_id._compute_quantity(
            bom.product_qty,
            self.uom_id,
            round=False,
        )
        if not produced_quantity:
            return 0.0, 0.0
        return material_cost / produced_quantity, labor_cost / produced_quantity

    def _urbanstyle_recompute_sale_prices(self):
        for template in self.filtered(
            lambda product: product.urbanstyle_is_finished_product and product.urbanstyle_auto_price
        ):
            bom = template.urbanstyle_kit_bom_ids[:1]
            if not bom or not bom.bom_line_ids:
                continue
            material_cost, labor_cost = template._urbanstyle_get_unit_costs()
            price = (material_cost + labor_cost) * (1 + template.urbanstyle_margin_pct / 100.0)
            currency = template.currency_id or self.env.company.currency_id
            price = currency.round(price)
            if float_compare(template.list_price, price, precision_rounding=currency.rounding):
                template.with_context(urbanstyle_auto_price_update=True).write({"list_price": price})

    def _ensure_urbanstyle_material_kit(self):
        Bom = self.env["mrp.bom"].sudo()
        for template in self.filtered("urbanstyle_is_finished_product"):
            company = template.company_id or self.env.company
            bom = Bom.search(
                [
                    ("product_tmpl_id", "=", template.id),
                    ("product_id", "=", False),
                    ("type", "=", "normal"),
                    ("company_id", "in", [False, company.id]),
                ],
                order="urbanstyle_is_material_kit desc, sequence, id",
                limit=1,
            )
            if bom:
                if not bom.urbanstyle_is_material_kit:
                    bom.urbanstyle_is_material_kit = True
                continue
            Bom.with_company(company).create(
                {
                    "product_tmpl_id": template.id,
                    "product_qty": 1.0,
                    "product_uom_id": template.uom_id.id,
                    "type": "normal",
                    "company_id": company.id,
                    "urbanstyle_is_material_kit": True,
                }
            )

    def _urbanstyle_bom_is_ready(self, bom=None, require_costed_operations=False):
        self.ensure_one()
        bom = bom or self.urbanstyle_kit_bom_ids[:1]
        if not bom or bom.product_tmpl_id != self or bom.type != "normal":
            return False

        components = bom.bom_line_ids.filtered(
            lambda line: line.product_id and line.product_qty > 0
        )
        if not components or len(components) != len(bom.bom_line_ids) or not bom.operation_ids:
            return False

        for operation in bom.operation_ids:
            workcenter = operation.workcenter_id
            if not workcenter or operation.time_cycle <= 0:
                return False
            if require_costed_operations and workcenter.costs_hour <= 0:
                return False
        return True

    def _ensure_urbanstyle_sales_uoms(self):
        Uom = self.env["uom.uom"].sudo()
        for template in self.filtered("urbanstyle_is_finished_product"):
            if not template.uom_id:
                continue
            for packaging_type, quantity, field_name, label in (
                ("pack", template.urbanstyle_pack_quantity, "urbanstyle_pack_uom_id", "Paquete"),
                ("box", template.urbanstyle_box_quantity, "urbanstyle_box_uom_id", "Caja"),
            ):
                uom = Uom.search(
                    [
                        ("urbanstyle_product_tmpl_id", "=", template.id),
                        ("urbanstyle_packaging_type", "=", packaging_type),
                        ("relative_uom_id", "=", template.uom_id.id),
                        ("relative_factor", "=", quantity),
                    ],
                    limit=1,
                )
                if not uom:
                    uom = Uom.create(
                        {
                            "name": _("%(product)s - %(packaging)s x%(quantity)s")
                            % {
                                "product": template.name,
                                "packaging": label,
                                "quantity": quantity,
                            },
                            "relative_uom_id": template.uom_id.id,
                            "relative_factor": quantity,
                            "urbanstyle_product_tmpl_id": template.id,
                            "urbanstyle_packaging_type": packaging_type,
                        }
                    )
                previous_uom = template[field_name]
                commands = [Command.link(uom.id)]
                if previous_uom and previous_uom != uom and previous_uom in template.uom_ids:
                    commands.insert(0, Command.unlink(previous_uom.id))
                template.write({field_name: uom.id, "uom_ids": commands})

    @api.constrains("urbanstyle_pack_quantity", "urbanstyle_box_quantity")
    def _check_urbanstyle_pack_quantities(self):
        for template in self.filtered("urbanstyle_is_finished_product"):
            if template.urbanstyle_pack_quantity < 1 or template.urbanstyle_box_quantity < 1:
                raise ValidationError(_("El paquete y la caja deben contener al menos una unidad."))
            if template.urbanstyle_box_quantity <= template.urbanstyle_pack_quantity:
                raise ValidationError(_("La caja debe contener más unidades que el paquete."))
            if template.urbanstyle_box_quantity % template.urbanstyle_pack_quantity:
                raise ValidationError(_("La cantidad por caja debe ser múltiplo de la cantidad por paquete."))

    @api.constrains("urbanstyle_margin_pct")
    def _check_urbanstyle_margin(self):
        if any(template.urbanstyle_margin_pct < 0 for template in self):
            raise ValidationError(_("El margen de ganancia no puede ser negativo."))

    @api.model_create_multi
    def create(self, vals_list):
        templates = super().create(vals_list)
        templates._ensure_urbanstyle_material_kit()
        templates._ensure_urbanstyle_sales_uoms()
        templates._urbanstyle_recompute_sale_prices()
        return templates

    def write(self, vals):
        vals = dict(vals)
        if "list_price" in vals and not self.env.context.get("urbanstyle_auto_price_update"):
            vals.setdefault("urbanstyle_auto_price", False)
        result = super().write(vals)
        if self.env.context.get("urbanstyle_auto_price_update"):
            return result
        if {"urbanstyle_is_finished_product", "urbanstyle_pack_quantity", "urbanstyle_box_quantity", "uom_id"} & vals.keys():
            self._ensure_urbanstyle_material_kit()
            self._ensure_urbanstyle_sales_uoms()
        if {"urbanstyle_is_finished_product", "urbanstyle_auto_price", "urbanstyle_margin_pct"} & vals.keys():
            self._urbanstyle_recompute_sale_prices()
        if "standard_price" in vals:
            dependent_templates = self.env["mrp.bom.line"].search(
                [("product_id.product_tmpl_id", "in", self.ids)]
            ).mapped("bom_id.product_tmpl_id")
            dependent_templates._urbanstyle_recompute_sale_prices()
        return result

    @api.depends("urbanstyle_min_stock", "product_variant_ids.qty_available")
    @api.depends_context("company")
    def _compute_urbanstyle_low_stock(self):
        for template in self:
            quantity_available = sum(template.product_variant_ids.mapped("qty_available"))
            template.urbanstyle_low_stock = (
                template.urbanstyle_is_raw_material
                and quantity_available < template.urbanstyle_min_stock
            )

    @api.model
    def _search_urbanstyle_low_stock(self, operator, value):
        if operator not in ("=", "!=") or value not in (True, False):
            return NotImplemented
        raw_templates = self.search([("urbanstyle_is_raw_material", "=", True)])
        low_stock_templates = raw_templates.filtered(
            lambda template: sum(template.product_variant_ids.mapped("qty_available"))
            < template.urbanstyle_min_stock
        )
        match = (operator == "=") == value
        return [("id", "in" if match else "not in", low_stock_templates.ids)]
