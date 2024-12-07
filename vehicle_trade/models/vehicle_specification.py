# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class VehicleSpecification(models.Model):
    """Vehicle Specification"""
    _name = 'vehicle.specification'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True)


class VehicleSpecificationUsed(models.Model):
    """Vehicle Specification"""
    _name = 'vehicle.specification.used'
    _description = __doc__
    _rec_name = 'vehicle_specification_id'

    vehicle_specification_id = fields.Many2one('vehicle.specification', required=True, string="Title")
    used = fields.Char(string="Description")
    vehicle_information_id = fields.Many2one('vehicle.information')