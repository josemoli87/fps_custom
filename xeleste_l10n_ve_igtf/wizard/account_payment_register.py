from odoo import api, fields, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    company_apply_igtf = fields.Boolean(related='company_id.apply_igtf', string='IGTF Company')
    apply_igtf = fields.Boolean(string='Apply IGTF')
    percentage_igtf = fields.Float(string='Percentage IGTF')
    amount_cc = fields.Monetary(string="Amount Company Currency", currency_field='company_currency_id', compute='_onchange_igtf', store=True)
    amount_igtf = fields.Monetary(string="Amount IGTF", currency_field='currency_id', compute='_onchange_igtf', store=True)
    amount_igtf_cc = fields.Monetary(string="Amount IGTF Company Currency", currency_field='company_currency_id', compute='_onchange_igtf', store=True)
    total_pay_igtf = fields.Monetary(string="Total with IGTF", currency_field='currency_id', compute='_onchange_igtf', store=True)
    total_pay_igtf_cc = fields.Monetary(string="Total with IGTF Company Currency", currency_field='company_currency_id', compute='_onchange_igtf', store=True)
    pay_igtf = fields.Boolean(string='Pay IGTF')
    igtf_product_id = fields.Many2one('product.product', string='IGTF Product')

    @api.onchange('apply_igtf', 'company_id')
    def onchange_apply_igtf(self):
        for wi in self:
            wi.percentage_igtf = wi.company_id.igtf_percentage
            wi.igtf_product_id = wi.company_id.igtf_product_id

    @api.depends('apply_igtf', 'amount', 'line_ids', 'company_id', 'currency_id', 'percentage_igtf', 'payment_date')
    def _onchange_igtf(self):
        for res in self:
            res.amount_cc = res.currency_id._convert(
                from_amount=res.amount,
                to_currency=res.company_currency_id,
                company=res.company_id,
                date=res.payment_date,
            )
            res.amount_cc = res.currency_id._convert(
                from_amount=res.amount,
                to_currency=res.company_currency_id,
                company=res.company_id,
                date=res.payment_date,
            )
            invoice = res.line_ids.mapped('move_id')
            if res.apply_igtf and res.percentage_igtf > 0 and len(invoice) == 1:
                amount = res.amount
                res.amount_igtf = amount * res.percentage_igtf / 100
                res.amount_igtf_cc = res.currency_id._convert(
                    from_amount=res.amount_igtf,
                    to_currency=res.company_currency_id,
                    company=res.company_id,
                    date=res.payment_date,
                )
                res.total_pay_igtf = res.amount + res.amount_igtf
                res.total_pay_igtf_cc = res.amount_cc + res.amount_igtf_cc
            else:
                res.amount_igtf = 0
                res.amount_igtf_cc = 0
                res.total_pay_igtf = res.amount
                res.total_pay_igtf_cc = res.amount_cc

    def _create_payments(self):
        amount_igtf = self.currency_id._convert(self.amount_igtf, self.source_currency_id, self.company_id, self.payment_date)
        if self.apply_igtf and amount_igtf > 0 and self.pay_igtf:
            self.amount = self.total_pay_igtf
        payments = super()._create_payments()
        invoice = self.line_ids.mapped('move_id')

        if self.apply_igtf and self.percentage_igtf > 0 and len(invoice) == 1 and amount_igtf:
            lines = invoice._get_reconciled_amls()
            self.line_ids.remove_move_reconcile()
            line_igtf_invoice = invoice.invoice_line_ids.filtered(lambda x: x.product_id.id == self.igtf_product_id.id)
            if line_igtf_invoice:
                line_igtf_invoice.price_unit += amount_igtf
            else:
                invoice.invoice_line_ids += self.env['account.move.line'].new({
                    'product_id': self.igtf_product_id.id,
                    'currency_id': invoice.currency_id.id,
                    'price_unit': amount_igtf,
                    'tax_ids': [(5,)],
                    'sequence': (max(invoice.invoice_line_ids.mapped('sequence')) + 1),
                })
            for account in lines.account_id:
                (lines + self.line_ids) \
                    .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)]) \
                    .reconcile()
        return payments
