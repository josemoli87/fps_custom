from odoo import fields, models, api


class AccountWithholding(models.Model):
    _inherit = 'account.withholding'

    withholding_method = fields.Selection(selection_add=[('iva', 'IVA')], ondelete={'iva': 'set default'})

    def get_sequence(self):
        if self.withholding_method == 'iva':
            return 'withholding.iva.%s' % self.company_id.id
        return super().get_sequence()


class AccountWithholdingLine(models.Model):
    _inherit = 'account.withholding.line'

    aliquot = fields.Char(string='Aliquot')

    @api.depends('amount_origin', 'percentage', 'amount_base', 'move_line_id', 'move_id', 'currency_id')
    def _compute_amounts(self):
        for line in self:
            if line.withholding_id.withholding_method == 'iva':
                withholding = (line.percentage / 100) * line.amount_base
                line.amount_withholding = -withholding if line.move_id.move_type in ['out_refund', 'in_refund'] else withholding
            else:
                super()._compute_amounts()
