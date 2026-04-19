# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Course(models.Model):
    _name = 'faraz_std.course'
    _description = 'Course List'

    name = fields.Char("Name")