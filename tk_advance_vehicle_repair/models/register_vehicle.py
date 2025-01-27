# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class RegisterVehicle(models.Model):
    """Register Vehicle"""
    _name = 'register.vehicle'
    _description = __doc__
    _rec_name = 'display_name'

    display_name = fields.Char(compute='_compute_display_name', store=True)
    customer_id = fields.Many2one('res.partner', string='Customer')
    vehicle_brand_id = fields.Many2one('vehicle.brand', string="Vehicle")
    vehicle_model_id = fields.Many2one('vehicle.model', string="Model",
                                       domain="[('vehicle_brand_id', '=', vehicle_brand_id)]")
    registration_no = fields.Char(string="Registration No")
    vehicle_fuel_type_id = fields.Many2one('vehicle.fuel.type', string="Fuel Type")
    transmission_type = fields.Selection([
        ('manual', "Manual"),
        ('automatic', "Automatic"),
        ('cvt', "CVT")],
        string="Transmission Type")
    vin_no = fields.Char(string="VIN Number")

    @api.model_create_multi
    def create(self, vals_list):
        """Check if a registration number already exists before creating a new record."""
        for vals in vals_list:
            registration_no = vals.get('registration_no')
            if registration_no:
                existing_record = self.search([('registration_no', '=', registration_no)], limit=1)
                if existing_record:
                    raise ValidationError(_(
                        f"Registration '{registration_no}' is already in use. Please try a different one."))
        return super(RegisterVehicle, self).create(vals_list)

    @api.depends('vehicle_brand_id', 'vehicle_model_id', 'registration_no')
    def _compute_display_name(self):
        for rec in self:
            brand_name = rec.vehicle_brand_id.name or ''
            model_name = rec.vehicle_model_id.name or ''
            registration_no = rec.registration_no or ''
            rec.display_name = f"{brand_name}/{model_name}/{registration_no}"
