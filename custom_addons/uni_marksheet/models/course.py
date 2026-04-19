from odoo import models, fields

class Course(models.Model):
    _name = 'uni_marksheet.course'
    _description = 'Academic Course'

    name = fields.Char(string='Course Name', required=True)
    code = fields.Char(string='Course Code')
    credit_hours = fields.Integer(string='Credit Hours')
    max_marks = fields.Integer(string='Max Marks', default=100)
