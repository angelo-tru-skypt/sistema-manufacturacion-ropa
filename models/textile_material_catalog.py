from odoo import fields, models


URBANSTYLE_MATERIAL_USAGE_SELECTION = [
    ("shirts", "Camisas y blusas"),
    ("tshirts", "Camisetas"),
    ("pants", "Pantalones"),
    ("dresses", "Vestidos y faldas"),
    ("sportswear", "Ropa deportiva"),
    ("outerwear", "Chaquetas y abrigos"),
    ("lining", "Forros"),
    ("uniforms", "Uniformes"),
    ("home_textile", "Textiles para el hogar"),
    ("accessories", "Accesorios"),
    ("other", "Otro uso"),
]


class ProductTemplate(models.Model):
    _inherit = "product.template"

    urbanstyle_composition = fields.Char(
        string="Composición",
        help="Ejemplo: 65% poliéster, 35% algodón.",
    )
    urbanstyle_texture = fields.Char(
        string="Textura o tejido",
        help="Ejemplo: jersey, sarga, satén o tejido plano.",
    )
    urbanstyle_material_color = fields.Char(string="Color del material")
    urbanstyle_weight_gsm = fields.Float(
        string="Peso (g/m²)",
        digits=(16, 2),
        help="Gramaje del tejido en gramos por metro cuadrado.",
    )
    urbanstyle_usage = fields.Selection(
        URBANSTYLE_MATERIAL_USAGE_SELECTION,
        string="Utilización recomendada",
    )
