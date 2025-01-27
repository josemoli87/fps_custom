# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class VehiclePartInfo(models.Model):
    """Vehicle Part Info"""
    _name = "vehicle.part.info"
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True)
    type = fields.Selection(
        [('exterior', "Exterior"), ('interior', "Interior"),
         ('under_hood', "Under Hood"), ('under_vehicle', "Under Vehicle"),
         ('fluids', "Fluids"), ('tires', "Tires"),
         ('brake_condition', "Brake Condition")], string="Type")

    @api.constrains('type')
    def _constrain_check_part_type(self):
        for record in self:
            if not record.type:
                raise ValidationError(_("Please select a any one type of part"))


class ExteriorVehiclePart(models.Model):
    """Exterior Vehicle Part"""
    _name = "exterior.vehicle.part"
    _description = __doc__
    _rec_name = 'vehicle_part_info_id'

    avatar = fields.Binary(string="Avatar")
    vehicle_part_info_id = fields.Many2one('vehicle.part.info',
                                           string="Part", domain=[('type', '=', 'exterior')])
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete='cascade')

    okay_for_now = fields.Boolean()
    further_attention = fields.Boolean()
    required_attention = fields.Boolean()
    not_inspected = fields.Boolean()

    def action_okay_for_now_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.okay_for_now = True
        self.required_attention = False
        self.further_attention = False
        self.not_inspected = False

    def action_okay_for_now_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.okay_for_now = False

    def action_further_attention_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.further_attention = True
        self.okay_for_now = False
        self.required_attention = False
        self.not_inspected = False

    def action_further_attention_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.further_attention = False

    def action_required_attention_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.required_attention = True
        self.further_attention = False
        self.okay_for_now = False
        self.not_inspected = False

    def action_required_attention_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.required_attention = False

    def action_not_inspected_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.not_inspected = True
        self.okay_for_now = False
        self.required_attention = False
        self.further_attention = False

    def action_not_inspected_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.not_inspected = False


class InteriorVehiclePart(models.Model):
    """Interior Vehicle Part"""
    _name = "interior.vehicle.part"
    _description = __doc__
    _rec_name = 'vehicle_part_info_id'

    avatar = fields.Binary(string="Avatar")
    vehicle_part_info_id = fields.Many2one('vehicle.part.info',
                                           string="Part", domain=[('type', '=', 'interior')])
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete='cascade')

    okay_for_now = fields.Boolean()
    further_attention = fields.Boolean()
    required_attention = fields.Boolean()
    not_inspected = fields.Boolean()

    def action_okay_for_now_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.okay_for_now = True
        self.required_attention = False
        self.further_attention = False
        self.not_inspected = False

    def action_okay_for_now_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.okay_for_now = False

    def action_further_attention_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.further_attention = True
        self.okay_for_now = False
        self.required_attention = False
        self.not_inspected = False

    def action_further_attention_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.further_attention = False

    def action_required_attention_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.required_attention = True
        self.further_attention = False
        self.okay_for_now = False
        self.not_inspected = False

    def action_required_attention_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.required_attention = False

    def action_not_inspected_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.not_inspected = True
        self.okay_for_now = False
        self.required_attention = False
        self.further_attention = False

    def action_not_inspected_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.not_inspected = False


class UnderHoodVehiclePart(models.Model):
    """Under Hood Vehicle Part"""
    _name = "under.hood.vehicle.part"
    _description = __doc__
    _rec_name = 'vehicle_part_info_id'

    avatar = fields.Binary(string="Avatar")
    vehicle_part_info_id = fields.Many2one('vehicle.part.info',
                                           string="Part", domain=[('type', '=', 'under_hood')])
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete='cascade')

    okay_for_now = fields.Boolean()
    further_attention = fields.Boolean()
    required_attention = fields.Boolean()
    not_inspected = fields.Boolean()

    def action_okay_for_now_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.okay_for_now = True
        self.required_attention = False
        self.further_attention = False
        self.not_inspected = False

    def action_okay_for_now_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.okay_for_now = False

    def action_further_attention_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.further_attention = True
        self.okay_for_now = False
        self.required_attention = False
        self.not_inspected = False

    def action_further_attention_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.further_attention = False

    def action_required_attention_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.required_attention = True
        self.further_attention = False
        self.okay_for_now = False
        self.not_inspected = False

    def action_required_attention_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.required_attention = False

    def action_not_inspected_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.not_inspected = True
        self.okay_for_now = False
        self.required_attention = False
        self.further_attention = False

    def action_not_inspected_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.not_inspected = False


class UnderVehiclePart(models.Model):
    """Under Vehicle Part"""
    _name = "under.vehicle.part"
    _description = __doc__
    _rec_name = 'vehicle_part_info_id'

    avatar = fields.Binary(string="Avatar")
    vehicle_part_info_id = fields.Many2one('vehicle.part.info',
                                           string="Part", domain=[('type', '=', 'under_vehicle')])
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete='cascade')

    okay_for_now = fields.Boolean()
    further_attention = fields.Boolean()
    required_attention = fields.Boolean()
    not_inspected = fields.Boolean()

    def action_okay_for_now_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.okay_for_now = True
        self.required_attention = False
        self.further_attention = False
        self.not_inspected = False

    def action_okay_for_now_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.okay_for_now = False

    def action_further_attention_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.further_attention = True
        self.okay_for_now = False
        self.required_attention = False
        self.not_inspected = False

    def action_further_attention_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.further_attention = False

    def action_required_attention_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.required_attention = True
        self.further_attention = False
        self.okay_for_now = False
        self.not_inspected = False

    def action_required_attention_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.required_attention = False

    def action_not_inspected_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.not_inspected = True
        self.okay_for_now = False
        self.required_attention = False
        self.further_attention = False

    def action_not_inspected_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.not_inspected = False


class FluidsVehiclePart(models.Model):
    """Fluids Vehicle Part"""
    _name = "fluids.vehicle.part"
    _description = __doc__
    _rec_name = 'vehicle_part_info_id'

    avatar = fields.Binary(string="Avatar")
    vehicle_part_info_id = fields.Many2one('vehicle.part.info',
                                           string="Part", domain=[('type', '=', 'fluids')])
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete='cascade')

    okay_for_now = fields.Boolean()
    further_attention = fields.Boolean()
    required_attention = fields.Boolean()
    not_inspected = fields.Boolean()
    filled = fields.Boolean()

    def action_okay_for_now_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.okay_for_now = True
        self.required_attention = False
        self.further_attention = False
        self.not_inspected = False
        self.filled = False

    def action_okay_for_now_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.okay_for_now = False

    def action_further_attention_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.further_attention = True
        self.okay_for_now = False
        self.required_attention = False
        self.not_inspected = False
        self.filled = False

    def action_further_attention_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.further_attention = False

    def action_required_attention_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.required_attention = True
        self.further_attention = False
        self.okay_for_now = False
        self.not_inspected = False
        self.filled = False

    def action_required_attention_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.required_attention = False

    def action_not_inspected_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.not_inspected = True
        self.okay_for_now = False
        self.required_attention = False
        self.further_attention = False
        self.filled = False

    def action_not_inspected_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.not_inspected = False

    def action_filled_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.filled = True
        self.not_inspected = False
        self.okay_for_now = False
        self.required_attention = False
        self.further_attention = False

    def action_filled_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.filled = False


class VehiclePartTires(models.Model):
    """Vehicle Part Tires"""
    _name = "vehicle.part.tires"
    _description = __doc__
    _rec_name = 'vehicle_part_info_id'

    avatar = fields.Binary(string="Avatar")
    vehicle_part_info_id = fields.Many2one('vehicle.part.info',
                                           string="Tire Pressure", domain=[('type', '=', 'tires')])
    incoming = fields.Char(string="Incoming")
    adjusted_to = fields.Char(string="Adjusted to")
    tread_depth = fields.Char(string="Tread Depth")
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete='cascade')

    okay_for_now = fields.Boolean()
    further_attention = fields.Boolean()
    required_attention = fields.Boolean()
    not_inspected = fields.Boolean()

    def action_okay_for_now_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.okay_for_now = True
        self.required_attention = False
        self.further_attention = False
        self.not_inspected = False

    def action_okay_for_now_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.okay_for_now = False

    def action_further_attention_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.further_attention = True
        self.okay_for_now = False
        self.required_attention = False
        self.not_inspected = False

    def action_further_attention_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.further_attention = False

    def action_required_attention_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.required_attention = True
        self.further_attention = False
        self.okay_for_now = False
        self.not_inspected = False

    def action_required_attention_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.required_attention = False

    def action_not_inspected_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.not_inspected = True
        self.okay_for_now = False
        self.required_attention = False
        self.further_attention = False

    def action_not_inspected_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.not_inspected = False


class VehicleBrakeCondition(models.Model):
    """Vehicle Brake Condition"""
    _name = "vehicle.brake.condition"
    _description = __doc__
    _rec_name = 'vehicle_part_info_id'

    avatar = fields.Binary(string="Avatar")
    vehicle_part_info_id = fields.Many2one('vehicle.part.info', string="Part",
                                           domain=[('type', '=', 'brake_condition')])
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete='cascade')

    okay_for_now = fields.Boolean()
    further_attention = fields.Boolean()
    required_attention = fields.Boolean()
    not_inspected = fields.Boolean()

    def action_okay_for_now_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.okay_for_now = True
        self.required_attention = False
        self.further_attention = False
        self.not_inspected = False

    def action_okay_for_now_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.okay_for_now = False

    def action_further_attention_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.further_attention = True
        self.okay_for_now = False
        self.required_attention = False
        self.not_inspected = False

    def action_further_attention_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.further_attention = False

    def action_required_attention_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.required_attention = True
        self.further_attention = False
        self.okay_for_now = False
        self.not_inspected = False

    def action_required_attention_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.required_attention = False

    def action_not_inspected_accept(self):
        if self._context.get('click_from_tree'):
            return
        self.not_inspected = True
        self.okay_for_now = False
        self.required_attention = False
        self.further_attention = False

    def action_not_inspected_reject(self):
        if self._context.get('click_from_tree'):
            return
        self.not_inspected = False
