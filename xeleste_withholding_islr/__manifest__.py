# -*- coding: utf-8 -*-
# Powered by Xeleste 23 C.A. (<https://xeleste.net>).

{
    'name': 'Witholding ISLR - Venezuela',
    'version': '17.0.1.0',
    'license': 'OPL-1',
    'countries': ['ve'],
    'icon': '/xeleste_withholding_islr/static/description/icon.png',
    'author': 'Xeleste 23 C.A.',
    "contribuitors": ["Clara Savelli <clara.15is.cs@gmail.com>"],
    'website': 'https://xeleste.net',
    'category': 'Accounting/Accounting',
    "summary": '''
        Witholdings ISLR for Venezuela.
    ''',
    'description':
"""
Witholdings ISLR for Venezuela.
===============================

""",
    'depends': ['account', 'xeleste_withholding_base'],
    'data': [
        'security/security.xml',
        'data/ir_sequence_data.xml',
        'data/table_islr_data.xml',
        'security/ir.model.access.csv',
        'views/table_islr_views.xml',
        'views/product_views.xml',
        'views/account_withholding_views.xml',
        'views/report_islr.xml',
        'views/xml_islr_views.xml',
        'wizard/wizard_generate_withholding_views.xml',
    ],
}
