from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        for order in self:
            for line in order.order_line.filtered(
                lambda sale_line: not sale_line.display_type
                and sale_line.product_id.product_tmpl_id.urbanstyle_is_finished_product
            ):
                template = line.product_id.product_tmpl_id
                bom = template.urbanstyle_kit_bom_ids.filtered(
                    lambda candidate: candidate.product_id == line.product_id
                )[:1]
                if not bom:
                    bom = template.urbanstyle_kit_bom_ids.filtered(
                        lambda candidate: not candidate.product_id
                    )[:1]
                if not template._urbanstyle_bom_is_ready(
                    bom,
                    require_costed_operations=template.urbanstyle_auto_price,
                ):
                    raise UserError(
                        _(
                            "No se puede confirmar la venta de %(product)s. "
                            "Completa primero su kit con materiales y operaciones. "
                            "Para calcular el precio automáticamente, cada área debe tener un costo por hora mayor que cero."
                        )
                        % {"product": line.product_id.display_name}
                    )
        return super().action_confirm()
