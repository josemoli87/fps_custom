from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    apply_igtf = fields.Boolean(string='Apply IGTF')
    igtf_percentage = fields.Float(string='Percentage IGTF')
    igtf_product_id = fields.Many2one('product.product', string='IGTF Product')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    apply_igtf = fields.Boolean(related='company_id.apply_igtf', readonly=False)
    igtf_percentage = fields.Float(related='company_id.igtf_percentage', readonly=False)
    igtf_product_id = fields.Many2one(related='company_id.igtf_product_id', readonly=False)
