# -*- coding: utf-8 -*-

from odoo import api, fields, models


class School(models.Model):
    _name = 'faraz_std.school'
    _description = 'School List'

    name = fields.Char("School Name")
    address = fields.Text("School Address")
    # joining_date = fields.Datetime("Joining Date")
    std_fees = fields.Float("STD Fees")
    student_list = fields.One2many("faraz_std.student", "school_id")
    ref_field_id = fields.Reference([('faraz_std.school','school'),
                                     ('faraz_std.student','student'),
                                     ('faraz_std.course','course')])
    invoice_id = fields.Many2one('account.move')
    invoice_user_id = fields.Many2one('res.users', related = 'invoice_id.invoice_user_id')
    invoice_date = fields.Date(related = 'invoice_id.invoice_date')