from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    person_type_ve = fields.Selection([
        ('PNR', 'RESIDENT NATURAL PERSON (PNR)'),
        ('PNNR', 'NON-RESIDENT NATURAL PERSON (PNNR)'),
        ('PJD', 'DOMICILED LEGAL PERSON (PJD)'),
        ('PJND', 'NON-DOMICILED LEGAL PERSON (PJND)'),
        ('PJNCD', 'PERSONA JURÍDICA NO CONSTITUIDA DOMICILIADA (PJNCD)')
    ], string='Person Type', default='PJD', related='partner_id.person_type_ve', readonly=False)
    iva_withholding_percentage = fields.Float(string="IVA withholding percentage", related='partner_id.iva_withholding_percentage', readonly=False)

    @api.model
    def create(self, vals):
        company = super(ResCompany, self).create(vals)
        self.env['ir.sequence'].create({
            'name': _('Control Number Sequence %s') % company.name,
            'padding': 5,
            'prefix': '00-',
            'code': 'control.number.%s' % company.id,
            'company_id': company.id,
        })
        return company

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    iva_withholding_percentage = fields.Float(string="IVA withholding percentage", related='company_id.iva_withholding_percentage',
                                              readonly=False)
    person_type_ve = fields.Selection(related='company_id.person_type_ve', readonly=False)
