# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
{
    'name': "Vehicle Trade Management | Car Trade",
    'version': "1.2",
    'description': "Part of Vehicle Trade Tech, Vehicle Trade is an automotive portal for Vehicles.",
    'summary': "Vehicle Trade",
    'author': 'TechKhedut Inc.',
    'website': "https://techkhedut.com",
    'depends': ['mail', 'contacts', 'product', 'account', 'sale_management'],
    'data': [
        # data
        'data/sequence_views.xml',
        'data/vehicle_category_views.xml',
        'data/document_type_data.xml',
        'data/fuel_type_data.xml',
        'data/insurance_type_data.xml',
        'data/vehicle_brands_models_data.xml',
        'data/vehicle_specification_data.xml',
        'data/vehicle_trade_completed_mail.xml',
        # Security
        'security/ir.model.access.csv',
        # Views
        'views/assets.xml',
        'views/vehicle_information_views.xml',
        'views/expert_inspection_views.xml',
        'views/vehicle_brand_model_views.xml',
        'views/vehicle_condition_views.xml',
        'views/vehicle_image_views.xml',
        'views/vehicle_specification_views.xml',
        'views/vehicle_insurance_views.xml',
        'views/vehicle_fuel_type_views.xml',
        'views/document_type_views.xml',
        'views/previous_service_history_views.xml',
        'views/model_views.xml',
        # Reports
        'report/vehicle_report_views.xml',
        # Menus
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'vehicle_trade/static/src/xml/template.xml',
            'vehicle_trade/static/src/scss/style.scss',
            'vehicle_trade/static/src/js/lib/apexcharts.js',
            'vehicle_trade/static/src/js/dashboard/vehicle_trade_dashboard.js',
        ],
    },
    'images': ['static/description/cover.gif'],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 49,
    'currency': 'EUR',
}
