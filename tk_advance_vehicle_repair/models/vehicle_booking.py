# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class VehicleBooking(models.Model):
    """Vehicle Booking"""
    _name = 'vehicle.booking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'booking_number'

    booking_number = fields.Char(string='Booking No', readonly=True, default=lambda self: _('New'), copy=False)
    booking_date = fields.Date(string="Booking Date", default=fields.Date.today)
    vehicle_brand_id = fields.Many2one('vehicle.brand', string="Vehicle Brand")
    vehicle_model_id = fields.Many2one('vehicle.model', string="Model",
                                       domain="[('vehicle_brand_id', '=', vehicle_brand_id)]")
    vehicle_fuel_type_id = fields.Many2one('vehicle.fuel.type', string="Fuel Type")
    registration_no = fields.Char(string="Registration No", translate=True)
    vin_no = fields.Char(string="VIN No", translate=True)
    transmission_type = fields.Selection([('manual', "Manual"),
                                          ('automatic', "Automatic"),
                                          ('cvt', "CVT")], string="Transmission Type")

    customer_id = fields.Many2one('res.partner', string='Customer')
    street = fields.Char(string="Street", translate=True)
    street2 = fields.Char(string="Street 2", translate=True)
    city = fields.Char(string="City", translate=True)
    country_id = fields.Many2one("res.country", string="Country")
    state_id = fields.Many2one("res.country.state", string="State",
                               domain="[('country_id', '=?', country_id)]")
    zip = fields.Char(string="Zip")
    phone = fields.Char(string="Phone", translate=True)
    email = fields.Char(string="Email", translate=True)
    customer_observation = fields.Text(string="Customer Observation", translate=True)
    responsible_id = fields.Many2one('res.users', default=lambda self: self.env.user,
                                     string="Responsible")

    booking_source = fields.Selection([('direct', "Direct"), ('website', "Website")],
                                      string="Booking Source", default='direct')
    booking_type = fields.Selection(
        [('only_inspection', "Only Vehicle Inspection"),
         ('only_repair', "Only Vehicle Repair"),
         ('inspection_and_repair', "Vehicle Inspection + Vehicle Repair")],
        string="Booking Type", default='only_inspection')

    estimate_cost = fields.Monetary(string="Estimate Cost")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  related="company_id.currency_id")

    vehicle_service_ids = fields.Many2many('vehicle.service', string=" Services")
    vehicle_spare_part_ids = fields.Many2many('product.product', string='Spare Parts',
                                              domain="[('is_vehicle_part', '=', True)]")

    inspection_job_card_id = fields.Many2one('inspection.job.card', string="Inspection Job Card")
    repair_job_card_id = fields.Many2one('repair.job.card', string="Repair Job Card")

    booking_stages = fields.Selection(
        [('draft', "New"),
         ('vehicle_inspection', "Vehicle Inspection"),
         ('vehicle_repair', "Vehicle Repair"),
         ('vehicle_inspection_repair', "Inspection + Repair"),
         ('cancel', "Cancelled")], default='draft',
        string="Stages", group_expand='_expand_groups', tracking=True)

    vehicle_from = fields.Selection(
        [('new', "New"),
         ('fleet_vehicle', "Vehicle From Fleet"),
         ('customer_vehicle', "Vehicle From Customer")], string="Vehicle From", default='new')
    is_registered_vehicle = fields.Boolean(string="Registered")
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Fleet")
    register_vehicle_id = fields.Many2one('register.vehicle', string="Registered Vehicle",
                                          domain="[('customer_id', '=', customer_id)]")

    booking_appointment_id = fields.Many2one('booking.appointment', string="Appointment Day")
    booking_appointment_slot_id = fields.Many2one('booking.appointment.slot', string="Booking Slot",
                                                  domain="[('booking_appointment_id', '=', booking_appointment_id)]")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('booking_number', _('New')) == _('New'):
                vals['booking_number'] = self.env['ir.sequence'].next_by_code('vehicle.booking') or _('New')
        res = super(VehicleBooking, self).create(vals_list)
        return res

    def write(self, vals_list):
        rec = super(VehicleBooking, self).write(vals_list)
        self.customer_id.write({
            'name': self.customer_id.name,
            'street': self.street,
            'street2': self.street2,
            'city': self.city,
            'country_id': self.country_id.id,
            'state_id': self.state_id.id,
            'zip': self.zip,
            'phone': self.phone,
            'email': self.email,
        })
        return rec

    @api.model
    def _expand_groups(self, states, domain, order):
        return ['draft', 'vehicle_inspection', 'vehicle_repair', 'vehicle_inspection_repair', 'cancel']

    def draft_to_vehicle_inspection(self):
        """Vehicle Inspection Job Card Create"""
        if not self.vehicle_brand_id or not self.registration_no or not self.vehicle_model_id or not self.vehicle_fuel_type_id:
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _("Required: Vehicle, Registration No, Model, and Fuel Type for mandatory information."),
                    'sticky': False,
                }
            }
            return message
        inspection_job_card_id = self.env['inspection.job.card'].create({
            "vehicle_brand_id": self.vehicle_brand_id.id,
            "vehicle_model_id": self.vehicle_model_id.id,
            "inspection_date": self.booking_date,
            "vehicle_fuel_type_id": self.vehicle_fuel_type_id.id,
            "registration_no": self.registration_no,
            "fleet_vehicle_id": self.fleet_vehicle_id.id,
            "register_vehicle_id": self.register_vehicle_id.id,
            "vehicle_from": self.vehicle_from,
            "is_registered_vehicle": self.is_registered_vehicle,
            "vin_no": self.vin_no,
            "transmission_type": self.transmission_type,
            "customer_id": self.customer_id.id,
            "street": self.street,
            "street2": self.street2,
            "city": self.city,
            "state_id": self.state_id.id,
            "country_id": self.country_id.id,
            "zip": self.zip,
            "phone": self.phone,
            "email": self.email,
            "inspect_type": self.booking_type,
            "customer_observation": self.customer_observation,
            "responsible_id": self.env.user.id if self.env.user.has_group(
                'tk_advance_vehicle_repair.vehicle_repair_technician') else False,
        })
        self.write({
            'inspection_job_card_id': inspection_job_card_id.id,
            'booking_stages': 'vehicle_inspection'
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Inspection Job Card'),
            'res_model': 'inspection.job.card',
            'res_id': inspection_job_card_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def vehicle_inspection_to_vehicle_repair(self):
        """Vehicle Repair Job Card Create"""
        if not self.vehicle_brand_id or not self.registration_no or not self.vehicle_model_id or not self.vehicle_fuel_type_id:
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _("Required: Vehicle, Registration No, Model, and Fuel Type for mandatory information."),
                    'sticky': False,
                }
            }
            return message
        repair_job_card_id = self.env['repair.job.card'].create({
            "vehicle_brand_id": self.vehicle_brand_id.id,
            "vehicle_model_id": self.vehicle_model_id.id,
            "inspect_repair_date": self.booking_date,
            "vehicle_fuel_type_id": self.vehicle_fuel_type_id.id,
            "registration_no": self.registration_no,
            "fleet_vehicle_id": self.fleet_vehicle_id.id,
            "register_vehicle_id": self.register_vehicle_id.id,
            "vehicle_from": self.vehicle_from,
            "is_registered_vehicle": self.is_registered_vehicle,
            "vin_no": self.vin_no,
            "transmission_type": self.transmission_type,
            "customer_id": self.customer_id.id,
            "street": self.street,
            "street2": self.street2,
            "city": self.city,
            "state_id": self.state_id.id,
            "country_id": self.country_id.id,
            "zip": self.zip,
            "phone": self.phone,
            "email": self.email,
            "customer_observation": self.customer_observation,
        })
        self.write({
            'repair_job_card_id': repair_job_card_id.id,
            'booking_stages': 'vehicle_repair'
        })
        # Required Parts
        for part in self.vehicle_spare_part_ids:
            part = {
                'product_id': part.id,
                'unit_price': part.lst_price,
                'repair_job_card_id': repair_job_card_id.id,
            }
            self.env['vehicle.order.spare.part'].create(part)
        # Required Services
        for service in self.vehicle_service_ids:
            service = {
                'vehicle_service_id': service.id,
                'service_charge': service.service_charge,
                'repair_job_card_id': repair_job_card_id.id
            }
            self.env['vehicle.service.team'].create(service)
        # Return the form view of the newly created repair job card
        return {
            'type': 'ir.actions.act_window',
            'name': _('Repair Job Card'),
            'res_model': 'repair.job.card',
            'res_id': repair_job_card_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def vehicle_repair_to_vehicle_inspection_repair(self):
        """Vehicle Inspection and Repair Job Card Create"""
        if not self.vehicle_brand_id or not self.registration_no or not self.vehicle_model_id or not self.vehicle_fuel_type_id:
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _("Required: Vehicle, Registration No, Model, and Fuel Type for mandatory information."),
                    'sticky': False,
                }
            }
            return message
        inspection_job_card_id = self.env['inspection.job.card'].create({
            "vehicle_brand_id": self.vehicle_brand_id.id,
            "vehicle_model_id": self.vehicle_model_id.id,
            "inspection_date": self.booking_date,
            "vehicle_fuel_type_id": self.vehicle_fuel_type_id.id,
            "registration_no": self.registration_no,
            "fleet_vehicle_id": self.fleet_vehicle_id.id,
            "register_vehicle_id": self.register_vehicle_id.id,
            "vehicle_from": self.vehicle_from,
            "is_registered_vehicle": self.is_registered_vehicle,
            "vin_no": self.vin_no,
            "transmission_type": self.transmission_type,
            "customer_id": self.customer_id.id,
            "street": self.street,
            "street2": self.street2,
            "city": self.city,
            "state_id": self.state_id.id,
            "country_id": self.country_id.id,
            "zip": self.zip,
            "phone": self.phone,
            "email": self.email,
            "inspect_type": self.booking_type,
            "customer_observation": self.customer_observation,
            "responsible_id": self.env.user.id if self.env.user.has_group(
                'tk_advance_vehicle_repair.vehicle_repair_technician') else False,
        })
        self.write({
            'inspection_job_card_id': inspection_job_card_id.id,
            'booking_stages': 'vehicle_inspection_repair'
        })
        # Required Parts
        for s_part in self.vehicle_spare_part_ids:
            s_part = {
                'product_id': s_part.id,
                'unit_price': s_part.lst_price,
                'inspection_job_card_id': inspection_job_card_id.id,
            }
            self.env['vehicle.spare.part'].create(s_part)
        # Required Services
        for s_service in self.vehicle_service_ids:
            s_service = {
                'vehicle_service_id': s_service.id,
                'service_charge': s_service.service_charge,
                'inspection_job_card_id': inspection_job_card_id.id
            }
            self.env['inspection.repair.team'].create(s_service)
        # Return the form view of the newly created inspection job card
        return {
            'type': 'ir.actions.act_window',
            'name': _('Inspection Job Card'),
            'res_model': 'inspection.job.card',
            'res_id': inspection_job_card_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def vehicle_inspection_repair_to_cancel(self):
        """Cancel Stage"""
        self.booking_stages = 'cancel'

    @api.onchange('booking_date')
    def _onchange_booking_days(self):
        """Appointment Day Wise Slot Visible"""
        if self.booking_date:
            day = self.booking_date.strftime("%A").lower()
            booking_appointment = self.env['booking.appointment'].sudo().search([('appointment_day', '=', day)])
            self.booking_appointment_id = booking_appointment.id

    @api.onchange('fleet_vehicle_id', 'vehicle_from')
    def _onchange_fleet_vehicle(self):
        """Fleet Vehicle Details"""
        for rec in self:
            if rec.vehicle_from == 'fleet_vehicle' and rec.fleet_vehicle_id:
                rec.vehicle_brand_id = rec.fleet_vehicle_id.vehicle_brand_id.id
                rec.vehicle_model_id = rec.fleet_vehicle_id.vehicle_model_id.id
                rec.vehicle_fuel_type_id = rec.fleet_vehicle_id.vehicle_fuel_type_id.id
                rec.transmission_type = rec.fleet_vehicle_id.transmission_type
                rec.registration_no = rec.fleet_vehicle_id.license_plate
                rec.vin_no = rec.fleet_vehicle_id.vin_no
            else:
                rec.transmission_type = ''
                rec.registration_no = ''
                rec.vin_no = ''
                rec.vehicle_brand_id = False
                rec.vehicle_model_id = False
                rec.vehicle_fuel_type_id = False

    @api.onchange('register_vehicle_id', 'vehicle_from')
    def _onchange_customer_vehicle(self):
        """Customer Vehicle Details"""
        for rec in self:
            if rec.vehicle_from == 'customer_vehicle' and rec.register_vehicle_id:
                rec.vehicle_brand_id = rec.register_vehicle_id.vehicle_brand_id.id
                rec.vehicle_model_id = rec.register_vehicle_id.vehicle_model_id.id
                rec.vehicle_fuel_type_id = rec.register_vehicle_id.vehicle_fuel_type_id.id
                rec.transmission_type = rec.register_vehicle_id.transmission_type
                rec.registration_no = rec.register_vehicle_id.registration_no
                rec.vin_no = rec.register_vehicle_id.vin_no
            else:
                rec.transmission_type = ''
                rec.registration_no = ''
                rec.vin_no = ''
                rec.vehicle_brand_id = False
                rec.vehicle_model_id = False
                rec.vehicle_fuel_type_id = False

    @api.onchange('customer_id')
    def _onchange_customer_details(self):
        """Customer Details"""
        for rec in self:
            rec.phone = rec.customer_id.phone
            rec.email = rec.customer_id.email
            rec.street = rec.customer_id.street
            rec.street2 = rec.customer_id.street2
            rec.city = rec.customer_id.city
            rec.state_id = rec.customer_id.state_id
            rec.country_id = rec.customer_id.country_id
            rec.zip = rec.customer_id.zip

    def action_create_vehicle_registration(self):
        """Register Vehicle In Customer"""
        if not self.vehicle_brand_id or not self.vehicle_model_id:
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _(
                        "Please provide the vehicle name and model along with any other relevant vehicle details."),
                    'sticky': False,
                }
            }
            return message
        register_vehicle_id = self.env['register.vehicle'].create({
            'customer_id': self.customer_id.id,
            'vehicle_brand_id': self.vehicle_brand_id.id,
            'vehicle_model_id': self.vehicle_model_id.id,
            'vehicle_fuel_type_id': self.vehicle_fuel_type_id.id,
            'registration_no': self.registration_no,
            'vin_no': self.vin_no,
            'transmission_type': self.transmission_type,
        })
        self.write({
            'register_vehicle_id': register_vehicle_id.id,
            'vehicle_from': 'customer_vehicle',
            'is_registered_vehicle': True
        })
