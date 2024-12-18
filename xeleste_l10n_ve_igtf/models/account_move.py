from odoo import fields, models, api
from odoo.tools.misc import formatLang


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends_context('lang')
    @api.depends(
        'invoice_line_ids.currency_rate',
        'invoice_line_ids.tax_base_amount',
        'invoice_line_ids.tax_line_id',
        'invoice_line_ids.price_total',
        'invoice_line_ids.price_subtotal',
        'invoice_payment_term_id',
        'partner_id',
        'currency_id',
    )
    def _compute_tax_totals(self):
        super()._compute_tax_totals()
        for move in self:
            # TODO: buscar una mejor manera para esto
            lines_igtf = move.invoice_line_ids.filtered(lambda l: l.product_id.id == move.company_id.igtf_product_id.id)
            igtf_amount = sum(lines_igtf.mapped('price_total'))

            if igtf_amount:
                tax_totals = move.tax_totals
                if not tax_totals:
                    continue
                amount_untaxed = tax_totals['amount_untaxed']
                move.tax_totals.update({
                    'amount_untaxed': amount_untaxed - igtf_amount,
                    'formatted_amount_untaxed': formatLang(self.env, amount_untaxed - igtf_amount, currency_obj=move.currency_id),
                })
                if not move.tax_totals['subtotals']:
                    move.tax_totals['subtotals'] = [{
                        'name': 'Base Imponible',
                        'amount': amount_untaxed,
                        'formatted_amount': formatLang(self.env, amount_untaxed, currency_obj=move.currency_id),
                    }]
                base = move.tax_totals['subtotals']
                base[0].update({
                    'amount': base[0]['amount'] - igtf_amount,
                    'formatted_amount': formatLang(self.env, base[0]['amount'] - igtf_amount, currency_obj=move.currency_id),
                })

                if not move.tax_totals['subtotals_order']:
                    move.tax_totals['subtotals_order'] = ['Base Imponible']
                if not move.tax_totals['groups_by_subtotal']:
                    move.tax_totals['groups_by_subtotal'] = {'Base Imponible': []}

                is_company_currency_requested = move.currency_id != move.company_id.currency_id
                percentage = move.company_id.igtf_percentage or 3
                igtf_values = {
                    'tax_group': 'IGTF 3%',
                    'tax_group_name': 'IGTF 3%',
                    'tax_group_amount': igtf_amount,
                    'tax_amount': igtf_amount,
                    'tax_group_base_amount': igtf_amount * 100 / percentage,
                    'base_amount': igtf_amount * 100 / percentage,
                    'formatted_tax_group_amount': formatLang(self.env, igtf_amount, currency_obj=move.currency_id),
                    'formatted_tax_group_base_amount': formatLang(self.env, igtf_amount * 100 / percentage, currency_obj=move.currency_id),
                    'ignore': True,
                    'hide_base_amount': False,
                }
                if is_company_currency_requested:
                    comp_currency = move.company_id.currency_id
                    igtf_company_amount = comp_currency.round(move.currency_id._convert(
                        igtf_amount,
                        comp_currency,
                        move.company_id,
                        move.invoice_date or move.date or fields.Date.today(),
                    ))
                    igtf_base_company_amount = comp_currency.round(move.currency_id._convert(
                            igtf_amount * 100 / percentage,
                            comp_currency,
                            move.company_id,
                            move.invoice_date or move.date or fields.Date.today(),
                        ))
                    igtf_values.update({
                        'base_amount_company_currency': igtf_base_company_amount,
                        'tax_amount_company_currency': igtf_company_amount,
                        'tax_group_amount_company_currency': igtf_company_amount,
                        'tax_group_base_amount_company_currency': igtf_base_company_amount,
                        'amount_total_company_currency': igtf_company_amount,
                    })
                move.tax_totals['groups_by_subtotal'][tax_totals['subtotals_order'][0]] += [igtf_values]
