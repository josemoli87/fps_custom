# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class InspectionTemplate(models.Model):
    """Inspection Template"""
    _name = 'inspection.template'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True)
    inspection_template_item_ids = fields.One2many('inspection.template.item', 'inspection_template_id')


class InspectionTemplateItem(models.Model):
    """Inspection Template Item"""
    _name = 'inspection.template.item'
    _description = __doc__
    _rec_name = 'title'

    title = fields.Char(string="Title", required=True)
    inspection_template_id = fields.Many2one('inspection.template')


class ExpertInspectionTemplate(models.Model):
    """Expert Inspection Template"""
    _name = 'expert.inspection.template'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True)
    available = fields.Boolean(string="Available")
    description = fields.Char(string="Description")
    vehicle_information_id = fields.Many2one('vehicle.information')

    @api.onchange('available')
    def onchange_is_available(self):
        for record in self:
            if record.available:
                record.name = record.name
            else:
                record.name = False
