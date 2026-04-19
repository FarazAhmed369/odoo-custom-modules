from odoo import models, fields, api

class Student(models.Model):
    _name = 'uni_marksheet.student'
    _description = 'Student Record'

    name = fields.Char(string='Student Name', required=True)
    roll_no = fields.Char(string='Roll Number', required=True)
    father_name = fields.Char(string='F.Name')
    dob = fields.Date(string='DOB')
    address = fields.Text(string='Address')
    age = fields.Integer(string='Age')
    std_image = fields.Image(string='Profile Image')

    university_id = fields.Many2one('uni_marksheet.university', string='University')
    # course_ids = fields.Many2many('uni_marksheet.course', string='Selected Courses')

    # Performance Fields
    marks_obtained = fields.Float(string='Total Marks')
    total_marks = fields.Float(string='Max Marks')
    percentage = fields.Float(string='Percentage', compute='_compute_percentage', store=True)
    grade = fields.Char(string='Grade', compute='_compute_grade', store=True)
    gpa = fields.Float(string='GPA', compute='_compute_gpa', store=True)

    subject_line_ids = fields.One2many('uni_marksheet.subject.line', 'student_id',)

    # marks_obtained = fields.Float(string='Total Marks', compute='_compute_totals', store=True)
    # total_marks = fields.Float(string='Max Marks', compute='_compute_totals', store=True)

    @api.depends('marks_obtained', 'total_marks')
    def _compute_percentage(self):
        for rec in self:
            rec.percentage = (rec.marks_obtained / rec.total_marks * 100) if rec.total_marks else 0.0

    @api.depends('percentage')
    def _compute_grade(self):
        for rec in self:
            p = rec.percentage
            if p >= 90:
                rec.grade = 'A+'
            elif p >= 80:
                rec.grade = 'A'
            elif p >= 70:
                rec.grade = 'B'
            elif p >= 60:
                rec.grade = 'C'
            elif p >= 50:
                rec.grade = 'D'
            else:
                rec.grade = 'F'

    @api.depends('percentage')
    def _compute_gpa(self):
        for rec in self:
            p = rec.percentage

            if p >= 90:
                rec.gpa = 4.00
            elif p >= 80:
                rec.gpa = 3.50
            elif p >= 70:
                rec.gpa = 3.00
            elif p >= 60:
                rec.gpa = 2.50
            elif p >= 50:
                rec.gpa = 2.00
            else:
                rec.gpa = 0.00

    # Grand Totals (for report summary only)
    grand_total_marks = fields.Float(string='Grand Total', compute='_compute_grand_summary', store=True)
    grand_obtained_marks = fields.Float(string='Grand Obtained', compute='_compute_grand_summary', store=True)
    grand_percentage = fields.Float(string='Grand Percentage', compute='_compute_grand_summary', store=True)
    grand_grade = fields.Char(string='Grand Grade', compute='_compute_grand_summary', store=True)
    grand_gpa = fields.Float(string='Grand GPA', compute='_compute_grand_summary', store=True)

    @api.depends('subject_line_ids.total_max', 'subject_line_ids.total_obtain')
    def _compute_grand_summary(self):
        for rec in self:
            total = sum(line.total_max for line in rec.subject_line_ids)
            obtained = sum(line.total_obtain for line in rec.subject_line_ids)
            percentage = (obtained / total * 100) if total else 0.0

            rec.grand_total_marks = total
            rec.grand_obtained_marks = obtained
            rec.grand_percentage = percentage

            # Grade
            if percentage >= 90:
                rec.grand_grade = 'A+'
                rec.grand_gpa = 4.00
            elif percentage >= 80:
                rec.grand_grade = 'A'
                rec.grand_gpa = 3.50
            elif percentage >= 70:
                rec.grand_grade = 'B'
                rec.grand_gpa = 3.00
            elif percentage >= 60:
                rec.grand_grade = 'C'
                rec.grand_gpa = 2.50
            elif percentage >= 50:
                rec.grand_grade = 'D'
                rec.grand_gpa = 2.00
            else:
                rec.grand_grade = 'F'
                rec.grand_gpa = 0.00

    # Grand Totals (for report summary only)
    grand_total_marks = fields.Float(string='Grand Total', compute='_compute_grand_summary', store=True)
    grand_obtained_marks = fields.Float(string='Grand Obtained', compute='_compute_grand_summary', store=True)
    grand_percentage = fields.Float(string='Grand Percentage', compute='_compute_grand_summary', store=True)
    grand_grade = fields.Char(string='Grand Grade', compute='_compute_grand_summary', store=True)
    grand_gpa = fields.Float(string='Grand GPA', compute='_compute_grand_summary', store=True)

    @api.depends('subject_line_ids.total_max', 'subject_line_ids.total_obtain')
    def _compute_grand_summary(self):
        for rec in self:
            total = sum(line.total_max for line in rec.subject_line_ids)
            obtained = sum(line.total_obtain for line in rec.subject_line_ids)
            percentage = (obtained / total * 100) if total else 0.0

            rec.grand_total_marks = total
            rec.grand_obtained_marks = obtained
            rec.grand_percentage = percentage

            # Grade
            if percentage >= 90:
                rec.grand_grade = 'A+'
                rec.grand_gpa = 4.00
            elif percentage >= 80:
                rec.grand_grade = 'A'
                rec.grand_gpa = 3.50
            elif percentage >= 70:
                rec.grand_grade = 'B'
                rec.grand_gpa = 3.00
            elif percentage >= 60:
                rec.grand_grade = 'C'
                rec.grand_gpa = 2.50
            elif percentage >= 50:
                rec.grand_grade = 'D'
                rec.grand_gpa = 2.00
            else:
                rec.grand_grade = 'F'
                rec.grand_gpa = 0.00
