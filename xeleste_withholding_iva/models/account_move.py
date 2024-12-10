from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _check_apply_withholdings(self):
        # TODO: verify validations
        if self.move_type in ['out_invoice', 'out_refund', 'out_receipt'] and self.company_id.iva_withholding_percentage \
                and self.amount_tax > 0 and self.partner_id.retention_agent:
            return True
        if self.move_type in ['in_invoice', 'in_refund', 'in_receipt'] and self.partner_id.iva_withholding_percentage \
                and self.amount_tax > 0:
            return True
        return super()._check_apply_withholdings()

    def _parse_withholding_iva(self, **default_vals):
        self.ensure_one()
        if self.withholding_ids.filtered(lambda w: w.withholding_method == 'iva'):
            return {}
        withholding_type = 'inbound' if self.move_type in ['out_invoice', 'out_refund', 'out_receipt'] else 'outbound'
        journal_id = self.env['account.journal'].search([
            ('use_withholding', '=', True),
            ('withholding_type', '=', 'iva'),
        ], limit=1)
        if not journal_id:
            raise UserError(_('You do not have a journal set up for IVA holds.'))

        withholding_vals = {
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'withholding_type': withholding_type,
            'partner_id': self.partner_id.id,
            'ref': self.name,
            'date': self.invoice_date or self.date or fields.Date.today(),
            'withholding_date': self.invoice_date,
            'withholding_method': 'iva',
            'journal_id': journal_id.id,
            'withholding_line_ids': []
        }
        for amount_by_group_list in self.tax_totals['groups_by_subtotal'].values():
            for amount_by_group in amount_by_group_list:
                if amount_by_group.get('ignore'):
                    continue
                withholding_vals['withholding_line_ids'].append((0, 0, {
                    'amount_origin': amount_by_group['tax_group_base_amount'],
                    'aliquot': amount_by_group['tax_group_name'],
                    'amount_base': amount_by_group['tax_group_amount'],
                    'move_id': self.id,
                    'percentage': self.partner_id.iva_withholding_percentage if withholding_type == 'outbound'
                    else self.company_id.iva_withholding_percentage
                }))

        if withholding_vals['withholding_line_ids']:
            return withholding_vals

        return {}

    def _generate_withholdings(self):
        withholdings = super()._generate_withholdings()
        if self.move_type in ['out_invoice', 'out_refund', 'out_receipt'] and self.company_id.iva_withholding_percentage \
                and self.amount_tax > 0 and self.partner_id.retention_agent:
            withholding_data = self._parse_withholding_iva()
            if withholding_data:
                withholdings |= self.env['account.withholding'].create(withholding_data)

        elif self.move_type in ['in_invoice', 'in_refund', 'in_receipt'] and self.partner_id.iva_withholding_percentage \
                and self.amount_tax > 0:
            withholding_data = self._parse_withholding_iva()
            if withholding_data:
                withholdings |= self.env['account.withholding'].create(withholding_data)
        return withholdings
