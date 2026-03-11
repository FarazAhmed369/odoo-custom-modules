from odoo import models, api, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_template_variant_value_ids = fields.Many2many('product.template.attribute.value', relation='product_variant_combination',
                                                          domain=[('attribute_line_id.value_count', '>=', 1)], string="Variant Values", ondelete='restrict')