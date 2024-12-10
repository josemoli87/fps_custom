from odoo import fields, models, api, _
from odoo.exceptions import UserError


class WizardGenerateWithholding(models.TransientModel):
    _name = 'wizard.generate.withholding'
    _description = 'Wizard for generate Withholding Manual'

    def _get_withholding_methods(self):
        # Here add the verification of the types of withholdings that can be applied
        return []

    invoice_id = fields.Many2one('account.move', string='Invoice')
    withholding_method = fields.Selection(selection=_get_withholding_methods, string='Withholding', required=True)
    warning_msg = fields.Char(string="Warning")
    auto_generate_after = fields.Boolean(string="Always generate for this client",
                                         help="Automatically generate withholdings when publishing the invoice for this client",
                                         related='invoice_id.partner_id.auto_withholding', readonly=False)
    move_type = fields.Selection(related='invoice_id.move_type')
    # TODO: CHANGE
    journal_id = fields.Many2one('account.journal', string="Journal", domain=[('type', 'in', ['cash', 'bank'])])
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        compute='_compute_currency_id', store=True, readonly=False, precompute=True,
        help="The withholding's currency.")

    def apply_withholding(self):
        if not self.withholding_method:
            UserError(_('Select the type of withholding to apply'))
        withholding_data = {}
        default_vals = {
            'currency_id': self.currency_id.id
        }

        try:
            parse_function = getattr(self.invoice_id, '_parse_withholding_' + self.withholding_method)
            withholding_data = parse_function(**default_vals)
        except Exception as e:
            UserError(_('Error generating this type of retention. Contact your administrator.\n %s' % e))

        if withholding_data:
            withholding_id = self.env['account.withholding'].create(withholding_data)
            self.invoice_id.withholding_ids = [(4, withholding_id.id)]

    @api.onchange('invoice_id', 'withholding_method', 'journal_id')
    def _onchange_warning_msg(self):
        for res in self:
            # add validations here
            if not self.withholding_method:
                res.warning_msg = _('Select the type of withholding to apply.')
            elif not self.journal_id:
                res.warning_msg = _('Select the journal.')
            elif self.invoice_id.amount_total == 0:
                res.warning_msg = _('You cannot apply withholdings to invoices with a zero amount.')
            else:
                res.warning_msg = False

    @api.onchange('withholding_method')
    def _onchange_journal(self):
        for res in self:
            journal_id = self.env['account.journal'].sudo().search([
                ('use_withholding', '=', True),
                ('withholding_type', '=', res.withholding_method),
                ('company_id', '=', res.invoice_id.company_id.id),
            ], limit=1)
            if journal_id:
                res.journal_id = journal_id

    @api.depends('journal_id')
    def _compute_currency_id(self):
        for wizard in self:
            wizard.currency_id = wizard.journal_id.currency_id or wizard.invoice_id.currency_id or wizard.company_id.currency_id
