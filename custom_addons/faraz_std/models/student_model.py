# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Student(models.Model):
    _name = 'faraz_std.student'
    _description = 'Student List'

    # def name_get(self):
    #     result = []
    #     for record in self:
    #         result.append((record.id, record.name))
    #     return result

    #     # @api.model
#     # def get_vip_list(self):
#     #     return [
#     #         ('male', 'Male'),
#     #         ('female', 'Female'),
#     #         ('custom', 'Custom')
#     #     ]
#     #
#     # school = fields.Json()
#     #
#     gender = fields.Selection(
#         [('male','Male'), ('female','Female')]
#     )
#     #
#     # def json_data_store(self):
#     #     self.school = {"name":self.name, "id":self.id, "gender": self.gender}
#     #     print(self.school)
#
#     birth_date = fields.Date(string="Birth Date", default = fields.Date.today())
#     joining_datetime = fields.Datetime(default=fields.Datetime.now)
#     # advance_gender = fields.Selection('get_advance_gender_list')
#     # vip_gender = fields.Selection('get_vip_list')
#     is_paid = fields.Boolean(string = 'paid?')
#     name = fields.Char("Name")
#     roll_number = fields.Integer("Roll no:")
#     std_fees = fields.Float(digits="Percentage Analytic")
#     payment = fields.Float(digits=(4, 4))
#     name1 = fields.Char("Name1")
#     name2 = fields.Char("Name2")
#     name3 = fields.Char("Name3", default = 'Welcome')
#     name4 = fields.Char("Name4", readonly = True)
#
#     student_name = fields.Char(string = 'Student', required = True, size = 5)
#     address = fields.Text("Student Address", help = "Enter your home address.")
#
#     address_html = fields.Html("Address Html", default = 'Welcome')
#     #
#     # def get_advance_gender_list(self):
#     #     return [
#     #         ('male', 'Male'),
#     #         ('female', 'Female'),
#     #         ('custom', 'Custom')
#     #     ]
#
# # class School(models.Model):
# #     _name = 'faraz.faraz_std'
# #     _description = 'School List'
# #
# #     name = fields.Char("School Name")
# #     address = fields.Text("School Address")
# #     joining_date = fields.Datetime("Joining Date")
# #     std_fees = fields.Float("STD Fees")

    @api.onchange('std_fees','discount')
    def Compute_School_fees(self):
        for record in self:
            record.disc_fees = record.std_fees - record.discount

    name = fields.Char(string="Name ")
    color_name = fields.Char(string="Fvt. Color Name ")
    roll_no = fields.Integer("Roll no ")
    age = fields.Integer("Age ")
    # school = fields.Char("School name")
    school_id = fields.Many2one(comodel_name="faraz_std.school", string="Sch Name")
    course_list = fields.Many2many("faraz_std.course","student_course_list_relation","school_id","course_id")
    std_fees = fields.Float()
    discount = fields.Float()
    disc_fees = fields.Float(compute = 'Compute_School_fees', store = '1')

    address_html = fields.Html("Address Html", default='Welcome')
    compute_address_html = fields.Html()

    @api.onchange("address_html")
    def Onchange_address_html_field(self):
        for record in self:
            record.compute_address_html = record.address_html

    binary_field = fields.Binary()
    binary_file_name = fields.Char()
    binary_fields = fields.Many2many("ir.attachment",string='Files')
    amount = fields.Monetary(currency_field='my_currency_id')
    # currency_id = fields.Many2one("res.currency", 'Currency')
    my_currency_id = fields.Many2one('res.currency','My Currency',
                                     default=159)
    std_image = fields.Image(max_width=128, max_height=128)