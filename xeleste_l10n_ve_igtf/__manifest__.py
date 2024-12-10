# -*- coding: utf-8 -*-
# Powered by Xeleste 23 C.A. (<https://xeleste.net>).

{
    'name': 'IGTF - Venezuela',
    'version': '17.0.3.0',
    'license': 'OPL-1',
    'countries': ['ve'],
    'icon': '/xeleste_l10n_ve_igtf/static/description/icon.png',
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
    'depends': ['account', 'xeleste_l10n_ve', 'xeleste_withholding_base'],
    'data': [
        # 'security/ir.model.access.csv',
        'data/product_data.xml',
        'wizard/account_payment_register_views.xml',
        'views/res_config_settings_views.xml',
    ],
}
