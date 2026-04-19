from odoo import fields, models

class TestStudent(models.Model):
    _name = 'faraz.test_student'
    _description = 'Testing Student Model'

    name = fields.Char("Name")
    age = fields.Integer("Age")
    email = fields.Char("Email")
    remarks = fields.Text("Remarks")
