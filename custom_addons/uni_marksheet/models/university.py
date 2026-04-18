from odoo import models, fields

class University(models.Model):
    _name = 'uni_marksheet.university'
    _description = 'University Information'

    name = fields.Char(string='University Name', required=True)
    address = fields.Char(string='Address')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    website = fields.Char(string='Website')
    logo = fields.Image(string='University Logo')
