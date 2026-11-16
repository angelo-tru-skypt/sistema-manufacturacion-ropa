from odoo import api, fields, models


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
        help="Incluye la prenda en el catálogo textil y los indicadores de existencias UrbanStyle.",
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
