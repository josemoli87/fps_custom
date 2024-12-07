# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class DocumentType(models.Model):
    """Document Type"""
    _name = 'document.type'
    _description = __doc__
    _rec_name = 'document_type'

    document_type = fields.Char(string="Document", required=True)


class VehicleDocument(models.Model):
    """Vehicle Document"""
    _name = 'vehicle.document'
    _description = __doc__
    _rec_name = 'document_type_id'

    vehicle_information_id = fields.Many2one('vehicle.information', string="VIN")
    vehicle_brand_id = fields.Many2one(related="vehicle_information_id.vehicle_brand_id", string="Vehicle")
    document_type_id = fields.Many2one('document.type', string="Document Name")
    file_name = fields.Char(string="File Name")
    avatar = fields.Binary(string="Upload Document")
