from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    person_type_ve = fields.Selection([
        ('PNR', 'RESIDENT NATURAL PERSON (PNR)'),
        ('PNNR', 'NON-RESIDENT NATURAL PERSON (PNNR)'),
        ('PJD', 'DOMICILED LEGAL PERSON (PJD)'),
        ('PJND', 'NON-DOMICILED LEGAL PERSON (PJND)'),
        ('PJNCD', 'PERSONA JURÍDICA NO CONSTITUIDA DOMICILIADA (PJNCD)')
    ], string='Person Type')
    iva_withholding_percentage = fields.Float(string="IVA withholding percentage")
    retention_agent = fields.Boolean(string="Agente de Retencion")

    @api.constrains('vat', 'country_id', 'l10n_latam_identification_type_id')
    def check_vat(self):
        # no check Venezuela
        if self.country_id == self.env.ref('base.ve'):
            return True


  