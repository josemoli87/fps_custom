from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    auto_withholding = fields.Boolean(string='Automatically generate withholdings')
