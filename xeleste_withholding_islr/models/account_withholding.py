from odoo import fields, models, api


class AccountWithholding(models.Model):
    _inherit = 'account.withholding'

    withholding_method = fields.Selection(selection_add=[('islr', 'ISLR')], ondelete={'islr': 'set default'})

    def get_sequence(self):
        if self.withholding_method == 'islr' and self.withholding_type != 'inbound':
            return 'withholding.islr.%s' % self.env.company.id 
        return super().get_sequence()


class AccountWithholdingLine(models.Model):
    _inherit = 'account.withholding.line'

    code_islr = fields.Char(string='Code')
    concept_islr = fields.Char(string='Concept ISLR')
    subt = fields.Float(string='Subtracting', default=0.0)

    @api.depends('amount_origin', 'percentage', 'amount_base', 'move_line_id', 'move_id', 'currency_id')
    def _compute_amounts(self):
        lines = self.env['account.withholding.line']
        for line in self:
            if line.withholding_id.withholding_method == 'islr':
                withholding = ((line.percentage / 100) * line.amount_base) - line.subt
                line.amount_withholding = -withholding if line.move_id.move_type in ['out_refund', 'in_refund'] else withholding
                lines |= line

        OthersLines = self - lines
        super(AccountWithholdingLine, OthersLines)._compute_amounts()
