from odoo import fields, models, api


class AccountTax(models.Model):
    _inherit = 'account.tax'

    l10n_ve_aliquot_type = fields.Selection(string='Aliquot Type', required=False,
                                 selection=[('exempt', 'Exempt'),
                                            ('reduced', 'Reduced'),
                                            ('general', 'General'),
                                            ('additional', 'General + Additional')])

    @api.model_create_multi
    def create(self, vals_list):
        results = super().create(vals_list)
        for res in results:
            if res.country_code == 'VE' and not res.l10n_ve_aliquot_type:
                amount = res.amount
                res.l10n_ve_aliquot_type = (amount == 8 and 'reduced') or (amount == 16 and 'general') or \
                                           (amount == 31 and 'additional') or 'exempt'
        return results
