# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class PreviousServiceHistory(models.Model):
    """Previous Service History"""
    _name = 'previous.service.history'
    _description = __doc__
    _rec_name = 'title'

    title = fields.Char(string="Title")
    date_of_service = fields.Date(string="Date of Service")
    odometer_reading = fields.Integer(string="Odometer Reading")
    previous_service_description = fields.Char(string="Description")
    vehicle_information_id = fields.Many2one('vehicle.information')
