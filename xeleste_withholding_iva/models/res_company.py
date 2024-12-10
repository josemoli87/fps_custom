from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def create(self, vals):
        company = super(ResCompany, self).create(vals)
        self.env['ir.sequence'].create({
            'name': _('Withholding IVA %s') % company.name,
            'padding': 8,
            'prefix': '%(year)s%(month)s',
            'code': 'withholding.iva.%s' % company.id,
            'company_id': company.id,
        })
        return company
