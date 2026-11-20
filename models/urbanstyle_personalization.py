from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


PERSONALIZATION_TECHNIQUE_SELECTION = [
    ("screen_print", "Serigrafía"),
    ("sublimation", "Sublimación"),
    ("vinyl", "Vinilo o transfer"),
    ("embroidery", "Bordado"),
    ("applique", "Aplicación o parche"),
    ("other", "Otra técnica"),
]


class UrbanStyleCustomizationSpecialty(models.Model):
    _name = "urbanstyle.customization.specialty"
    _description = "Especialización de personalización UrbanStyle"
    _order = "name"

    name = fields.Char(string="Especialización", required=True, translate=True)
    code = fields.Char(string="Código", index=True)
    description = fields.Text(string="Descripción")
    active = fields.Boolean(default=True)


class UrbanStylePrintDesign(models.Model):
    _name = "urbanstyle.print.design"
    _description = "Diseño o estampado personalizado UrbanStyle"
    _order = "name"

    name = fields.Char(string="Diseño o estampado", required=True, translate=True)
    reference = fields.Char(string="Referencia", index=True)
    technique = fields.Selection(
        PERSONALIZATION_TECHNIQUE_SELECTION,
        string="Técnica",
        required=True,
        default="screen_print",
    )
    image_1920 = fields.Image(string="Muestra del diseño", max_width=1920, max_height=1920)
    description = fields.Text(string="Detalles del diseño")
    extra_cost = fields.Monetary(
        string="Recargo por prenda",
        currency_field="currency_id",
        help="Se suma al precio unitario cuando este diseño se selecciona en una línea de venta.",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Moneda",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    specialty_ids = fields.Many2many(
        "urbanstyle.customization.specialty",
        "urbanstyle_print_design_specialty_rel",
        "design_id",
        "specialty_id",
        string="Especializaciones requeridas",
    )
    active = fields.Boolean(default=True)

    @api.constrains("extra_cost")
    def _check_extra_cost(self):
        if any(design.extra_cost < 0 for design in self):
            raise ValidationError(_("El recargo del diseño no puede ser negativo."))
