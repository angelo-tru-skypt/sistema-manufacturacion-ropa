from odoo import api, fields, models


class UomUom(models.Model):
    _inherit = "uom.uom"

    urbanstyle_product_tmpl_id = fields.Many2one(
        "product.template",
        string="Prenda UrbanStyle",
        copy=False,
        index=True,
        ondelete="cascade",
    )
    urbanstyle_packaging_type = fields.Selection(
        [("pack", "Paquete"), ("box", "Caja")],
        string="Presentación de venta UrbanStyle",
        copy=False,
        index=True,
    )


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    urbanstyle_is_material_kit = fields.Boolean(
        string="Kit de materiales UrbanStyle",
        default=False,
        copy=False,
        index=True,
        help="Fórmula de fabricación de la prenda con consumos y operaciones por unidad.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        boms = super().create(vals_list)
        boms.mapped("product_tmpl_id")._urbanstyle_recompute_sale_prices()
        return boms

    def write(self, vals):
        templates = self.mapped("product_tmpl_id")
        result = super().write(vals)
        (templates | self.mapped("product_tmpl_id"))._urbanstyle_recompute_sale_prices()
        return result

    def unlink(self):
        templates = self.mapped("product_tmpl_id")
        result = super().unlink()
        templates._urbanstyle_recompute_sale_prices()
        return result


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines.mapped("bom_id.product_tmpl_id")._urbanstyle_recompute_sale_prices()
        return lines

    def write(self, vals):
        templates = self.mapped("bom_id.product_tmpl_id")
        result = super().write(vals)
        (templates | self.mapped("bom_id.product_tmpl_id"))._urbanstyle_recompute_sale_prices()
        return result

    def unlink(self):
        templates = self.mapped("bom_id.product_tmpl_id")
        result = super().unlink()
        templates._urbanstyle_recompute_sale_prices()
        return result


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    @api.model_create_multi
    def create(self, vals_list):
        operations = super().create(vals_list)
        operations.mapped("bom_id.product_tmpl_id")._urbanstyle_recompute_sale_prices()
        return operations

    def write(self, vals):
        templates = self.mapped("bom_id.product_tmpl_id")
        result = super().write(vals)
        (templates | self.mapped("bom_id.product_tmpl_id"))._urbanstyle_recompute_sale_prices()
        return result

    def unlink(self):
        templates = self.mapped("bom_id.product_tmpl_id")
        result = super().unlink()
        templates._urbanstyle_recompute_sale_prices()
        return result


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    def write(self, vals):
        result = super().write(vals)
        if {"costs_hour", "time_efficiency", "time_start", "time_stop", "capacity_ids"} & vals.keys():
            templates = self.env["mrp.routing.workcenter"].search(
                [("workcenter_id", "in", self.ids)]
            ).mapped("bom_id.product_tmpl_id")
            templates._urbanstyle_recompute_sale_prices()
        return result


class ProductProduct(models.Model):
    _inherit = "product.product"

    def write(self, vals):
        result = super().write(vals)
        if "standard_price" in vals:
            templates = self.env["mrp.bom.line"].search(
                [("product_id", "in", self.ids)]
            ).mapped("bom_id.product_tmpl_id")
            templates._urbanstyle_recompute_sale_prices()
        return result
