from odoo import models

class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'

    def _get_combination_name(self):
        """
        Include single-value attribute lines in variant name.
        Still exclude no_variant attributes.
        """
        ptavs = self._without_no_variant_attributes().with_prefetch(self._prefetch_ids)
        return ", ".join(ptav.name for ptav in ptavs)
