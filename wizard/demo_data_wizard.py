from collections import defaultdict

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError


class UrbanStyleDemoDataWizard(models.TransientModel):
    _name = "urbanstyle.demo.data.wizard"
    _description = "Carga de datos demostrativos UrbanStyle RD"

    name = fields.Char(default="UrbanStyle RD", readonly=True)

    def _mark_result(self, counts, label, created):
        bucket = "created" if created else "existing"
        counts[bucket][label] += 1

    def _get_or_create_demo(self, model_name, name, values, counts, label=None, default_code=None):
        model = self.env[model_name].with_company(self.env.company)
        base_domain = [("is_urbanstyle_demo", "=", True)]
        if default_code and "default_code" in model._fields:
            record = model.search(base_domain + [("default_code", "=", default_code)], limit=1)
            if not record and model.search([("default_code", "=", default_code)], limit=1):
                # Preserve a manually created product with the same internal
                # reference and give the demo item a stable, unique reference.
                candidate = "%s-DEMO" % default_code
                suffix = 2
                while model.search([("default_code", "=", candidate)], limit=1):
                    candidate = "%s-DEMO-%s" % (default_code, suffix)
                    suffix += 1
                values = dict(values, default_code=candidate)
        else:
            record = model.browse()
        if not record and "name" in model._fields:
            record = model.search(base_domain + [("name", "=", name)], limit=1)
        if record:
            self._mark_result(counts, label or name, False)
            return record, False
        values = dict(values)
        values["is_urbanstyle_demo"] = True
        record = model.create(values)
        self._mark_result(counts, label or name, True)
        return record, True

    def _get_or_create_named(self, model_name, name, values=None):
        model = self.env[model_name].with_company(self.env.company)
        record = model.search([("name", "=", name)], limit=1)
        if record:
            return record
        create_values = dict(values or {})
        create_values["name"] = name
        return model.create(create_values)

    def _find_or_create_supplier(self, name, counts):
        partner, created = self._get_or_create_demo(
            "res.partner",
            name,
            {"name": name, "supplier_rank": 1, "company_type": "company"},
            counts,
            label="Proveedores",
        )
        return partner, created

    def _ensure_attribute(self, name, values):
        Attribute = self.env["product.attribute"].with_company(self.env.company)
        attribute = Attribute.search([("name", "=", name)], limit=1)
        if attribute:
            existing_values = set(attribute.value_ids.mapped("name"))
            if attribute.create_variant != "always" or not set(values).issubset(existing_values):
                # Keep pre-existing attributes untouched if their variant mode or
                # value set differs from this demo's requirements.
                name = _("%(name)s (UrbanStyle RD)", name=name)
                attribute = Attribute.search([("name", "=", name)], limit=1)
        if not attribute:
            attribute = Attribute.create({"name": name, "create_variant": "always"})
        result = {}
        for value_name in values:
            value = self.env["product.attribute.value"].search(
                [("attribute_id", "=", attribute.id), ("name", "=", value_name)], limit=1
            )
            if not value:
                value = self.env["product.attribute.value"].create(
                    {"attribute_id": attribute.id, "name": value_name}
                )
            result[value_name] = value
        return attribute, result

    def _set_variant_references(self, template, code_prefix):
        size_codes = {"XS": "XS", "S": "S", "M": "M", "L": "L", "XL": "XL"}
        color_codes = {"Negro": "NE", "Blanco": "BL", "Beige": "BE", "Azul": "AZ"}
        for variant in template.product_variant_ids:
            size = variant.product_template_attribute_value_ids.filtered(
                lambda value: value.attribute_id.name.startswith("Talla")
            ).mapped("product_attribute_value_id.name")
            color = variant.product_template_attribute_value_ids.filtered(
                lambda value: value.attribute_id.name.startswith("Color")
            ).mapped("product_attribute_value_id.name")
            if size and color and not variant.default_code:
                variant.default_code = "US-%s-%s-%s" % (
                    code_prefix,
                    size_codes.get(size[0], size[0].upper()),
                    color_codes.get(color[0], color[0][:2].upper()),
                )

    def _ensure_initial_stock(self, template, quantity, stock_location, counts):
        variant = template.product_variant_id
        Quant = self.env["stock.quant"].with_company(self.env.company).with_context(
            inventory_mode=True,
            inventory_name=_("UrbanStyle RD - inventario inicial demostrativo"),
        )
        existing_quant = Quant.search(
            [
                ("product_id", "=", variant.id),
                ("location_id", "=", stock_location.id),
                ("lot_id", "=", False),
                ("package_id", "=", False),
                ("owner_id", "=", False),
            ],
            limit=1,
        )
        if existing_quant:
            return
        quant = Quant.create(
            {
                "product_id": variant.id,
                "location_id": stock_location.id,
                "inventory_quantity": quantity,
            }
        )
        quant.action_apply_inventory()
        self._mark_result(counts, "Ajustes iniciales de inventario", True)

    def _make_quality_point(self, values, search_domain, counts):
        Point = self.env["quality.point"].with_company(self.env.company)
        point = Point.search(search_domain, limit=1)
        if point:
            self._mark_result(counts, "Puntos de control de calidad", False)
            return point
        point = Point.create(values)
        self._mark_result(counts, "Puntos de control de calidad", True)
        return point

    def _configure_pos_products(self, finished_templates):
        pos_installed = self.env["ir.module.module"].sudo().search_count(
            [("name", "=", "point_of_sale"), ("state", "=", "installed")]
        )
        ProductTemplate = self.env["product.template"].sudo()
        if not pos_installed or "available_in_pos" not in ProductTemplate._fields:
            return
        category = self.env["pos.category"].sudo().search([("name", "=", "UrbanStyle RD")], limit=1)
        if not category:
            category = self.env["pos.category"].sudo().create({"name": "UrbanStyle RD"})
        for template in finished_templates:
            values = {}
            if not template.available_in_pos:
                values["available_in_pos"] = True
            if category not in template.pos_categ_ids:
                values["pos_categ_ids"] = [Command.link(category.id)]
            if values:
                template.write(values)

    def action_load_demo_data(self):
        self.ensure_one()
        result_counts = {"created": defaultdict(int), "existing": defaultdict(int)}
        company = self.env.company

        # In Odoo 19 the dependency switch is the settings field
        # group_mrp_workorder_dependencies; allow_operation_dependencies is a BoM field.
        self.env["res.config.settings"].sudo().create(
            {
                "group_mrp_routings": True,
                "group_mrp_workorder_dependencies": True,
            }
        ).execute()

        warehouse = self.env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1)
        if not warehouse:
            raise UserError(_("Crea primero un almacén para la compañía activa y vuelve a cargar la demostración."))
        meter = self.env.ref("uom.product_uom_meter", raise_if_not_found=False)
        unit = self.env.ref("uom.product_uom_unit", raise_if_not_found=False)
        if not meter or not unit:
            raise UserError(_("Las unidades de medida estándar Metro y Unidad deben estar disponibles."))

        supplier_specs = [
            "Textiles del Caribe",
            "Distribuidora Textil RD",
            "Accesorios y Confecciones",
        ]
        suppliers = {}
        for supplier_name in supplier_specs:
            suppliers[supplier_name], _created = self._find_or_create_supplier(supplier_name, result_counts)

        raw_category = self._get_or_create_named("product.category", "Materias primas textiles")
        finished_category = self._get_or_create_named("product.category", "Prendas terminadas")
        sizes = ["XS", "S", "M", "L", "XL"]
        colors = ["Negro", "Blanco", "Beige", "Azul"]
        size_attribute, size_values = self._ensure_attribute("Talla", sizes)
        color_attribute, color_values = self._ensure_attribute("Color", colors)

        raw_specs = [
            {
                "name": "Tela de poliéster",
                "code": "US-RM-POLY",
                "uom": meter,
                "price": 145.0,
                "cost": 145.0,
                "initial": 240.0,
                "minimum": 60.0,
                "supplier": "Textiles del Caribe",
            },
            {
                "name": "Tela de algodón",
                "code": "US-RM-COT",
                "uom": meter,
                "price": 185.0,
                "cost": 185.0,
                "initial": 180.0,
                "minimum": 45.0,
                "supplier": "Distribuidora Textil RD",
            },
            {
                "name": "Hilo de costura",
                "code": "US-RM-THREAD",
                "uom": meter,
                "price": 1.2,
                "cost": 1.2,
                "initial": 9000.0,
                "minimum": 2000.0,
                "supplier": "Distribuidora Textil RD",
            },
            {
                "name": "Cierres",
                "code": "US-RM-ZIP",
                "uom": unit,
                "price": 38.0,
                "cost": 38.0,
                "initial": 400.0,
                "minimum": 80.0,
                "supplier": "Accesorios y Confecciones",
            },
            {
                "name": "Botones",
                "code": "US-RM-BUTTON",
                "uom": unit,
                "price": 4.5,
                "cost": 4.5,
                "initial": 1600.0,
                "minimum": 300.0,
                "supplier": "Accesorios y Confecciones",
            },
            {
                "name": "Entretela",
                "code": "US-RM-INTER",
                "uom": meter,
                "price": 72.0,
                "cost": 72.0,
                "initial": 140.0,
                "minimum": 35.0,
                "supplier": "Textiles del Caribe",
            },
            {
                "name": "Etiquetas de marca",
                "code": "US-RM-LABEL",
                "uom": unit,
                "price": 8.0,
                "cost": 8.0,
                "initial": 700.0,
                "minimum": 150.0,
                "supplier": "Accesorios y Confecciones",
            },
        ]
        raw_materials = {}
        for spec in raw_specs:
            supplier = suppliers[spec["supplier"]]
            template, created = self._get_or_create_demo(
                "product.template",
                spec["name"],
                {
                    "name": spec["name"],
                    "default_code": spec["code"],
                    "type": "consu",
                    "is_storable": True,
                    "sale_ok": False,
                    "purchase_ok": True,
                    "uom_id": spec["uom"].id,
                    "categ_id": raw_category.id,
                    "standard_price": spec["cost"],
                    "urbanstyle_is_raw_material": True,
                    "urbanstyle_is_finished_product": False,
                    "urbanstyle_min_stock": spec["minimum"],
                    "seller_ids": [
                        Command.create(
                            {
                                "partner_id": supplier.id,
                                "price": spec["price"],
                                "min_qty": 1.0,
                                "company_id": company.id,
                            }
                        )
                    ],
                },
                result_counts,
                label="Materias primas",
                default_code=spec["code"],
            )
            raw_materials[spec["name"]] = template
            if created:
                self._ensure_initial_stock(template, spec["initial"], warehouse.lot_stock_id, result_counts)

        finished_specs = [
            {
                "name": "Falda plisada clásica",
                "prefix": "FAL",
                "price": 1890.0,
                "cost": 520.0,
            },
            {"name": "Camiseta básica", "prefix": "CAM", "price": 890.0, "cost": 240.0},
            {"name": "Pantalón recto", "prefix": "PAN", "price": 2190.0, "cost": 650.0},
        ]
        finished_templates = {}
        for spec in finished_specs:
            template, created = self._get_or_create_demo(
                "product.template",
                spec["name"],
                {
                    "name": spec["name"],
                    "type": "consu",
                    "is_storable": True,
                    "sale_ok": True,
                    "purchase_ok": False,
                    "uom_id": unit.id,
                    "categ_id": finished_category.id,
                    "list_price": spec["price"],
                    "standard_price": spec["cost"],
                    "urbanstyle_is_raw_material": False,
                    "urbanstyle_is_finished_product": True,
                },
                result_counts,
                label="Productos terminados",
            )
            finished_templates[spec["name"]] = template
            if created:
                template.write(
                    {
                        "attribute_line_ids": [
                            Command.create(
                                {
                                    "attribute_id": size_attribute.id,
                                    "value_ids": [Command.set([value.id for value in size_values.values()])],
                                }
                            ),
                            Command.create(
                                {
                                    "attribute_id": color_attribute.id,
                                    "value_ids": [Command.set([value.id for value in color_values.values()])],
                                }
                            ),
                        ]
                    }
                )
                self._set_variant_references(template, spec["prefix"])
            else:
                # The created templates already carry the native variant lines.
                # No edits are made to pre-existing demo records.
                pass

        self._configure_pos_products(list(finished_templates.values()))

        workcenter_specs = [
            ("Área de corte", 12.0, 2.0, 95.0, 250.0, 6.0),
            ("Área de plisado", 18.0, 3.0, 90.0, 350.0, 4.0),
            ("Área de costura", 14.0, 2.0, 96.0, 300.0, 8.0),
            ("Área de bordado", 20.0, 3.0, 92.0, 425.0, 3.0),
            ("Área de acabados", 10.0, 2.0, 95.0, 275.0, 8.0),
            ("Área de inspección", 8.0, 1.0, 98.0, 225.0, 10.0),
        ]
        workcenters = {}
        for name, setup, cleanup, efficiency, hourly_cost, capacity in workcenter_specs:
            workcenter, _created = self._get_or_create_demo(
                "mrp.workcenter",
                name,
                {
                    "name": name,
                    "company_id": company.id,
                    "time_start": setup,
                    "time_stop": cleanup,
                    "time_efficiency": efficiency,
                    "costs_hour": hourly_cost,
                    "capacity_ids": [
                        Command.create(
                            {
                                "product_uom_id": unit.id,
                                "capacity": capacity,
                                "time_start": setup,
                                "time_stop": cleanup,
                            }
                        )
                    ],
                },
                result_counts,
                label="Centros de trabajo",
            )
            workcenters[name] = workcenter

        skirt = finished_templates["Falda plisada clásica"]
        bom = self.env["mrp.bom"].search(
            [
                ("is_urbanstyle_demo", "=", True),
                ("product_tmpl_id", "=", skirt.id),
            ],
            limit=1,
        )
        if not bom:
            bom_values = {
                "product_tmpl_id": skirt.id,
                "product_qty": 1.0,
                "product_uom_id": unit.id,
                "type": "normal",
                "company_id": company.id,
                "picking_type_id": warehouse.manu_type_id.id,
                "allow_operation_dependencies": True,
                "is_urbanstyle_demo": True,
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": raw_materials["Tela de poliéster"].product_variant_id.id,
                            "product_qty": 1.60,
                            "product_uom_id": meter.id,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": raw_materials["Hilo de costura"].product_variant_id.id,
                            "product_qty": 60.0,
                            "product_uom_id": meter.id,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": raw_materials["Cierres"].product_variant_id.id,
                            "product_qty": 1.0,
                            "product_uom_id": unit.id,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": raw_materials["Entretela"].product_variant_id.id,
                            "product_qty": 0.20,
                            "product_uom_id": meter.id,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": raw_materials["Etiquetas de marca"].product_variant_id.id,
                            "product_qty": 1.0,
                            "product_uom_id": unit.id,
                        }
                    ),
                ],
            }
            bom = self.env["mrp.bom"].with_company(company).create(bom_values)
            self._mark_result(result_counts, "Listas de materiales", True)
        else:
            self._mark_result(result_counts, "Listas de materiales", False)

        operation_specs = [
            {
                "name": "Inspección inicial de tela",
                "workcenter": "Área de inspección",
                "minutes": 6.0,
                "notes": "Verificar metraje, tono, defectos, composición y humedad antes del extendido.",
            },
            {
                "name": "Extendido y corte",
                "workcenter": "Área de corte",
                "minutes": 18.0,
                "notes": "Alinear la tela al hilo; marcar el patrón y cortar las piezas evitando defectos visibles.",
            },
            {
                "name": "Elaboración de pliegues",
                "workcenter": "Área de plisado",
                "minutes": 28.0,
                "is_pleating_operation": True,
                "pleat_type": "box",
                "pleat_width_cm": 2.5,
                "pleat_distance_cm": 1.5,
                "pleat_count": 24,
                "fabric_type": "Poliéster tejido para falda plisada",
                "fixation_method": "steam",
                "notes": (
                    "Marcar 24 pliegues de tabla, cada uno de 2.5 cm y separados 1.5 cm. "
                    "Mantener tensión uniforme, alinear las marcas y fijar con vapor industrial. "
                    "Dejar enfriar la pieza extendida antes de liberarla a costura."
                ),
            },
            {
                "name": "Costura y confección",
                "workcenter": "Área de costura",
                "minutes": 42.0,
                "notes": "Cerrar costados, colocar cierre y mantener puntadas uniformes sin deformar los pliegues.",
            },
            {
                "name": "Bordado o personalización",
                "workcenter": "Área de bordado",
                "minutes": 16.0,
                "notes": "Aplicar la personalización aprobada y comprobar ubicación, color y fijación del hilo.",
            },
            {
                "name": "Planchado y acabados",
                "workcenter": "Área de acabados",
                "minutes": 14.0,
                "notes": "Planchar a temperatura adecuada, retirar hilos sueltos y colocar la etiqueta de marca.",
            },
            {
                "name": "Inspección final y empaque",
                "workcenter": "Área de inspección",
                "minutes": 10.0,
                "notes": "Revisar medidas, costuras, cierre, pliegues, limpieza y presentación; empacar si aprueba.",
            },
        ]
        operations = []
        created_operations = []
        for sequence, spec in enumerate(operation_specs, start=1):
            operation = bom.operation_ids.filtered(lambda item: item.name == spec["name"])[:1]
            if operation:
                self._mark_result(result_counts, "Operaciones de fabricación", False)
                operations.append(operation)
                created_operations.append(False)
                continue
            operation_values = {
                "name": spec["name"],
                "sequence": sequence * 10,
                "workcenter_id": workcenters[spec["workcenter"]].id,
                "time_mode": "manual",
                "time_cycle_manual": spec["minutes"],
                "technical_notes": spec["notes"],
            }
            for field_name in (
                "is_pleating_operation",
                "pleat_type",
                "pleat_width_cm",
                "pleat_distance_cm",
                "pleat_count",
                "fabric_type",
                "fixation_method",
            ):
                if field_name in spec:
                    operation_values[field_name] = spec[field_name]
            operation = self.env["mrp.routing.workcenter"].with_company(company).create(
                dict(operation_values, bom_id=bom.id)
            )
            self._mark_result(result_counts, "Operaciones de fabricación", True)
            operations.append(operation)
            created_operations.append(True)

        for index, operation in enumerate(operations):
            if index and created_operations[index]:
                operation.blocked_by_operation_ids = [Command.link(operations[index - 1].id)]

        mrp_operation_type = self.env["stock.picking.type"].search(
            [("code", "=", "mrp_operation"), ("warehouse_id", "=", warehouse.id)], limit=1
        )
        if not mrp_operation_type:
            mrp_operation_type = warehouse.manu_type_id
        pass_fail_type = self.env.ref("quality_control.test_type_passfail")
        operation_qc_specs = {
            "Extendido y corte": "Control después del corte",
            "Elaboración de pliegues": "Control después del plisado",
            "Costura y confección": "Control después de la confección",
            "Inspección final y empaque": "Control final antes del almacenamiento",
        }
        for operation in operations:
            title = operation_qc_specs.get(operation.name)
            if not title:
                continue
            self._make_quality_point(
                {
                    "title": title,
                    "note": "Registrar aprobación o rechazo y describir cualquier defecto observado.",
                    "test_type_id": pass_fail_type.id,
                    "measure_on": "operation",
                    "operation_id": operation.id,
                    "picking_type_ids": [Command.link(mrp_operation_type.id)],
                    "company_id": company.id,
                },
                [("operation_id", "=", operation.id), ("title", "=", title)],
                result_counts,
            )

        receipt_title = "Inspección de materias primas al recibir - UrbanStyle RD"
        incoming_point = self.env["quality.point"].search(
            [("title", "=", receipt_title), ("picking_type_ids", "in", [warehouse.in_type_id.id])],
            limit=1,
        )
        if incoming_point:
            self._mark_result(result_counts, "Puntos de control de calidad", False)
        else:
            incoming_point = self.env["quality.point"].with_company(company).create(
                {
                    "title": receipt_title,
                    "note": "Comprobar metraje, color, composición, defectos y estado del rollo antes de liberar a stock.",
                    "test_type_id": pass_fail_type.id,
                    "measure_on": "operation",
                    "product_ids": [
                        Command.set([template.product_variant_id.id for template in raw_materials.values()])
                    ],
                    "picking_type_ids": [Command.link(warehouse.in_type_id.id)],
                    "company_id": company.id,
                }
            )
            self._mark_result(result_counts, "Puntos de control de calidad", True)

        skirt_variant = skirt.product_variant_ids.filtered(
            lambda variant: (
                "M" in variant.product_template_attribute_value_ids.mapped("product_attribute_value_id.name")
                and "Negro" in variant.product_template_attribute_value_ids.mapped("product_attribute_value_id.name")
            )
        )[:1]
        existing_mo = self.env["mrp.production"].search(
            [
                ("is_urbanstyle_demo", "=", True),
                ("product_id", "=", skirt_variant.id),
            ],
            limit=1,
        )
        if existing_mo:
            self._mark_result(result_counts, "Orden de fabricación demostrativa", False)
        else:
            self.env["mrp.production"].with_company(company).create(
                {
                    "product_id": skirt_variant.id,
                    "product_qty": 1.0,
                    "product_uom_id": unit.id,
                    "bom_id": bom.id,
                    "picking_type_id": warehouse.manu_type_id.id,
                    "company_id": company.id,
                    "is_urbanstyle_demo": True,
                }
            )
            self._mark_result(result_counts, "Orden de fabricación demostrativa", True)

        created_summary = self._format_counts(result_counts["created"])
        existing_summary = self._format_counts(result_counts["existing"])
        message = _("Creados: %(created)s. Ya existentes: %(existing)s.") % {
            "created": created_summary or _("ninguno"),
            "existing": existing_summary or _("ninguno"),
        }
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Demostración UrbanStyle RD lista"),
                "message": message,
                "type": "success",
                "sticky": True,
                "next": {"type": "ir.actions.act_window_close"},
            },
        }

    @api.model
    def _format_counts(self, counts):
        return ", ".join("%s: %s" % (label, amount) for label, amount in counts.items())
