from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_ve_control_number = fields.Char(string="Control Number", copy=False)
    statement_ids = fields.One2many("invoice.statements", 'move_id', string='Statements VE')

    def action_open_invoice_statements(self):
        self.ensure_one()
        return {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': "invoice.statements",
            'domain': [('move_id', '=', self.id)],
            'target': 'current',
        }

    def action_post(self):
        value = super().action_post()
        for move in self:
            if move.move_type in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt') and \
                    move.country_code == 'VE':
                doc_type = 'debit' if move.debit_origin_id else 'credit' if move.move_type in (
                'in_refund', 'out_refund') else 'invoice'
                vals = {
                    'move_id': move.id,
                    'date': move.date,
                    'invoice_date': move.invoice_date,
                    'partner_vat': move.partner_id.vat,
                    'partner_name': move.partner_id.name,
                    'document_type': doc_type,
                    'system_number': move.name,
                    'document_number': move.name if move.move_type in ('out_invoice', 'out_refund', 'out_receipt')
                        else move.ref,
                    'control_number': move.l10n_ve_control_number,
                    'affect_document': move.reversed_entry_id.ref if doc_type == 'credit' else move.debit_origin_id.ref
                        if doc_type == 'debit' else '',
                    'amount_total': move.amount_total,
                    'amount_untaxed': move.amount_untaxed,
                    'amount_tax': move.amount_tax,
                    'company_id': move.company_id.id,
                }

                statement = self.env['invoice.statements'].sudo().search([('state', '=', 'no_declared'),
                                                                          ('move_id', '=', move.id)])
                if statement:
                    statement.sudo().write(vals)
                    continue

                statement = self.env['invoice.statements'].sudo().search([
                    ('move_id', '=', move.id), ('date', '=', move.date), ('invoice_date', '=', move.invoice_date),
                    ('partner_vat', '=', vals['partner_vat']), ('partner_name', '=', vals['partner_name']),
                    ('document_type', '=', vals['document_type']), ('system_number', '=', vals['system_number']),
                    ('document_number', '=', vals['document_number']), ('control_number', '=', vals['control_number']),
                    ('affect_document', '=', vals['affect_document']), ('amount_total', '=', vals['amount_total']),
                    ('amount_tax', '=', vals['amount_tax']), ('company_id', '=', vals['company_id']),
                ])
                if not statement:
                    vals.update({'is_modified': bool(move.statement_ids)})
                    self.env['invoice.statements'].sudo().create(vals)

        return value

    def get_tax_by_aliquot_type(self):
        self.ensure_one()
        values = {'exempt': [0, 0, 0], 'reduced': [0, 0, 0], 'general': [0, 0, 0], 'additional': [0, 0, 0]}
        tax_ids = self.mapped('invoice_line_ids.tax_ids')
        group_list = self.tax_totals['groups_by_subtotal'].values()

        for groups in group_list:
            for amount_by_group in groups:
                if amount_by_group.get('ignore'):
                    continue
                tax_id = tax_ids.filtered(lambda x: x.tax_group_id.id == int(amount_by_group['group_key']))
                if not tax_id:
                    continue
                values[tax_id[0].l10n_ve_aliquot_type][0] += amount_by_group['tax_group_base_amount']
                values[tax_id[0].l10n_ve_aliquot_type][1] = tax_id.amount
                values[tax_id[0].l10n_ve_aliquot_type][2] += amount_by_group['tax_group_amount']

        return values

    @api.model_create_multi
    def create(self, vals_list):
        IrSequence = self.env["ir.sequence"]
        results = super().create(vals_list)
        for res in results:
            if res.move_type in ('out_invoice', 'out_receipt') and res.country_code == 'VE':
                res.l10n_ve_control_number = IrSequence.next_by_code("control.number.%s" % res.company_id.id)
        return results
