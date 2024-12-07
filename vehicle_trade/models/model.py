# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class ResPartner(models.Model):
    """Vehicle Vendor"""
    _inherit = 'res.partner'
    _description = __doc__

    is_vendor = fields.Boolean(string="Vendor")


class SaleInvoice(models.Model):
    """Sale Invoice"""
    _inherit = 'account.move'
    _description = __doc__

    vehicle_information_id = fields.Many2one('vehicle.information', string="Vehicle Trade")