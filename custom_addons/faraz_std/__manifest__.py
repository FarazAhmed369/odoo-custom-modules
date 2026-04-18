# -*- coding: utf-8 -*-
{
    'name': "faraz_std",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'version': '18.0',

    'depends': ['faraz_test_student', 'account'],

    # always loaded
    'data': [
        "security/ir.model.access.csv",
        "views/student_view.xml",
        "views/school_view.xml",
        "views/course_view.xml",

    ],

    'installable': True,
    'application': True,

    'license': 'LGPL-3',

}

