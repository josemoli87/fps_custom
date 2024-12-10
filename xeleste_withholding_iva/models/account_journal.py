from odoo import fields, models, api


class AccountJournal(models.Model):
    _inherit = "account.journal"

    withholding_type = fields.Selection(selection_add=[('iva', 'IVA')])
