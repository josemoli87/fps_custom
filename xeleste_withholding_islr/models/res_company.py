from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def create(self, vals):
        company = super(ResCompany, self).create(vals)
        self.env['ir.sequence'].create({
            'name': _('Withholding ISLR %s') % company.name,
            'padding': 5,
            # 'prefix': 'WTH/',
            'code': 'withholding.islr.%s' % company.id,
            'company_id': company.id,
        })
        return company
