from odoo import api, fields, models, _


class UrbanStyleDashboard(models.Model):
    _name = "urbanstyle.dashboard"
    _description = "Panel ejecutivo UrbanStyle RD"

    name = fields.Char(default="UrbanStyle RD", required=True)
    manufacturing_pending = fields.Integer(compute="_compute_kpis", string="Órdenes pendientes")
    manufacturing_in_progress = fields.Integer(compute="_compute_kpis", string="Órdenes en producción")
    manufacturing_done = fields.Integer(compute="_compute_kpis", string="Órdenes completadas")
    finished_product_count = fields.Integer(
        compute="_compute_kpis", string="Modelos de prendas"
    )
    produced_units = fields.Float(
        compute="_compute_kpis", string="Unidades fabricadas", digits="Product Unit"
    )
    quality_checks_pending = fields.Integer(compute="_compute_kpis", string="Controles pendientes")
    raw_materials_low = fields.Integer(compute="_compute_kpis", string="Materias primas con stock bajo")
    finished_stock_units = fields.Float(
        compute="_compute_kpis", string="Prendas disponibles", digits="Product Unit"
    )

    @api.depends_context("uid", "company")
    def _compute_kpis(self):
        Production = self.env["mrp.production"]
        QualityCheck = self.env["quality.check"]
        ProductTemplate = self.env["product.template"]

        finished_product_count = ProductTemplate.search_count(
            [("urbanstyle_is_finished_product", "=", True)]
        )
        pending = Production.search_count([("state", "=", "confirmed")])
        in_progress = Production.search_count([("state", "=", "progress")])
        done_orders = Production.search([("state", "=", "done")])
        pending_checks = QualityCheck.search_count([("quality_state", "=", "none")])

        low_stock_count = ProductTemplate.search_count(
            [
                ("urbanstyle_is_raw_material", "=", True),
                ("urbanstyle_low_stock", "=", True),
            ]
        )

        finished_products = self.env["product.product"].search(
            [
                ("product_tmpl_id.urbanstyle_is_finished_product", "=", True),
                ("is_storable", "=", True),
            ]
        )
        finished_stock = sum(
            quantity
            for quantity in finished_products.mapped("qty_available")
            if quantity > 0
        )

        for dashboard in self:
            dashboard.finished_product_count = finished_product_count
            dashboard.manufacturing_pending = pending
            dashboard.manufacturing_in_progress = in_progress
            dashboard.manufacturing_done = len(done_orders)
            dashboard.produced_units = sum(done_orders.mapped("qty_produced"))
            dashboard.quality_checks_pending = pending_checks
            dashboard.raw_materials_low = low_stock_count
            dashboard.finished_stock_units = finished_stock

    def _open_records(self, model, name, domain=None, context=None, view_mode="list,form"):
        return {
            "type": "ir.actions.act_window",
            "name": name,
            "res_model": model,
            "view_mode": view_mode,
            "domain": domain or [],
            "context": context or {},
        }

    def action_open_pending_productions(self):
        return self._open_records(
            "mrp.production", _("Órdenes de fabricación pendientes"), [("state", "=", "confirmed")]
        )

    def action_open_progress_productions(self):
        return self._open_records(
            "mrp.production", _("Órdenes en producción"), [("state", "=", "progress")]
        )

    def action_open_done_productions(self):
        return self._open_records(
            "mrp.production", _("Órdenes completadas"), [("state", "=", "done")]
        )

    def action_open_quality_checks(self):
        return self._open_records(
            "quality.check",
            _("Controles de calidad pendientes"),
            [("quality_state", "=", "none")],
        )

    def action_open_low_stock_materials(self):
        return self._open_records(
            "product.template",
            _("Materias primas textiles"),
            [
                ("urbanstyle_is_raw_material", "=", True),
                ("urbanstyle_low_stock", "=", True),
            ],
        )

    def action_open_finished_stock(self):
        return self._open_records(
            "stock.quant",
            _("Prendas terminadas en inventario"),
            [
                ("product_tmpl_id.urbanstyle_is_finished_product", "=", True),
                ("quantity", ">", 0),
                ("location_id.usage", "=", "internal"),
            ],
        )

    def action_open_workorders(self):
        return self.env["ir.actions.actions"]._for_xml_id("mrp.mrp_workorder_todo")

    def action_open_shop_floor(self):
        return self.env["ir.actions.actions"]._for_xml_id("mrp_workorder.mrp_workorder_action_tablet")

    def action_open_inventory(self):
        return self.env["ir.actions.actions"]._for_xml_id("stock.stock_quant_action")

    def action_open_purchase_orders(self):
        return self.env["ir.actions.actions"]._for_xml_id(
            "urbanstyle_textile_demo.action_urbanstyle_purchase_orders"
        )

    def action_open_demo_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Cargar datos de demostración"),
            "res_model": "urbanstyle.demo.data.wizard",
            "view_mode": "form",
            "target": "new",
        }
