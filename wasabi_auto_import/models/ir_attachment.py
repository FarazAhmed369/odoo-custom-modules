from odoo import models, fields

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    wasabi_key = fields.Char(index=True)