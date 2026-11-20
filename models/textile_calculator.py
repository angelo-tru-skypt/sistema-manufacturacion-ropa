from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .textile_material_catalog import URBANSTYLE_MATERIAL_USAGE_SELECTION


class UrbanStyleTextileCalculator(models.TransientModel):
    _name = "urbanstyle.textile.calculator"
    _description = "Calculadora textil UrbanStyle"

    project_name = fields.Char(string="Nombre del proyecto", required=True, default="Proyecto textil")
    filter_composition = fields.Char(string="Composición contiene")
    filter_texture = fields.Char(string="Textura contiene")
    filter_color = fields.Char(string="Color contiene")
    filter_usage = fields.Selection(
        URBANSTYLE_MATERIAL_USAGE_SELECTION,
        string="Utilización",
    )
    filter_weight_min_gsm = fields.Float(string="Peso mínimo (g/m²)", digits=(16, 2))
    filter_weight_max_gsm = fields.Float(string="Peso máximo (g/m²)", digits=(16, 2))
    eligible_material_ids = fields.Many2many(
        "product.template",
        compute="_compute_eligible_material_ids",
        string="Telas compatibles",
    )
    material_id = fields.Many2one(
        "product.template",
        string="Tela a calcular",
        domain="[('id', 'in', eligible_material_ids)]",
    )
    quantity = fields.Integer(string="Cantidad de prendas o piezas", default=1, required=True)
    project_length_cm = fields.Float(
        string="Largo por pieza (cm)",
        digits=(16, 2),
        default=100.0,
        required=True,
    )
    project_width_cm = fields.Float(
        string="Ancho por pieza (cm)",
        digits=(16, 2),
        default=100.0,
        required=True,
    )
    waste_percent = fields.Float(
        string="Desperdicio estimado (%)",
        digits=(16, 2),
        default=10.0,
        help="Porcentaje adicional para cortes, empalmes y desperdicio.",
    )
    fabric_width_cm = fields.Float(
        string="Ancho del rollo (cm)",
        compute="_compute_estimates",
        digits=(16, 2),
    )
    estimated_area_m2 = fields.Float(
        string="Superficie estimada (m²)",
        compute="_compute_estimates",
        digits=(16, 3),
    )
    estimated_linear_m = fields.Float(
        string="Consumo estimado (m lineales)",
        compute="_compute_estimates",
        digits=(16, 3),
    )

    @api.depends(
        "filter_composition",
        "filter_texture",
        "filter_color",
        "filter_usage",
        "filter_weight_min_gsm",
        "filter_weight_max_gsm",
    )
    def _compute_eligible_material_ids(self):
        ProductTemplate = self.env["product.template"]
        for wizard in self:
            domain = [
                ("urbanstyle_is_raw_material", "=", True),
                ("urbanstyle_material_kind", "=", "fabric"),
            ]
            if wizard.filter_composition:
                domain.append(("urbanstyle_composition", "ilike", wizard.filter_composition.strip()))
            if wizard.filter_texture:
                domain.append(("urbanstyle_texture", "ilike", wizard.filter_texture.strip()))
            if wizard.filter_color:
                domain.append(("urbanstyle_material_color", "ilike", wizard.filter_color.strip()))
            if wizard.filter_usage:
                domain.append(("urbanstyle_usage", "=", wizard.filter_usage))
            if wizard.filter_weight_min_gsm > 0:
                domain.append(("urbanstyle_weight_gsm", ">=", wizard.filter_weight_min_gsm))
            if wizard.filter_weight_max_gsm > 0:
                domain.append(("urbanstyle_weight_gsm", "<=", wizard.filter_weight_max_gsm))
            wizard.eligible_material_ids = ProductTemplate.search(domain)

    @api.onchange(
        "filter_composition",
        "filter_texture",
        "filter_color",
        "filter_usage",
        "filter_weight_min_gsm",
        "filter_weight_max_gsm",
    )
    def _onchange_material_filters(self):
        self.material_id = False

    @api.depends(
        "material_id",
        "material_id.urbanstyle_fabric_width_in",
        "quantity",
        "project_length_cm",
        "project_width_cm",
        "waste_percent",
    )
    def _compute_estimates(self):
        for wizard in self:
            roll_width_cm = wizard.material_id.urbanstyle_fabric_width_in * 2.54
            area_m2 = 0.0
            linear_m = 0.0
            if wizard.quantity > 0 and wizard.project_length_cm > 0 and wizard.project_width_cm > 0:
                area_m2 = (
                    wizard.project_length_cm
                    * wizard.project_width_cm
                    * wizard.quantity
                    / 10000.0
                    * (1.0 + wizard.waste_percent / 100.0)
                )
                if roll_width_cm > 0:
                    linear_m = area_m2 / (roll_width_cm / 100.0)
            wizard.fabric_width_cm = roll_width_cm
            wizard.estimated_area_m2 = area_m2
            wizard.estimated_linear_m = linear_m

    @api.constrains("quantity", "project_length_cm", "project_width_cm", "waste_percent")
    def _check_calculator_dimensions(self):
        for wizard in self:
            if wizard.quantity < 1 or wizard.project_length_cm <= 0 or wizard.project_width_cm <= 0:
                raise ValidationError(_("La cantidad y las dimensiones deben ser mayores que cero."))
            if wizard.waste_percent < 0 or wizard.waste_percent > 100:
                raise ValidationError(_("El desperdicio debe estar entre 0% y 100%."))

    @api.constrains("filter_weight_min_gsm", "filter_weight_max_gsm")
    def _check_weight_filter(self):
        for wizard in self:
            if (
                wizard.filter_weight_min_gsm < 0
                or wizard.filter_weight_max_gsm < 0
                or (
                    wizard.filter_weight_max_gsm
                    and wizard.filter_weight_min_gsm > wizard.filter_weight_max_gsm
                )
            ):
                raise ValidationError(_("El rango de peso de la tela no es válido."))
