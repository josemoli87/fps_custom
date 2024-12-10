# -*- coding: utf-8 -*-
# Powered by Xeleste 23 C.A. (<https://xeleste.net>).

{
    'name': 'Witholding Base',
    'version': '17.0.1.0',
    'license': 'OPL-1',
    'countries': ['ve'],
    'icon': '/xeleste_withholding_base/static/description/icon.png',
    'author': 'Xeleste 23 C.A.',
    "contribuitors": ["Clara Savelli <clara.15is.cs@gmail.com>"],
    'website': 'https://xeleste.net',
    'category': 'Accounting/Accounting',
    "summary": '''
        Chart of Account for Venezuela.
    ''',
    'description':
"""
Chart of Account for Venezuela.
===============================

""",
    'depends': ['account', 'account_accountant', 'xeleste_l10n_ve', 'account_debit_note'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_withholding_views.xml',
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
        'views/account_journal_views.xml',
        'views/res_config_settings_views.xml',
        'views/report_withholding.xml',
        'views/invoice_report.xml',
        'wizard/wizard_generate_withholding_views.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'xeleste_withholding_base/static/src/components/**/*',
        ],
    }
}
