# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    _sql_constraints = [('product_template_code_uniqu', 'unique(default_code)',
                         'El Código de producto ya existe, por favor intenta uno nuevo!')]

    @api.onchange('name')
    def _compute_maj_temp(self):
        self.name = self.name.upper() if self.name else False


class ProductProduct(models.Model):
    _inherit = 'product.product'

    _sql_constraints = [('product_template_code_uniqu', 'unique(default_code)',
                         'El Código de producto ya existe, por favor intenta uno nuevo!')]

    @api.onchange('name')
    def _compute_maj_pro(self):
        self.name = self.name.upper() if self.name else False
