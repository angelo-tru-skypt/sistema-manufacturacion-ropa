from odoo import _, Command, api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    urbanstyle_is_finished_product = fields.Boolean(
        related="product_id.product_tmpl_id.urbanstyle_is_finished_product",
        string="Prenda UrbanStyle",
    )
    urbanstyle_print_design_id = fields.Many2one(
        "urbanstyle.print.design",
        string="Estampado o diseño solicitado",
        ondelete="restrict",
    )
    urbanstyle_customization_specialty_ids = fields.Many2many(
        "urbanstyle.customization.specialty",
        "urbanstyle_sale_line_specialty_rel",
        "sale_line_id",
        "specialty_id",
        string="Especializaciones requeridas",
    )
    urbanstyle_customization_notes = fields.Text(string="Instrucciones de personalización")
    urbanstyle_design_surcharge = fields.Monetary(
        string="Recargo del diseño",
        currency_field="currency_id",
        compute="_compute_urbanstyle_design_surcharge",
        help="Recargo por prenda convertido a la moneda de la orden. Se incluye en el precio unitario.",
    )

    @api.depends(
        "urbanstyle_print_design_id",
        "urbanstyle_print_design_id.extra_cost",
        "urbanstyle_print_design_id.currency_id",
        "currency_id",
        "company_id",
        "order_id.date_order",
    )
    def _compute_urbanstyle_design_surcharge(self):
        for line in self:
            design = line.urbanstyle_print_design_id
            currency = line.currency_id or line.company_id.currency_id or self.env.company.currency_id
            if not design or not design.currency_id or design.currency_id == currency:
                line.urbanstyle_design_surcharge = design.extra_cost if design else 0.0
                continue
            line.urbanstyle_design_surcharge = design.currency_id._convert(
                design.extra_cost,
                currency,
                line.company_id or self.env.company,
                line.order_id.date_order or fields.Date.context_today(line),
            )

    def _urbanstyle_has_manual_price(self):
        self.ensure_one()
        currency = self.currency_id or self.company_id.currency_id or self.env.company.currency_id
        return currency.compare_amounts(self.technical_price_unit, self.price_unit) != 0

    @api.depends(
        "product_id",
        "product_uom_id",
        "product_uom_qty",
        "urbanstyle_design_surcharge",
    )
    def _compute_price_unit(self):
        manually_priced_lines = self.filtered(lambda line: line._urbanstyle_has_manual_price())
        super()._compute_price_unit()
        for line in self:
            if line in manually_priced_lines and not line.urbanstyle_print_design_id:
                continue
            if line.urbanstyle_design_surcharge:
                currency = line.currency_id or line.company_id.currency_id or self.env.company.currency_id
                line.price_unit = currency.round(line.price_unit + line.urbanstyle_design_surcharge)
                line.technical_price_unit = line.price_unit

    @api.depends(
        "product_id",
        "linked_line_id",
        "linked_line_ids",
        "urbanstyle_print_design_id",
        "urbanstyle_customization_specialty_ids",
        "urbanstyle_customization_notes",
    )
    def _compute_name(self):
        super()._compute_name()

    def _get_sale_order_line_multiline_description_sale(self):
        description = super()._get_sale_order_line_multiline_description_sale()
        if self.urbanstyle_print_design_id:
            description += _("\nDiseño solicitado: %(design)s", design=self.urbanstyle_print_design_id.name)
        if self.urbanstyle_customization_specialty_ids:
            description += _(
                "\nEspecializaciones: %(specialties)s",
                specialties=", ".join(self.urbanstyle_customization_specialty_ids.mapped("name")),
            )
        if self.urbanstyle_customization_notes:
            description += _(
                "\nInstrucciones de personalización: %(notes)s",
                notes=self.urbanstyle_customization_notes,
            )
        return description

    @api.onchange("urbanstyle_print_design_id")
    def _onchange_urbanstyle_print_design_id(self):
        for line in self:
            if line.urbanstyle_print_design_id:
                line.urbanstyle_customization_specialty_ids = line.urbanstyle_print_design_id.specialty_ids

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            design_id = vals.get("urbanstyle_print_design_id")
            if design_id and "urbanstyle_customization_specialty_ids" not in vals:
                design = self.env["urbanstyle.print.design"].browse(design_id)
                vals["urbanstyle_customization_specialty_ids"] = [
                    Command.set(design.specialty_ids.ids)
                ]
        return super().create(vals_list)

    def write(self, vals):
        result = super().write(vals)
        if "urbanstyle_print_design_id" in vals and "urbanstyle_customization_specialty_ids" not in vals:
            for line in self.filtered("urbanstyle_print_design_id"):
                line.urbanstyle_customization_specialty_ids = [
                    Command.set(line.urbanstyle_print_design_id.specialty_ids.ids)
                ]
        return result
