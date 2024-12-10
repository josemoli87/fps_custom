# -*- coding: utf-8 -*-
# Powered by Xeleste 23 C.A. (<https://xeleste.net>).

{
    'name': 'VENEZUELA - Accounting Minimal Xeleste',
    'version': '17.0.1.0',
    'license': 'OPL-1',
    'countries': ['ve'],
    'icon': '/xeleste_l10n_ve/static/description/icon.png',
    'author': 'Xeleste 23 C.A.',
    "contribuitors": ["Clara Savelli <clara.15is.cs@gmail.com>"],
    'website': 'https://xeleste.net',
    'category': 'Accounting/Localizations/Account Charts',
    "summary": '''
        Base contable para Venezuela, minimal.
    ''',
    'description':
"""
Base contable para Venezuela, minimal.
===============================

""",
    'depends': ['account', 'l10n_ve_dpt'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/menuitems.xml',
        'views/tax_unit_views.xml',
        'views/account_tax_views.xml',
        'views/res_partner_views.xml',
        'views/account_move_views.xml',
        'views/res_config_settings_views.xml',
        'views/invoice_statements_views.xml',
    ]
}
