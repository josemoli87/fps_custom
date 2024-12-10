from odoo import fields, models


class TaxUnit(models.Model):
    _name = 'tax.unit'
    _description = 'Tax Unit'

    date = fields.Date(string='Date')
    price = fields.Float(string='Price')
    currency_id = fields.Many2one('res.currency', string='Currency')
    company_id = fields.Many2one('res.company', string='Company')
