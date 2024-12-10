from odoo import fields, models, api, _


class WizardGenerateWithholding(models.TransientModel):
    _inherit = 'wizard.generate.withholding'

    def _get_withholding_methods(self):
        res = super()._get_withholding_methods()
        res.append(('islr', _('ISLR Withholding')))
        return res

    withholding_method = fields.Selection(selection=_get_withholding_methods)
    table_islr_ids = fields.Many2many('table.islr', string='Concept ISLR', readonly=True)
    person_type = fields.Selection(related='invoice_id.partner_id.person_type_ve', readonly=False, string='Person Type')
    company_person_type = fields.Selection(related='invoice_id.company_id.partner_id.person_type_ve', string='Person Type (Company)')

    @api.onchange('invoice_id', 'withholding_method')
    def _onchange_table_islr_ids(self):
        for wizard in self:
            if self.withholding_method == 'islr':
                wizard.table_islr_ids = wizard.invoice_id.mapped('invoice_line_ids.product_id.ve_table_islr_id')

    @api.onchange('person_type')
    def _onchange_person_type(self):
        self._onchange_warning_msg()

    @api.onchange('invoice_id', 'withholding_method', 'iva_withholding_percentage')
    def _onchange_warning_msg(self):
        for res in self:
            if res.withholding_method == 'islr':
                partner_id = res.invoice_id.company_id.partner_id if res.invoice_id.move_type in ['out_invoice', 'out_refund', 'out_receipt'] else res.invoice_id.partner_id
                if res.person_type:
                    partner_id.person_type_ve = res.person_type

                person_type = res.person_type or partner_id.person_type_ve
                table_islr_ids = res.invoice_id.mapped('invoice_line_ids.product_id.ve_table_islr_id')
                line_islr = table_islr_ids.mapped('line_ids').filtered(lambda x: x.person_type == person_type and (not x.more_that or res.invoice_id.amount_total >= x.more_that))

                if not res.person_type and res.move_type in ['in_invoice', 'in_refund', 'in_receipt']:
                    res.warning_msg = _('Set the person type.')
                    return
                elif not res.company_person_type and res.move_type in ['out_invoice', 'out_refund', 'out_receipt']:
                    res.warning_msg = _('Set the person type.')
                    return
                elif not table_islr_ids:
                    res.warning_msg = _('There are no products configured to apply ISLR withholdings.')
                    return
                elif not line_islr:
                    res.warning_msg = _('The type of person or the amount of the document do not apply to this withholding concept.')
                    return
                elif res.invoice_id.amount_total <= 0:
                    res.warning_msg = _('The document is at 0.')
                    return
        super()._onchange_warning_msg()
