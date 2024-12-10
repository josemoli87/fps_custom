from odoo import fields, models, api


class AccountJournal(models.Model):
    _inherit = "account.journal"

    use_withholding = fields.Boolean(string="Use for Withholding")
    withholding_type = fields.Selection([('standard', 'Standard')], string="Type of Withholding")
