from odoo import api, fields, models

from .mrp_routing_workcenter import FIXATION_METHOD_SELECTION, PLEAT_TYPE_SELECTION, TEXTILE_OPERATION_FIELDS


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    is_pleating_operation = fields.Boolean(string="¿Es operación de plisado?")
    pleat_type = fields.Selection(PLEAT_TYPE_SELECTION, string="Tipo de pliegue", copy=False)
    pleat_width_cm = fields.Float(string="Ancho del pliegue (cm)", digits=(16, 2), copy=False)
    pleat_distance_cm = fields.Float(string="Distancia entre pliegues (cm)", digits=(16, 2), copy=False)
    pleat_count = fields.Integer(string="Cantidad de pliegues", copy=False)
    fabric_type = fields.Char(string="Material o tipo de tela", copy=False)
    fixation_method = fields.Selection(FIXATION_METHOD_SELECTION, string="Método de fijación", copy=False)
    technical_notes = fields.Text(string="Notas técnicas e instrucciones", copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        """Snapshot the operation's textile settings when Odoo creates its work order."""
        operations = self.env["mrp.routing.workcenter"]
        for vals in vals_list:
            operation_id = vals.get("operation_id")
            if not operation_id:
                continue
            operation = operations.browse(operation_id)
            for field_name in TEXTILE_OPERATION_FIELDS:
                vals.setdefault(field_name, operation[field_name])
        return super().create(vals_list)
