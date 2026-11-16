from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_urbanstyle_demo = fields.Boolean(
        string="Dato de demostración UrbanStyle RD",
        default=False,
        copy=False,
        index=True,
    )

class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    is_urbanstyle_demo = fields.Boolean(
        string="Dato de demostración UrbanStyle RD",
        default=False,
        copy=False,
        index=True,
    )


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    is_urbanstyle_demo = fields.Boolean(
        string="Dato de demostración UrbanStyle RD",
        default=False,
        copy=False,
        index=True,
    )
