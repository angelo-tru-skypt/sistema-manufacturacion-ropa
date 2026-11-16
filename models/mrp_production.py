from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    is_urbanstyle_demo = fields.Boolean(
        string="Dato de demostración UrbanStyle RD",
        default=False,
        copy=False,
        index=True,
    )
