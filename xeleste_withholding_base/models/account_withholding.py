from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountWithholding(models.Model):
    _name = 'account.withholding'
    _inherits = {'account.move': 'move_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Withholdings"
    _order = "date desc, name desc"
    _check_company_auto = True

    # == Business fields ==
    number = fields.Char(string="Number Withholding")
    move_id = fields.Many2one(comodel_name='account.move', string='Journal Entry', required=True, readonly=True,
                              ondelete='cascade', check_company=True)
    is_reconciled = fields.Boolean(string="Is Reconciled", store=True,
                                   help="Technical field indicating if the withholding is already reconciled.")
    is_matched = fields.Boolean(string="Is Matched With a Bank Statement", store=True,
                                help="Technical field indicating if the withholding has been matched with a statement line.")
    withholding_date = fields.Date(string="Withholding Date")
    withholding_line_ids = fields.One2many('account.withholding.line', 'withholding_id', string="Lines")
    ut_price = fields.Float(string='UT Price')
    reported = fields.Boolean(string="Reported")
    warning_msg = fields.Char(string="Warning")

    # == Synchronized fields with the account.move.lines ==
    amount = fields.Monetary(currency_field='currency_id', compute='_compute_amounts', store=True)
    amount_base = fields.Monetary(string="Amount Base", currency_field='currency_id', compute='_compute_amounts', store=True)
    amount_signed = fields.Monetary(
        currency_field='currency_id', compute='_compute_amount_signed', tracking=False,
        help='Negative value of amount field if withholding_type is outbound')
    withholding_type = fields.Selection([
        ('outbound', 'Vendor Withholding'),
        ('inbound', 'Customer Withholding'),
    ], string='Withholding Type', default='inbound', required=True)
    withholding_method = fields.Selection([('standard', 'Standard')], string='Withholding Method', required=True,
                                          default='standard', ondelete='set default')
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
                                  compute='_compute_currency_id',
                                  help="The withholding's currency.")
    partner_id = fields.Many2one(comodel_name='res.partner', string="Customer/Vendor", store=True, readonly=False,
                                 ondelete='restrict', check_company=True,
                                 domain="['|', ('parent_id','=', False), ('is_company','=', True)]")
    outstanding_account_id = fields.Many2one(comodel_name='account.account', string="Outstanding Account", store=True,
                                             compute='_compute_outstanding_account_id', check_company=True)
    destination_account_id = fields.Many2one(comodel_name='account.account', string='Destination Account', store=True,
                                             readonly=False, compute='_compute_destination_account_id',
                                             domain="[('account_type', 'in', ('asset_receivable', 'liability_payable'))]",
                                             check_company=True)

    # # == Stat buttons ==
    invoice_ids = fields.Many2many('account.move', string="Invoices",
                                              compute='_compute_invoice_ids',
                                              help="Invoices whose journal items have been reconciled with these withholdings.")
    invoices_count = fields.Integer(string="# Invoices",
                                               compute="_compute_invoice_ids")


    # =====================
    # Business Methods
    # =====================

    @api.onchange('invoice_ids', 'withholding_date')
    def _onchange_warning_msg(self):
        for res in self:
            origin_invoices = res.invoice_ids.mapped('debit_origin_id') | res.invoice_ids.mapped('reversed_entry_id')
            if origin_invoices and origin_invoices.mapped('withholding_ids').\
                    filtered(lambda x: x.withholding_method == res.withholding_method and
                                       x.withholding_date.month != res.withholding_date.month):

                res.warning_msg = _('This withholding is in a different period than your source document.')
            else:
                res.warning_msg = ''

    def _search_default_journal(self):
        journal_id = self.env['account.journal'].search([
            ('use_withholding', '=', True),
            ('withholding_type', '=', self.withholding_method),
        ], limit=1)
        return journal_id

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        ''' Prepare the dictionary to create the default account.move.lines for the current withholding.
        :param write_off_line_vals: Optional list of dictionaries to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        self.ensure_one()
        write_off_line_vals = write_off_line_vals or {}

        if not self.outstanding_account_id:
            raise UserError(_(
                "You can't create a new withholding without an outstanding withholdings account set either on the company or the %s withholding method in the %s journal.",
                self.withholding_type, self.journal_id.display_name))

        # Compute amounts.
        write_off_line_vals_list = write_off_line_vals or []
        amount = self.amount if self.withholding_type == 'inbound' else -self.amount
        liquidity_balance = self.currency_id._convert(
            self.amount,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        liquidity_balance = liquidity_balance if self.withholding_type == 'inbound' else -liquidity_balance
        counterpart_balance = -liquidity_balance
        currency_id = self.currency_id.id

        line_vals_list = [
            # Liquidity line.
            {
                'name': _('reference %s' % self.number),
                'date_maturity': self.date,
                'amount_currency': amount,
                'currency_id': currency_id,
                'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.outstanding_account_id.id,
            },
            # Receivable / Payable.
            {
                'name': _('reference %s' % self.number),
                'date_maturity': self.date,
                'amount_currency': -amount,
                'currency_id': currency_id,
                'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.destination_account_id.id,
            },
        ]
        return line_vals_list + write_off_line_vals_list

    @api.model
    def _get_trigger_fields_to_synchronize(self):
        return ['date', 'amount', 'currency_id', 'partner_id', 'destination_account_id', 'journal_id',
                'withholding_type']

    def _synchronize_to_moves(self, changed_fields):
        ''' Update the account.move regarding the modified account.withholding.
        :param changed_fields: A list containing all modified fields on account.withholding.
        '''
        if self._context.get('skip_account_move_synchronization'):
            return

        if not any(field_name in changed_fields for field_name in self._get_trigger_fields_to_synchronize()):
            return

        for wi in self.with_context(skip_account_move_synchronization=True):
            wi.move_id.line_ids.unlink()
            line_vals_list = wi._prepare_move_line_default_vals()

            wi.move_id\
                .with_context(skip_invoice_sync=True)\
                .write({
                    'partner_id': wi.partner_id.id,
                    'currency_id': wi.currency_id.id,
                    'line_ids': [(0, 0, line_vals) for line_vals in line_vals_list],
                })

    def action_post(self):
        ''' draft -> posted '''
        self.move_id._post(soft=False)
        domain = [
            ('parent_state', '=', 'posted'),
            ('account_id.account_type', 'in', ('asset_receivable', 'liability_payable')),
            ('reconciled', '=', False),
        ]
        withholding_line = self.move_id.line_ids.filtered_domain(domain)
        (withholding_line + self.invoice_ids.line_ids).filtered_domain([('account_id', '=', withholding_line.account_id.id)]) \
            .reconcile()

    def action_draft(self):
        ''' posted -> draft '''
        self.move_id.button_draft()

    def button_open_journal_entry(self):
        ''' Redirect the user to this withholding journal.
        :return:    An action on account.move.
        '''
        self.ensure_one()
        return {
            'name': _("Journal Entry"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False},
            'view_mode': 'form',
            'res_id': self.move_id.id,
        }

    def button_open_invoices(self):
        ''' Redirect the user to the invoice(s) paid by this withholding.
        :return:    An action on account.move.
        '''
        self.ensure_one()

        action = {
            'name': _("Withheld invoices"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False},
        }
        if len(self.invoice_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.invoice_ids.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', self.invoice_ids.ids)],
            })
        return action

    def get_sequence(self):
        return False

    # -------------------------------------------------------------------------
    # LOW-LEVEL METHODS
    # -------------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        write_off_line_vals_list = []
        for vals in vals_list:
            write_off_line_vals_list.append(vals.pop('write_off_line_vals', None))

            # Force the move_type to avoid inconsistency with residual 'default_move_type' inside the context.
            vals['move_type'] = 'entry'
            vals['journal_id'] = vals.get('journal_id') or self._search_default_journal or self.move_id._search_default_journal().id

        withholdings = super().create([{
            'name': False,
            **vals,
        } for vals in vals_list])

        for i, wi in enumerate(withholdings):
            sequence = wi.get_sequence()
            if not wi.number and sequence:
                number = self.env['ir.sequence'].next_by_code(sequence)
                wi.number = number
            write_off_line_vals = write_off_line_vals_list[i]
            to_write = {}
            for k, v in vals_list[i].items():
                if k in self._fields and self._fields[k].store and k in wi.move_id._fields and wi.move_id._fields[k].store:
                    to_write[k] = v

            if 'line_ids' not in vals_list[i]:
                to_write['line_ids'] = [(0, 0, line_vals) for line_vals in wi._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)]

            wi.move_id.write(to_write)
            self.env.add_to_compute(self.env['account.move']._fields['name'], wi.move_id)

        withholdings.invalidate_recordset(fnames=['name'])
        return withholdings

    def write(self, vals):
        # OVERRIDE
        res = super().write(vals)
        if vals.get('withholding_line_ids'):
            self._compute_amounts()
        self._synchronize_to_moves(set(vals.keys()))
        return res

    def unlink(self):
        moves = self.with_context(force_delete=True).move_id
        res = super().unlink()
        moves.unlink()
        return res

    @api.depends('move_id.name')
    def _compute_display_name(self):
        for withholding in self:
            withholding.display_name = withholding.move_id.name if withholding.move_id.name != '/' else _('Draft Withholing')

    # =====================
    # COMPUTES
    # =====================
    @api.depends('journal_id')
    def _compute_currency_id(self):
        for withholding in self:
            withholding.currency_id = withholding.journal_id.currency_id or withholding.journal_id.company_id.currency_id

    @api.depends('amount', 'withholding_type')
    def _compute_amount_signed(self):
        for withholding in self:
            if withholding.withholding_type == 'outbound':
                withholding.amount_signed = -withholding.amount
            else:
                withholding.amount_signed = withholding.amount

    @api.depends('journal_id', 'withholding_type')
    def _compute_outstanding_account_id(self):
        for wi in self:
            method_line_id = wi.journal_id._get_available_payment_method_lines(wi.withholding_type)
            account_id = False
            if method_line_id:
                account_id = method_line_id[0].payment_account_id

            if wi.withholding_type == 'inbound':
                wi.outstanding_account_id = (account_id
                                              or wi.journal_id.company_id.account_journal_payment_debit_account_id) # TODO: Create accounts
            elif wi.withholding_type == 'outbound':
                wi.outstanding_account_id = (account_id
                                              or wi.journal_id.company_id.account_journal_payment_credit_account_id) # TODO: Create accounts
            else:
                wi.outstanding_account_id = False

    @api.depends('journal_id', 'partner_id', 'withholding_type')
    def _compute_destination_account_id(self):
        self.destination_account_id = False
        for wi in self:
            if wi.withholding_type == 'inbound':
                # Receive money from invoice or send money to refund it.
                if wi.partner_id:
                    wi.destination_account_id = wi.partner_id.with_company(
                        wi.company_id).property_account_receivable_id
                else:
                    wi.destination_account_id = self.env['account.account'].search([
                        *self.env['account.account']._check_company_domain(wi.company_id),
                        ('account_type', '=', 'asset_receivable'),
                        ('deprecated', '=', False),
                    ], limit=1)
            elif wi.withholding_type == 'outbound':
                # Send money to pay a bill or receive money to refund it.
                if wi.partner_id:
                    wi.destination_account_id = wi.partner_id.with_company(wi.company_id).property_account_payable_id
                else:
                    wi.destination_account_id = self.env['account.account'].search([
                        *self.env['account.account']._check_company_domain(wi.company_id),
                        ('account_type', '=', 'liability_payable'),
                        ('deprecated', '=', False),
                    ], limit=1)

    @api.depends('withholding_line_ids', 'withholding_line_ids.amount_base', 'withholding_line_ids.amount_withholding',
                 'currency_id')
    def _compute_amounts(self):
        for withholding in self:
            withholding.amount = sum(withholding.withholding_line_ids.mapped('amount_withholding'))
            withholding.amount_base = sum(withholding.withholding_line_ids.mapped('amount_base'))

    @api.depends('withholding_line_ids', 'withholding_line_ids.move_id', 'withholding_line_ids.move_id.line_ids')
    def _compute_invoice_ids(self):
        for wi in self:
            invoices = wi.withholding_line_ids.mapped('move_id')
            wi.invoice_ids = invoices
            wi.invoices_count = len(invoices)


class AccountWithholdingLine(models.Model):
    _name = 'account.withholding.line'
    _description = "Withholding's Lines"

    withholding_id = fields.Many2one('account.withholding', string='Withholding')
    move_line_id = fields.Many2one('account.move.line', string='Origin Line')
    move_id = fields.Many2one('account.move', string='Origin Invoice')
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
                                  compute='_compute_currency_id')
    amount_origin = fields.Monetary(string="Amount Origin", currency_field='currency_id')
    percentage = fields.Float(string="Percentage Withholding")
    amount_base = fields.Monetary(string="Amount Base", currency_field='currency_id')
    amount_withholding = fields.Monetary(string='Amount Withholding', compute='_compute_amounts', store=True,
                                         currency_field='currency_id')

    @api.depends('withholding_id')
    def _compute_currency_id(self):
        for line in self:
            line.currency_id = line.withholding_id.currency_id

    @api.depends('amount_origin', 'percentage', 'amount_base', 'move_line_id', 'move_id', 'move_id.move_type',
                 'currency_id')
    def _compute_amounts(self):
        for line in self:
            if line.withholding_id.withholding_method == 'standard':
                withholding = (line.percentage / 100) * line.amount_base
                line.amount_withholding = -withholding if line.move_id.move_type in ['out_refund', 'in_refund'] else withholding
            else:
                line.amount_withholding = 0
