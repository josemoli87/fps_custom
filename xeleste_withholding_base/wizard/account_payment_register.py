from odoo import api, fields, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    @api.model
    def _get_batch_available_journals(self, batch_result):
        journals = super()._get_batch_available_journals(batch_result)
        journals = journals.filtered(lambda x: x.use_withholding == False)
        return journals
