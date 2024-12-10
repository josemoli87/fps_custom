from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    ve_table_islr_id = fields.Many2one('table.islr', string='Concept ISLR', compute='_compute_ve_table_islr_id',
                                   inverse='_set_ve_table_islr_id')

    @api.depends('product_variant_ids.ve_table_islr_id')
    def _compute_ve_table_islr_id(self):
        self.ve_table_islr_id = False
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.ve_table_islr_id = template.product_variant_ids.ve_table_islr_id

    def _set_ve_table_islr_id(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.ve_table_islr_id = self.ve_table_islr_id


class ProductProduct(models.Model):
    _inherit = "product.product"

    ve_table_islr_id = fields.Many2one('table.islr', string='Concept ISLR')
