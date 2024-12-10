from odoo import fields, models, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    apply_withholdings = fields.Selection(related='company_id.apply_withholdings')
    withholding_ids = fields.Many2many('account.withholding', string='Withholdings', copy=False,
                                       compute='_compute_withholdings')

    def _compute_withholdings(self):
        for move in self:
            lines = self.env['account.withholding.line'].search([('move_id', '=', move.id)])
            move.withholding_ids = lines.mapped('withholding_id')

    def _compute_payments_widget_reconciled_info(self):
        super()._compute_payments_widget_reconciled_info()
        for move in self:
            if move.invoice_payments_widget and move.state == 'posted' and move.is_invoice(include_receipts=True):
                reconciled_partials = move._get_all_reconciled_invoice_partials()
                for i, reconciled_partial in enumerate(reconciled_partials):
                    counterpart_line = reconciled_partial['aml']
                    if counterpart_line.move_id.sudo().journal_id.use_withholding:
                        move.invoice_payments_widget['content'][i].update({
                            'withholding_type': counterpart_line.move_id.sudo().journal_id.withholding_type,
                        })

    def button_draft(self):
        res = super().button_draft()
        withholding = self.withholding_ids.filtered(lambda x: x.state == 'posted')
        if withholding:
            withholding.action_draft()
        return res

    def _check_apply_withholdings(self):
        # TODO: only invoices
        return False

    def action_generate_withholdings(self):
        if self.company_id.apply_withholdings == 'no':
            return
        return {
            'name': _('Register Withholding'),
            'res_model': 'wizard.generate.withholding',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'context': {
                'default_invoice_id': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def _generate_withholdings(self):
        return self.env['account.withholding']

    def action_post(self):
        if self.company_id.apply_withholdings == 'auto' or (self.company_id.apply_withholdings != 'no'
                                                            and self.partner_id.auto_withholding):
            if self._check_apply_withholdings():
                withholding_ids = self._generate_withholdings()
                self.withholding_ids = [(6, 0, withholding_ids.ids)]

        return super().action_post()
