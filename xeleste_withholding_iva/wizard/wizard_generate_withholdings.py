from odoo import fields, models, api, _
from odoo.exceptions import UserError


class WizardGenerateWithholding(models.TransientModel):
    _inherit = 'wizard.generate.withholding'

    def _get_withholding_methods(self):
        res = super()._get_withholding_methods()
        res.append(('iva', _('IVA Withholding')))
        return res

    withholding_method = fields.Selection(selection=_get_withholding_methods)
    iva_withholding_percentage = fields.Float(related='invoice_id.partner_id.iva_withholding_percentage', readonly=False)
    iva_company_percentage = fields.Float(related='invoice_id.company_id.iva_withholding_percentage', readonly=True)
    retention_agent = fields.Boolean(related='invoice_id.partner_id.retention_agent', readonly=False)

    @api.onchange('retention_agent')
    def _onchange_retention_agent(self):
        self._onchange_warning_msg()

    @api.onchange('invoice_id', 'withholding_method', 'iva_withholding_percentage')
    def _onchange_warning_msg(self):
        for res in self:
            if res.withholding_method == 'iva':
                if not res.retention_agent and res.move_type in ['out_invoice', 'out_refund', 'out_receipt']:
                    res.warning_msg = _('Este Contribuyente no es agente de retención.')
                    return
                elif not res.iva_withholding_percentage and res.move_type in ['in_invoice', 'in_refund', 'in_receipt']:
                    res.warning_msg = _('You have not specified a retention percentage.')
                    return
                elif not res.iva_company_percentage and res.move_type in ['out_invoice', 'out_refund', 'out_receipt']:
                    res.warning_msg = _('You have not specified a retention percentage.')
                    return
                elif res.invoice_id.amount_tax <= 0:
                    res.warning_msg = _('This document does not have taxes.')
                    return
        super()._onchange_warning_msg()
