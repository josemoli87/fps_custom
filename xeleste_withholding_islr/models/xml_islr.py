import base64
from io import BytesIO
import xml.etree.ElementTree as ET

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class XMLISLR(models.Model):
    _name = "xml.islr"
    _description = 'XML for ISLR declaration'

    name = fields.Char(string='Period')
    date_start = fields.Date(string='Date Start')
    date_end = fields.Date(string='Date End')
    documents = fields.Selection([
        ('inbound', 'Sales'),
        ('outbound', 'Purchase'),
    ], string="Document types", required=True, default='outbound')
    withholding_ids = fields.Many2many('account.withholding', string='Withholdings')
    file = fields.Binary(attachment=True, string="XML File", copy=False)
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
        return super(XMLISLR, self).unlink()

    def get_data(self):
        sql = """
            SELECT 
                UPPER(SUBSTRING(partner.vat FROM 1 FOR 1)) || LEFT(REGEXP_REPLACE(SUBSTRING(partner.vat FROM 2), '[^0-9]', '', 'g'), 9)   rif,
                CASE WHEN withh.withholding_type = 'outbound' THEN RIGHT(invoice.ref, 10)
                ELSE RIGHT(invoice.name, 10) END               AS document_number,
                COALESCE(RIGHT(SPLIT_PART(invoice.l10n_ve_control_number, '-', 2), 8), 'NA')       AS control_number,
                with_line.code_islr         AS code_islr,
                TO_CHAR(with_line.amount_base, 'FM999999990.00')        AS amount_base,
                TO_CHAR(with_line.percentage, 'FM999999990')            AS percentage
            FROM account_withholding withh
            JOIN res_partner partner ON partner.id = withh.partner_id
            JOIN account_withholding_line with_line ON withh.id = with_line.withholding_id
            JOIN account_move mov ON mov.id = withh.move_id
            JOIN account_move invoice ON invoice.id = with_line.move_id
            WHERE withh.withholding_method = 'islr' AND mov.state = 'posted'
            AND mov.company_id = %s
            AND withh.withholding_type = %s
        """

        self.env.cr.execute(sql, (self.company_id.id, self.documents))
        results = self.env.cr.dictfetchall()
        return results

    def generate_xml(self):
        results = self.get_data()
        root = ET.Element("RelacionRetencionesISLR", RifAgente=self.company_id.vat.upper().strip()[:10], Periodo=self.date_start.strftime('%Y%m'))
        for line in results:
            body = ET.SubElement(root, "DetalleRetencion")
            ET.SubElement(body, "RifRetenido").text = line['rif']
            ET.SubElement(body, "NumeroFactura").text = line['document_number']
            ET.SubElement(body, "NumeroControl").text = line['control_number']
            ET.SubElement(body, "CodigoConcepto").text = line['code_islr']
            ET.SubElement(body, "MontoOperacion").text = line['amount_base']  # TODO: verify credit note
            ET.SubElement(body, "PorcentajeRetencion").text = line['percentage']
        tree = ET.ElementTree(root)
        tree.write('islr.xml', encoding='utf-8')
        f = BytesIO()
        tree.write(f)
        f.seek(0)
        file = f.read()

        self.file = base64.encodebytes(bytes(file))
        self.file_name = self.name + '.xml'
