from odoo import _, Command, api, fields, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    is_urbanstyle_demo = fields.Boolean(
        string="Dato de demostración UrbanStyle RD",
        default=False,
        copy=False,
        index=True,
    )
    urbanstyle_print_design_id = fields.Many2one(
        "urbanstyle.print.design",
        string="Diseño solicitado",
        ondelete="restrict",
        copy=True,
        tracking=True,
    )
    urbanstyle_customization_specialty_ids = fields.Many2many(
        "urbanstyle.customization.specialty",
        "urbanstyle_production_specialty_rel",
        "production_id",
        "specialty_id",
        string="Especializaciones requeridas",
        copy=True,
    )
    urbanstyle_customization_notes = fields.Text(
        string="Instrucciones de personalización",
        copy=True,
        tracking=True,
    )
    urbanstyle_customization_currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        string="Moneda",
    )
    urbanstyle_customization_extra_cost = fields.Monetary(
        string="Recargo del diseño por prenda",
        currency_field="urbanstyle_customization_currency_id",
        copy=True,
        tracking=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        SaleOrderLine = self.env["sale.order.line"]
        Company = self.env["res.company"]
        for vals in vals_list:
            sale_line = SaleOrderLine.browse(vals.get("sale_line_id")).exists()
            if not sale_line:
                continue
            company = Company.browse(vals.get("company_id")) or sale_line.company_id or self.env.company
            customization_values = {
                "urbanstyle_print_design_id": sale_line.urbanstyle_print_design_id.id,
                "urbanstyle_customization_specialty_ids": [
                    Command.set(sale_line.urbanstyle_customization_specialty_ids.ids)
                ],
                "urbanstyle_customization_notes": sale_line.urbanstyle_customization_notes,
                "urbanstyle_customization_extra_cost": sale_line.currency_id._convert(
                    sale_line.urbanstyle_design_surcharge,
                    company.currency_id,
                    company,
                    sale_line.order_id.date_order or fields.Date.context_today(sale_line),
                ),
            }
            for field_name, value in customization_values.items():
                vals.setdefault(field_name, value)
        return super().create(vals_list)

    @api.onchange("urbanstyle_print_design_id")
    def _onchange_urbanstyle_print_design_id(self):
        for production in self:
            design = production.urbanstyle_print_design_id
            if not design:
                continue
            production.urbanstyle_customization_specialty_ids = design.specialty_ids
            company = production.company_id or self.env.company
            production.urbanstyle_customization_extra_cost = design.currency_id._convert(
                design.extra_cost,
                company.currency_id,
                company,
                fields.Date.context_today(production),
            )

    def _get_backorder_mo_vals(self):
        self.ensure_one()
        vals = super()._get_backorder_mo_vals()
        vals.update(
            {
                "urbanstyle_print_design_id": self.urbanstyle_print_design_id.id,
                "urbanstyle_customization_specialty_ids": [
                    Command.set(self.urbanstyle_customization_specialty_ids.ids)
                ],
                "urbanstyle_customization_notes": self.urbanstyle_customization_notes,
                "urbanstyle_customization_extra_cost": self.urbanstyle_customization_extra_cost,
            }
        )
        return vals

    def action_confirm(self):
        for production in self.filtered(
            lambda order: order.product_id.product_tmpl_id.urbanstyle_is_finished_product
        ):
            template = production.product_id.product_tmpl_id
            if not template._urbanstyle_bom_is_ready(production.bom_id):
                raise UserError(
                    _(
                        "Completa el kit de %(product)s antes de confirmar la fabricación. "
                        "Debe incluir materiales y operaciones con área de trabajo y tiempo."
                    )
                    % {"product": production.product_id.display_name}
                )
        return super().action_confirm()
