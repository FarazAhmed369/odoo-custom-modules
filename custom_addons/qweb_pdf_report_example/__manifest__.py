# -*- coding: utf-8 -*-
{
    'name': "Qweb Report Demo",

    'summary': "Qweb Report Demo",

    'description': "Qweb Report Demo",

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'school',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','faraz_std'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/student_report_template.xml',
        'report/inherit_pdf_report.xml',
        'report/Sudent_card_template.xml',
    ],
}

