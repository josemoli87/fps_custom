# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class VehicleInsuranceType(models.Model):
    """Vehicle Insurance Type"""
    _name = 'vehicle.insurance.type'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True)


class VehicleInsurance(models.Model):
    """Vehicle Insurance"""
    _name = 'vehicle.insurance'
    _description = __doc__
    _rec_name = 'vehicle_insurance_type_id'

    vehicle_insurance_type_id = fields.Many2one('vehicle.insurance.type', string="Insurance", required=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    insurance_status = fields.Selection([('running', "Running"), ('expired', 'Expired')], string="Status")
    vehicle_information_id = fields.Many2one('vehicle.information')

    @api.onchange('insurance_status')
    def onchange_to_insurance_status(self):
        for record in self:
            if record.insurance_status:
                record.vehicle_insurance_type_id = record.vehicle_insurance_type_id
            else:
                record.vehicle_insurance_type_id = False
