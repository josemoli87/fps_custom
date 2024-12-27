# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class VehicleCondition(models.Model):
    """Vehicle Conditions"""
    _name = 'vehicle.condition'
    _description = __doc__
    _rec_name = "title"

    title = fields.Char(string="Title", required=True)
    condition = fields.Float(help="Gives the condition order when displaying a list of records.")
    vehicle_information_id = fields.Many2one('vehicle.information')
