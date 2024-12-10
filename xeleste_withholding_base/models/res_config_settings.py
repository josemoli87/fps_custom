from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    apply_withholdings = fields.Selection([
        ('no', 'No Apply'),
        ('manual', 'Manual'),
        ('auto', 'Automatic'),
    ], string='Apply Withholdings', default='no', help='How withholdings are created from the invoice',
        required=True)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    apply_withholdings = fields.Selection(related='company_id.apply_withholdings', readonly=False)
