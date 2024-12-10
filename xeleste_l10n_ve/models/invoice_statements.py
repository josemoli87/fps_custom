from odoo import fields, models, api


class InvoiceStatements(models.Model):
    _name = 'invoice.statements'
    _description = 'Invoice Statements'
    _rec_name = 'document_number'

    move_id = fields.Many2one('account.move', string="Invoice", required=True, ondelete='cascade',
                                 domain=[('move_type', 'in', ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt'))])
    move_type = fields.Selection(related='move_id.move_type')
    date = fields.Date(string='Date', required=True)
    invoice_date = fields.Date(string='Invoice Date', required=True)
    partner_vat = fields.Char(string='RIF Partner')
    partner_name = fields.Char(string='Name Partner', required=True)
    document_type = fields.Selection([
        ('invoice', 'Invoice'),
        ('credit', 'Credit Note'),
        ('debit', 'Debit Note'),
    ], string="Document Type", default='invoice', required=True)
    system_number = fields.Char(string='System Number', required=True)
    document_number = fields.Char(string='Document Number', required=True)
    control_number = fields.Char(string='Control Number')
    affect_document = fields.Char(string='Affect Document')
    amount_total = fields.Float(string='Amount Total')
    amount_untaxed = fields.Float(string="Amount Untaxed")
    amount_tax = fields.Float(string='Amount Tax')
    is_modified = fields.Boolean(string="Modified")
    state = fields.Selection([
        ('no_declared', 'No Declared'),
        ('declared', 'Declared'),
    ], string="State", default='no_declared', required=True)
    declared_date = fields.Date(string='Declared Date')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def action_declare(self):
        self.write({'state': 'declared', 'declared_date': fields.Date.today()})

