from odoo import fields, models, api


class TableISLR(models.Model):
    _name = 'table.islr'
    _description = 'ISLR withholding table'

    name = fields.Char(string="Name")
    description = fields.Char(string="Description")
    date_start = fields.Date(string='Date Start')
    line_ids = fields.One2many('table.islr.line', 'table_id', string='Lines')
    active = fields.Boolean(string='Active', default=True)


class TableISLRLine(models.Model):
    _name = 'table.islr.line'
    _description = 'ISLR withholding line table'

    table_id = fields.Many2one('table.islr', string='Table', ondelete='cascade')
    code = fields.Char(string='Code')
    amount_base = fields.Float(string='Tax base', default=100.0)
    base_min = fields.Float(string='Min')
    base_max = fields.Float(string='Max')
    amount = fields.Float(string='Percentage')
    limit = fields.Float(string='Limit')
    more_that = fields.Float(string='More that', default=0.0)
    person_type = fields.Selection([
        ('PNR', 'RESIDENT NATURAL PERSON (PNR)'),
        ('PNNR', 'NON-RESIDENT NATURAL PERSON (PNNR)'),
        ('PJD', 'DOMICILED LEGAL PERSON (PJD)'),
        ('PJND', 'NON-DOMICILED LEGAL PERSON (PJND)'),
        ('PJNCD', 'PERSONA JURÍDICA NO CONSTITUIDA DOMICILIADA (PJNCD)'),
        ('all', 'ALL'),
    ], string='Person Type', default='all')

