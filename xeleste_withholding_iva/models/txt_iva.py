import base64

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class TXTIVA(models.Model):
    _name = 'txt.iva'
    _description = 'TXT for IVA declaration'

    name = fields.Char(string='Period')
    date_start = fields.Date(string='Date Start')
    date_end = fields.Date(string='Date End')
    documents = fields.Selection([
        ('inbound', 'Sales'),
        ('outbound', 'Purchase'),
    ], string="Document types", required=True)
    withholding_ids = fields.Many2many('account.withholding', string='Withholdings')
    file = fields.Binary(attachment=True, string="TXT File", copy=False)
    file_name = fields.Char(store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('declared', 'Declared'),
    ], string="State", default="draft", tracking=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    error_msg = fields.Text('Error Msg')

    def action_declare(self):
        self.write({'state': 'declared'})

    def unlink(self):
        if self.state == 'declared':
            raise UserError(_('You cannot delete an already declared file'))
        return super(TXTIVA, self).unlink()

    def generate_txt(self):
        self.print_txt()

    def get_data(self):
        sql = """
            SELECT 
                CASE WHEN withh.withholding_type = 'inbound' THEN 
                    UPPER(SUBSTRING(partner.vat FROM 1 FOR 1)) || REGEXP_REPLACE(SUBSTRING(partner.vat FROM 2), '[^0-9]', '', 'g')
                ELSE UPPER(SUBSTRING(c_partner.vat FROM 1 FOR 1)) || REGEXP_REPLACE(SUBSTRING(c_partner.vat FROM 2), '[^0-9]', '', 'g') END AS rif,
                TO_CHAR(mov.date, 'YYYYMM') AS period,
                TO_CHAR(invoice.invoice_date, 'YYYY-MM-DD') AS invoice_date,
                CASE WHEN withh.withholding_type = 'inbound' THEN 'V'
                ELSE 'C' END    AS operation_type,
                CASE WHEN invoice.move_type IN ('in_refund', 'out_refund') THEN '03'
                    WHEN invoice.debit_origin_id IS NOT NULL THEN '02'
                ELSE '01' END   AS document_type,
                CASE WHEN withh.withholding_type = 'inbound' THEN 
                    UPPER(SUBSTRING(c_partner.vat FROM 1 FOR 1)) || REGEXP_REPLACE(SUBSTRING(c_partner.vat FROM 2), '[^0-9]', '', 'g')
                ELSE UPPER(SUBSTRING(partner.vat FROM 1 FOR 1)) || REGEXP_REPLACE(SUBSTRING(partner.vat FROM 2), '[^0-9]', '', 'g') END AS rif_supplier,
                CASE WHEN invoice.move_type IN ('in_invoice', 'in_receipt', 'in_refund') THEN invoice.ref
                ELSE invoice.name END               AS document_number,
                invoice.l10n_ve_control_number      AS control_number,
                TO_CHAR(invoice.amount_total, 'FM999999990.00')                AS amount_total,
                TO_CHAR(invoice.amount_untaxed - COALESCE(no_tax.exempt, 0), 'FM999999990.00')              AS amount_untaxed,
                TO_CHAR(ABS(with_line.amount_withholding), 'FM999999990.00')        AS iva_with,
                CASE WHEN invoice.move_type = 'in_refund' THEN origin_refund.ref
                    WHEN invoice.move_type = 'out_refund' THEN origin_refund.name
                    WHEN invoice.move_type IN ('in_invoice', 'in_receipt') AND invoice.debit_origin_id IS NOT NULL THEN origin_debit.ref
                    WHEN invoice.move_type IN ('out_invoice', 'out_receipt') AND invoice.debit_origin_id IS NOT NULL THEN origin_debit.name
                ELSE '0' END    AS document_affect,
                withh.number     AS number_with,
                TO_CHAR(COALESCE(no_tax.exempt, 0), 'FM999999990.00')   AS exempt,
                COALESCE(TO_CHAR(CAST(REGEXP_REPLACE(with_line.aliquot, '[^0-9]', '', 'g') AS NUMERIC), 'FM999999990.00'), '0.00') AS aliquot,
                '0'             AS file
            FROM account_withholding withh
            JOIN res_partner partner ON partner.id = withh.partner_id
            JOIN account_withholding_line with_line ON withh.id = with_line.withholding_id
            JOIN account_move mov ON mov.id = withh.move_id
            JOIN account_move invoice ON invoice.id = with_line.move_id
            LEFT JOIN account_move origin_refund ON origin_refund.id = invoice.reversed_entry_id
            LEFT JOIN account_move origin_debit ON origin_debit.id = invoice.debit_origin_id
            JOIN res_company company ON company.id = mov.company_id
            JOIN res_partner c_partner ON c_partner.id = company.partner_id
            LEFT JOIN (
                SELECT 
                    a_line.move_id      AS invoice_id,
                    COALESCE(SUM(a_line.price_subtotal), 0) AS exempt
                FROM account_move_line a_line
                LEFT JOIN account_move_line_account_tax_rel tax_rel ON tax_rel.account_move_line_id = a_line.id
                LEFT JOIN account_tax tax ON tax.id = tax_rel.account_tax_id
                WHERE tax.l10n_ve_aliquot_type = 'exempt' OR tax_rel.account_move_line_id IS NULL
                GROUP BY a_line.move_id
            ) no_tax        ON no_tax.invoice_id = invoice.id
            
            WHERE withh.withholding_method = 'iva' AND mov.state = 'posted'
            AND mov.company_id = %s
            AND withh.withholding_type = %s
        """

        self.env.cr.execute(sql, (self.company_id.id, self.documents))

        results = self.env.cr.fetchall()

        if not results:
            results = [(
                self.company_id.partner_id.vat.strip().upper().replace('-', ''),
                self.date_start.strftime('%Y%m'),
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            )]

        return results

    def print_txt(self):
        results = self.get_data()
        errors = ''

        content = ''
        count = 0
        for line in results:
            count += 1
            content += '\t'.join([str(item) for item in line])
            content += '\n'

            # validations
            if not line[0]:
                errors += _('There is no rif registered for line %s\n') % count
            if line[0] and line[0][0] not in ('J', 'V', 'P', 'G', 'C'):
                errors += _('Bad rif on line %s\n') % count
            elif line[0] and len(line[0][1:]) < 9:
                errors += _('Bad rif on line %s\n') % count
            if line[12] and len(line[12]) != 14:
                errors += _('the length of the receipt number is different than 14 on line %s\n') % count

        self.error_msg = errors
        self.file = base64.encodebytes(bytes(content, 'utf-8'))
        self.file_name = self.name + '.txt'

