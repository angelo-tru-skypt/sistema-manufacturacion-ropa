from odoo import fields, models


TEXTILE_OPERATION_FIELDS = (
    "is_pleating_operation",
    "pleat_type",
    "pleat_width_cm",
    "pleat_distance_cm",
    "pleat_count",
    "fabric_type",
    "fixation_method",
    "technical_notes",
)

PLEAT_TYPE_SELECTION = [
    ("box", "Tabla"),
    ("accordion", "Acordeón"),
    ("knife", "Encontrado / Cuchilla"),
    ("sunburst", "Sol"),
    ("other", "Otro"),
]
FIXATION_METHOD_SELECTION = [
    ("steam", "Vapor industrial"),
    ("heat_press", "Termofijado"),
    ("basting", "Hilvanado"),
    ("chemical", "Resina / Químico"),
]


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    is_pleating_operation = fields.Boolean(string="¿Es operación de plisado?")
    pleat_type = fields.Selection(PLEAT_TYPE_SELECTION, string="Tipo de pliegue")
    pleat_width_cm = fields.Float(string="Ancho del pliegue (cm)", digits=(16, 2))
    pleat_distance_cm = fields.Float(string="Distancia entre pliegues (cm)", digits=(16, 2))
    pleat_count = fields.Integer(string="Cantidad de pliegues")
    fabric_type = fields.Char(string="Material o tipo de tela")
    fixation_method = fields.Selection(FIXATION_METHOD_SELECTION, string="Método de fijación")
    technical_notes = fields.Text(string="Notas técnicas e instrucciones")
