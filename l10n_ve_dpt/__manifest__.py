##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Localización Venezolana: Municipios y Parroquias",
    "version": "17.0",
    "author": "BACHACO-VE",
    "category": "Localization",
    'contributors': ['Clara Savelli <clara.15is.cs@gmail.com>'],
    "website": "http://www.bachaco.org.ve",
    'images': ['static/description/icon.png'],
    "depends": ['base', 'contacts',],
    "init_xml": [],
    "demo_xml": [],
    "data": [
        'security/ir.model.access.csv',
        'data/res.country.state.xml',
        'data/res.country.state.municipality.xml',
        'data/res.country.state.municipality.parish.xml',
        'views/l10n_ve_dpt_view.xml',
        'views/res_partner.xml',
        'data/res_country.xml',
    ],
    "installable": True,
    'license': 'LGPL-3',
}
