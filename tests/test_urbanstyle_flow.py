from odoo import Command
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestUrbanStyleFlow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["urbanstyle.demo.data.wizard"].create({}).action_load_demo_data()
        cls.skirt = cls.env["product.template"].search(
            [("name", "=", "Falda plisada clásica"), ("is_urbanstyle_demo", "=", True)], limit=1
        )
        cls.bom = cls.env["mrp.bom"].search(
            [("product_tmpl_id", "=", cls.skirt.id), ("is_urbanstyle_demo", "=", True)], limit=1
        )

    def test_demo_catalog_load_is_idempotent(self):
        Partner = self.env["res.partner"]
        Template = self.env["product.template"]
        Workcenter = self.env["mrp.workcenter"]
        before = (
            Partner.search_count([("is_urbanstyle_demo", "=", True)]),
            Template.search_count([("is_urbanstyle_demo", "=", True)]),
            Workcenter.search_count([("is_urbanstyle_demo", "=", True)]),
            self.env["mrp.bom"].search_count([("is_urbanstyle_demo", "=", True)]),
        )
        self.env["urbanstyle.demo.data.wizard"].create({}).action_load_demo_data()
        after = (
            Partner.search_count([("is_urbanstyle_demo", "=", True)]),
            Template.search_count([("is_urbanstyle_demo", "=", True)]),
            Workcenter.search_count([("is_urbanstyle_demo", "=", True)]),
            self.env["mrp.bom"].search_count([("is_urbanstyle_demo", "=", True)]),
        )
        self.assertEqual(after, before)

    def test_pleating_settings_copy_to_real_workorder(self):
        operation = self.bom.operation_ids.filtered("is_pleating_operation")
        self.assertEqual(operation.pleat_type, "box")
        self.assertEqual(operation.pleat_width_cm, 2.5)
        self.assertEqual(operation.pleat_distance_cm, 1.5)
        self.assertEqual(operation.pleat_count, 24)

        product = self.skirt.product_variant_ids.filtered(
            lambda variant: "M" in variant.product_template_attribute_value_ids.mapped("product_attribute_value_id.name")
            and "Negro" in variant.product_template_attribute_value_ids.mapped("product_attribute_value_id.name")
        )[:1]
        production = self.env["mrp.production"].create(
            {
                "product_id": product.id,
                "product_qty": 1,
                "product_uom_id": product.uom_id.id,
                "bom_id": self.bom.id,
                "picking_type_id": self.bom.picking_type_id.id,
                "company_id": self.env.company.id,
            }
        )
        production.action_confirm()
        workorder = production.workorder_ids.filtered("is_pleating_operation")
        self.assertTrue(workorder)
        self.assertEqual(workorder.pleat_type, operation.pleat_type)
        self.assertEqual(workorder.pleat_width_cm, operation.pleat_width_cm)
        self.assertEqual(workorder.pleat_distance_cm, operation.pleat_distance_cm)
        self.assertEqual(workorder.pleat_count, operation.pleat_count)

    def test_quality_points_are_attached_to_production_steps(self):
        checked_operations = self.bom.operation_ids.filtered("quality_point_ids")
        self.assertEqual(len(checked_operations), 4)
        self.assertTrue(
            self.env["quality.point"].search_count(
                [("title", "=", "Inspección de materias primas al recibir - UrbanStyle RD")]
            )
        )
