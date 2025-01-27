# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class SaleOrder(models.Model):
    """Sale Order"""
    _inherit = 'sale.order'
    _description = __doc__

    inspection_job_card_id = fields.Many2one('inspection.job.card',
                                             string="Inspection Job card")
    repair_job_card_id = fields.Many2one('repair.job.card',
                                         string="Repair Job Card")
