from odoo import models, fields, api

class SubjectLine(models.Model):
    _name = 'uni_marksheet.subject.line'
    _description = 'Subject Marks Line'

    student_id = fields.Many2one('uni_marksheet.student', string="Student")  # Link to Student
    subject_name = fields.Many2one('uni_marksheet.course', string='Subject Name')
    sessional_max = fields.Integer(string="Sessional Max.", default="40")
    sessional_obt = fields.Integer(string="Sessional Obt.")
    theory_max = fields.Integer(string="Theory Max.", default="60")
    theory_obt = fields.Integer(string="Theory Obt.")
    total_max = fields.Integer(string="Total Max.", default="100")
    total_obtain = fields.Integer(string="Total Obt.", compute="_compute_total_obtain", store=True)


    grand_total = fields.Integer(string="Grand Total", compute="_compute_grand_total", store=True)
    grade = fields.Char(string="Grade", compute="_compute_grade", store=True)
    gpa = fields.Integer(string="GPA", compute="_compute_gpa", store=True)

    @api.depends('sessional_obt', 'theory_obt')
    def _compute_total_obtain(self):
        for rec in self:
            rec.total_obtain = (rec.sessional_obt or 0) + (rec.theory_obt or 0)

    # @api.depends('sessional_obt', 'theory_obt', 'total_obtain')
    # def _compute_grand_total(self):
    #     for rec in self:
    #         rec.grand_total = (rec.sessional_obt or 0) + (rec.theory_obt or 0) + (rec.total_obtain or 0)

    @api.depends('total_obtain')
    def _compute_grade(self):
        for rec in self:
            gt = rec.total_obtain
            if gt >= 90:
                rec.grade = 'A+'
            elif gt >= 80:
                rec.grade = 'A'
            elif gt >= 70:
                rec.grade = 'B'
            elif gt >= 60:
                rec.grade = 'C'
            elif gt >= 50:
                rec.grade = 'D'
            else:
                rec.grade = 'F'

    @api.depends('total_obtain')
    def _compute_gpa(self):
        for rec in self:
            gt = rec.total_obtain
            if gt >= 90:
                rec.gpa = 4.00
            elif gt >= 80:
                rec.gpa = 3.50
            elif gt >= 70:
                rec.gpa = 3.00
            elif gt >= 60:
                rec.gpa = 2.50
            elif gt >= 50:
                rec.gpa = 2.00
            else:
                rec.gpa = 0.00
