from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _check_apply_withholdings(self):
        # TODO: verify validations
        partner_id = self.company_id.partner_id if self.move_type in ['out_invoice', 'out_refund', 'out_receipt'] else self.partner_id
        if partner_id.person_type_ve and self.amount_total:
            for line in self.invoice_line_ids:
                for islr_line in line.product_id.ve_table_islr_id.line_ids:
                    if islr_line.person_type == partner_id.person_type_ve and self.amount_total >= islr_line.more_that:
                        return True
        return super()._check_apply_withholdings()

    def _parse_withholding_islr(self, **default_vals):
        if self.withholding_ids.filtered(lambda w: w.withholding_method == 'islr'):
            return {}
        ut = self.env['tax.unit'].search([
            '|', ('company_id', '=', False), ('company_id', '=', self.company_id.id),
            ('date', '<=', self.invoice_date or self.date or fields.Date.today())
        ], order='company_id, date DESC', limit=1)
        if not ut:
            raise UserError(_('There is no tax unit registered to date. Cannot create ISLR hold.'))
        journal_id = self.env['account.journal'].search([
            ('use_withholding', '=', True),
            ('withholding_type', '=', 'islr'),
        ], limit=1)
        if not journal_id:
            raise UserError(_('You do not have a journal set up for ISLR holds.'))

        withholding_type = 'inbound' if self.move_type in ['out_invoice', 'out_refund', 'out_receipt'] else 'outbound'
        partner_id = self.company_id.partner_id if self.move_type in ['out_invoice', 'out_refund', 'out_receipt'] else self.partner_id
        withholding_vals = {
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'withholding_type': withholding_type,
            'partner_id': self.partner_id.id,
            'ref': self.name,
            'date': self.invoice_date or self.date or fields.Date.today(),
            'withholding_date': self.invoice_date,
            'withholding_method': 'islr',
            'journal_id': journal_id.id,
            'ut_price': ut.price,
            'withholding_line_ids': []
        }

        for islr_concept in self.mapped('invoice_line_ids.product_id.ve_table_islr_id'):
            lines = self.invoice_line_ids.filtered(lambda x: x.product_id.ve_table_islr_id.id == islr_concept.id)
            amount_origin = sum(lines.mapped('price_subtotal'))
            amount_ut = amount_origin / ut.price

            concept_line = islr_concept.line_ids.filtered(lambda l: l.person_type == partner_id.person_type_ve and
                                                                    amount_origin >= l.more_that and amount_ut >= l.base_min
                                                                    and (not l.base_max or amount_ut <= l.base_max))

            if concept_line:
                concept_line = concept_line[0]
            else:
                continue

            subt = 0
            if partner_id.person_type_ve == 'PNR':
                subt = 83.3334 * ut.price * (concept_line.amount / 100)
            amount_base = amount_origin * (concept_line.amount_base / 100)
            withholding = ((concept_line.amount / 100) * amount_base) - subt
            if withholding <= 0:
                continue
            withholding_vals['withholding_line_ids'].append((0, 0, {
                'amount_origin': amount_origin,
                'amount_base': amount_base,
                'move_id': self.id,
                'code_islr': concept_line.code,
                'concept_islr': islr_concept.name,
                'subt': subt,
                'percentage': concept_line.amount
            }))

        if withholding_vals['withholding_line_ids']:
            return withholding_vals
        return {}

    def _generate_withholdings(self):
        withholdings = super()._generate_withholdings()
        partner_id = self.company_id.partner_id if self.move_type in ['out_invoice', 'out_refund', 'out_receipt'] else self.partner_id
        if partner_id.person_type_ve and self.amount_total:
            generate = False
            for line in self.invoice_line_ids:
                for islr_line in line.product_id.ve_table_islr_id.line_ids:
                    if islr_line.person_type == partner_id.person_type_ve and self.amount_total >= islr_line.more_that:
                        generate = True
                        break

            if generate:
                withholding_data = self._parse_withholding_islr()
                if withholding_data:
                    withholdings |= self.env['account.withholding'].create(withholding_data)

        return withholdings
