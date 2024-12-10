# -*- coding: utf-8 -*-
# Powered by Xeleste 23 C.A. (<https://xeleste.net>).

{
    'name': 'Witholding IVA - Venezuela',
    'version': '17.0.1.0',
    'license': 'OPL-1',
    'countries': ['ve'],
    'icon': '/xeleste_withholding_iva/static/description/icon.png',
    'author': 'Xeleste 23 C.A.',
    "contribuitors": ["Clara Savelli <clara.15is.cs@gmail.com>"],
    'website': 'https://xeleste.net',
    'category': 'Accounting/Accounting',
    "summary": '''
        Witholdings IVA for Venezuela.
    ''',
    'description':
"""
Witholdings IVA for Venezuela.
===============================

""",
    'depends': ['account', 'xeleste_withholding_base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'wizard/wizard_generate_withholding_views.xml',
        'views/account_withholding_views.xml',
        'views/report_iva.xml',
        'views/txt_iva_views.xml',
    ],
}
