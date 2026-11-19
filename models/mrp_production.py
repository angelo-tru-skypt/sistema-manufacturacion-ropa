from odoo import _, fields, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    is_urbanstyle_demo = fields.Boolean(
        string="Dato de demostración UrbanStyle RD",
        default=False,
        copy=False,
        index=True,
    )

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
