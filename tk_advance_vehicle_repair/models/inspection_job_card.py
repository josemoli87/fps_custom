# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from email.policy import default

from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class InspectionImage(models.Model):
    """Inspection Image"""
    _name = "inspection.image"
    _description = __doc__
    _rec_name = 'name'

    avatar = fields.Binary(string="Avatar")
    name = fields.Char(string="Name", required=True, translate=True, size=36)
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete='cascade')


class InspectionJobCard(models.Model):
    """Inspection Job Card"""
    _name = 'inspection.job.card'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'inspection_number'

    inspection_number = fields.Char(string='Inspection No', readonly=True,
                                    default=lambda self: _('New'), copy=False)
    vehicle_brand_id = fields.Many2one('vehicle.brand', string="Brand")
    vehicle_model_id = fields.Many2one('vehicle.model', string="Model",
                                       domain="[('vehicle_brand_id', '=', vehicle_brand_id)]")
    vehicle_fuel_type_id = fields.Many2one('vehicle.fuel.type', string="Fuel Type")
    registration_no = fields.Char(string="Registration No", translate=True)
    vin_no = fields.Char(string="VIN No", translate=True)
    transmission_type = fields.Selection([('manual', "Manual"),
                                          ('automatic', "Automatic"),
                                          ('cvt', "CVT")], string="Transmission Type")

    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
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
    responsible_id = fields.Many2one('res.users', string="Inspected By")

    inspection_type = fields.Selection(
        [('full_inspection', "Full Inspection"),
         ('specific_inspection', "Specific Inspection")],
        default='full_inspection', string="Type of Inspection")

    inspect_type = fields.Selection([
        ('only_inspection', "Only Inspection"),
        ('inspection_and_repair', "Inspection + Repair")], string="Inspection Type")

    vehicle_booking_id = fields.Many2one('vehicle.booking', compute="_compute_vehicle_booking",
                                         string="Booking No")
    inspection_date = fields.Date(string="Date", default=fields.Date.today)
    inspection_charge_type = fields.Selection([('free', "Free"), ('paid', "Paid")], default='paid',
                                              string="Inspection Charge Type")
    inspection_charge = fields.Monetary(string="Inspection Charge")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  related="company_id.currency_id")

    # Part Assessment
    part_assessment = fields.Boolean(string="Part Assessment")
    wd = fields.Boolean(string="4WD")
    abs = fields.Boolean(string="ABS")
    awd = fields.Boolean(string="AWD")
    gps = fields.Boolean(string="GPS")
    stereo = fields.Boolean(string="Stereo")
    bed_liner = fields.Boolean(string="Bedliner")
    wide_tires = fields.Boolean(string="Wide Tires")
    power_locks = fields.Boolean(string="Power Locks")
    power_seats = fields.Boolean(string="Power Seats")
    power_windows = fields.Boolean(string="Power Windows")
    running_boards = fields.Boolean(string="Running Boards")
    roof_rack = fields.Boolean(string="Roof Rack")
    camper_shell = fields.Boolean(string="Camper Shell")
    sport_wheels = fields.Boolean(string="Sport Wheels")
    tilt_wheel = fields.Boolean(string="Tilt Wheel")
    cruise_control = fields.Boolean(string="Cruise Control")
    cvt_transmission = fields.Boolean(string="CVT Transmission")
    infotainment_system = fields.Boolean(string="Infotainment System")
    moon_sun_roof = fields.Boolean(string="Moon or Sun Roof")
    rear_sliding_window = fields.Boolean(string="Rear Sliding Window")
    rear_window_wiper = fields.Boolean(string="Rear Window Wiper")
    rear_lift_gate = fields.Boolean(string="Rear Liftgate")
    air_conditioning = fields.Boolean(string="Air Conditioning")
    leather_interior = fields.Boolean(string="Leather Interior")
    towing_package = fields.Boolean(string="Towing Package")
    auto_transmission = fields.Boolean(string="Automatic Transmission")
    am_fm_radio = fields.Boolean(string="AM / FM / Sirius Radio")
    cd_usb_bluetooth = fields.Boolean(string="CD / USB / Bluetooth")
    luxury_sport_pkg = fields.Boolean(string="Luxury / Sport pkg.")
    other = fields.Boolean(string="Other")

    # Inner Body Inspection
    inner_body_inspection = fields.Boolean(string="Inner Body Inspection")
    interior_item_condition_ids = fields.One2many(comodel_name='interior.item.condition',
                                                  inverse_name='inspection_job_card_id',
                                                  string="Interior Item")

    # Outer Body Inspection
    outer_body_inspection = fields.Boolean(string="Outer Body Inspection")
    vehicle_condition_line_ids = fields.One2many(comodel_name='vehicle.condition.line',
                                                 inverse_name='inspection_job_card_id',
                                                 string="Exterior Item")

    # Mechanical Condition
    mechanical_condition = fields.Boolean(string="Mechanical Condition")
    mechanical_item_condition_ids = fields.One2many(comodel_name='mechanical.item.condition',
                                                    inverse_name='inspection_job_card_id',
                                                    string="Mechanical Item")

    # Vehicle Components
    vehicle_component = fields.Boolean(string="Vehicle Component")
    vehicle_components_ids = fields.One2many(comodel_name='vehicle.components',
                                             inverse_name='inspection_job_card_id',
                                             string=" Vehicle Component")

    # Vehicle Fluids
    vehicle_fluid = fields.Boolean(string="Vehicle Fluid")
    vehicle_fluids_ids = fields.One2many(comodel_name='vehicle.fluids',
                                         inverse_name='inspection_job_card_id',
                                         string=" Vehicle Fluid")

    # Tyre Inspection
    tyre_inspection = fields.Boolean(string="Tire Inspection")
    tyre_inspection_ids = fields.One2many(comodel_name='tyre.inspection',
                                          inverse_name='inspection_job_card_id',
                                          string="Vehicle Tire")

    vehicle_spare_part_ids = fields.One2many(comodel_name='vehicle.spare.part',
                                             inverse_name='inspection_job_card_id',
                                             string="Required Spare Part")
    inspection_repair_team_ids = fields.One2many(comodel_name='inspection.repair.team',
                                                 inverse_name='inspection_job_card_id',
                                                 string="Required Service")
    repair_job_card_id = fields.Many2one('repair.job.card', string="Repair Job Card")

    part_price = fields.Monetary(compute="_compute_spare_part_price", string="Part Price")
    service_charge = fields.Monetary(compute="_compute_service_charge", string="Service Charges")
    sub_total = fields.Monetary(string="Sub Total", compute="_compute_sub_total")

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    sale_order_state = fields.Selection(related='sale_order_id.state', string="Order State")
    amount_total = fields.Monetary(related='sale_order_id.amount_total', string="Total Amount")
    sale_invoiced = fields.Monetary()

    check_list_template_id = fields.Many2one('checklist.template', string="Checklist Template")
    inspection_checklist_ids = fields.One2many(comodel_name='inspection.checklist',
                                               inverse_name='inspection_job_card_id',
                                               string="Checklist")

    vehicle_from = fields.Selection(
        [('new', "New"),
         ('fleet_vehicle', "Vehicle From Fleet"),
         ('customer_vehicle', "Vehicle From Customer")],
        string="Vehicle From", default='new')
    register_vehicle_id = fields.Many2one('register.vehicle', string="Registered Vehicle",
                                          domain="[('customer_id', '=', customer_id)]")
    is_registered_vehicle = fields.Boolean(string="Registered")
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Fleet")
    review_notes = fields.Text(string="Review Notes")
    date = fields.Date(string=" Date")
    signature = fields.Binary(string="Authorized Signature")
    inspection_image_ids = fields.One2many(comodel_name='inspection.image',
                                           inverse_name='inspection_job_card_id')

    inspection_report_type = fields.Selection(
        [('advanced_inspection', "Advanced Inspection"),
         ('classic_inspection', "Classic Inspection")],
        string="Inspection Report Type", default='advanced_inspection')

    exterior_vehicle_part_ids = fields.One2many(comodel_name='exterior.vehicle.part',
                                                inverse_name='inspection_job_card_id')
    interior_vehicle_part_ids = fields.One2many(comodel_name='interior.vehicle.part',
                                                inverse_name='inspection_job_card_id')
    under_hood_vehicle_part_ids = fields.One2many(comodel_name='under.hood.vehicle.part',
                                                  inverse_name='inspection_job_card_id')
    under_vehicle_part_ids = fields.One2many(comodel_name='under.vehicle.part',
                                             inverse_name='inspection_job_card_id')
    fluids_vehicle_part_ids = fields.One2many(comodel_name='fluids.vehicle.part',
                                              inverse_name='inspection_job_card_id')
    vehicle_part_tires_ids = fields.One2many(comodel_name='vehicle.part.tires',
                                             inverse_name='inspection_job_card_id',
                                             string="Tire Condition")
    vehicle_brake_condition_ids = fields.One2many(comodel_name='vehicle.brake.condition',
                                                  inverse_name='inspection_job_card_id',
                                                  string="Brake Condition")
    is_scratch_report = fields.Boolean(string="Custom Scratch Report")
    scratch_report_id = fields.Many2one('scratch.report', string="Scratch Report")
    quote_mail_send = fields.Boolean()
    inspection_repair_sale_order_id = fields.Many2one('sale.order', string=" Sale Order")
    is_skip_quotation = fields.Boolean(string="Skip Quotation")
    stages = fields.Selection(
        [('a_draft', "New"), ('b_in_progress', "In Progress"),
         ('in_review', "In Review"), ('reject', "Reject"),
         ('c_complete', "Completed"), ('d_cancel', "Cancelled"),
         ('locked', "Locked")], default='a_draft',
        group_expand='_expand_groups', tracking=True)

    # unused
    repair_sale_order_state = fields.Selection(related='inspection_repair_sale_order_id.state')
    repair_amount_total = fields.Monetary(related='inspection_repair_sale_order_id.amount_total',
                                          string=" Total Amount")
    team_task_count = fields.Integer(compute="_compute_team_task", string="Task")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('inspection_number', _('New')) == _('New'):
                vals['inspection_number'] = self.env['ir.sequence'].next_by_code('inspection.job.card') or _('New')
        res = super(InspectionJobCard, self).create(vals_list)
        return res

    def write(self, vals_list):
        rec = super(InspectionJobCard, self).write(vals_list)
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
        return ['a_draft', 'b_in_progress', 'in_review', 'reject', 'c_complete', 'locked', 'd_cancel']

    def a_draft_to_b_in_progress(self):
        """In Progress Stage"""
        self.stages = 'b_in_progress'

    def skip_quotation(self):
        """Skip Quotation"""
        self.stages = 'in_review'
        self.is_skip_quotation = True

    def b_in_progress_to_in_review(self):
        """In Review Stage"""
        self.stages = 'in_review'

    def in_review_to_reject(self):
        """Reject Stage"""
        self.stages = 'reject'

    def reject_to_c_complete(self):
        """Checklist Template Check"""
        if any(not rec.is_check and not rec.display_type for rec in self.inspection_checklist_ids):
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _("Please complete the checklist template"),
                    'sticky': False,
                }
            }
            return message
        mail_template = self.env.ref('tk_advance_vehicle_repair.inspection_job_card_mail_template')
        if mail_template:
            mail_template.send_mail(self.id, force_send=True)
        self.stages = 'c_complete'

    def c_complete_to_d_cancel(self):
        """Cancel Stage"""
        self.stages = 'd_cancel'

    def d_cancel_to_locked(self):
        """Locked Stage"""
        self.stages = 'locked'

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

    @api.onchange('check_list_template_id')
    def _onchange_check_list_template_id(self):
        """Inspection Checklist Template"""
        for rec in self:
            rec.inspection_checklist_ids = [(5, 0, 0)]  # Clear existing lines
            # Prepare new checklist items
            lines = []
            for data in rec.check_list_template_id.checklist_template_item_ids.sorted('sequence'):
                lines.append((0, 0, {
                    'name': data.name,
                    'sequence': data.sequence,
                    'display_type': data.display_type,
                }))
            # Update the checklist items
            rec.inspection_checklist_ids = lines

    @api.onchange('inspection_report_type')
    def _onchange_inspection_report_type(self):
        for rec in self:
            rec.inspection_type = 'full_inspection'

    @api.onchange('inspection_type', 'inspection_report_type')
    def _onchange_inspection_type(self):
        for rec in self:
            rec.part_assessment = False
            rec.inner_body_inspection = False
            rec.outer_body_inspection = False
            rec.tyre_inspection = False
            rec.mechanical_condition = False
            rec.vehicle_component = False
            rec.vehicle_fluid = False

    @api.constrains('inspect_type')
    def _check_inspect_type(self):
        """Check Inspection Type"""
        for record in self:
            if not record.inspect_type:
                raise ValidationError(
                    _("Select inspection type: 'Only Inspection' or 'Inspection + Repair' Make a choice to proceed."))

    @api.depends('inspection_repair_team_ids.service_charge')
    def _compute_service_charge(self):
        """Total Service Charges"""
        for rec in self:
            rec.service_charge = sum(service.service_charge for service in rec.inspection_repair_team_ids)

    @api.depends('vehicle_spare_part_ids.unit_price', 'vehicle_spare_part_ids.qty')
    def _compute_spare_part_price(self):
        """Total Spare Parts Price"""
        for rec in self:
            rec.part_price = sum(part.unit_price * part.qty for part in rec.vehicle_spare_part_ids)

    @api.depends('service_charge', 'part_price', 'inspection_charge')
    def _compute_sub_total(self):
        """Total Service and Spare Parts Price"""
        for rec in self:
            rec.sub_total = rec.service_charge + rec.part_price + rec.inspection_charge

    def _compute_vehicle_booking(self):
        """Vehicle Booking Details"""
        for rec in self:
            vehicle_booking_id = self.env['vehicle.booking'].search([('inspection_job_card_id', '=', rec.id)], limit=1)
            rec.vehicle_booking_id = vehicle_booking_id.id

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

    def create_repair_job_card(self):
        # Validate required fields
        if not self.vehicle_brand_id or not self.registration_no or not self.vehicle_model_id:
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _("Required: Vehicle, Registration No, and Model information."),
                    'sticky': False,
                }
            }
            return message
        # Create repair job card
        repair_job_card = self.env['repair.job.card'].create({
            "vehicle_brand_id": self.vehicle_brand_id.id,
            "vehicle_model_id": self.vehicle_model_id.id,
            "vehicle_fuel_type_id": self.vehicle_fuel_type_id.id,
            "register_vehicle_id": self.register_vehicle_id.id,
            "fleet_vehicle_id": self.fleet_vehicle_id.id,
            "registration_no": self.registration_no,
            "vin_no": self.vin_no,
            "transmission_type": self.transmission_type,
            "inspect_repair_date": self.inspection_date,
            "vehicle_from": self.vehicle_from,
            "is_registered_vehicle": self.is_registered_vehicle,
            "customer_id": self.customer_id.id,
            "street": self.street,
            "street2": self.street2,
            "city": self.city,
            "state_id": self.state_id.id,
            "country_id": self.country_id.id,
            "zip": self.zip,
            "phone": self.phone,
            "email": self.email,
            "repair_sale_order_id": self.sale_order_id.id,
            "repair_amount": self.amount_total,
            "repair_order_state": self.sale_order_state,
            "sub_total": self.sub_total,
            "is_skip_quotation": self.is_skip_quotation,
        })
        self.repair_job_card_id = repair_job_card.id
        # Create spare parts entries
        for part in self.vehicle_spare_part_ids:
            self.env['vehicle.order.spare.part'].create({
                'product_id': part.product_id.id,
                'qty': part.qty,
                'unit_price': part.unit_price,
                'repair_job_card_id': repair_job_card.id
            })
        # Create service team entries
        for service in self.inspection_repair_team_ids:
            self.env['vehicle.service.team'].create({
                'vehicle_service_id': service.vehicle_service_id.id,
                'start_date': service.start_date,
                'end_date': service.end_date,
                'service_charge': service.service_charge,
                'repair_job_card_id': repair_job_card.id,
            })
        # Return the form view of the newly created repair job card
        return {
            'type': 'ir.actions.act_window',
            'name': _('Repair Job Card'),
            'res_model': 'repair.job.card',
            'res_id': repair_job_card.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def create_inspection_repair_quotation(self):
        order_line = []
        sequence_number = 1
        # Check if inspection charge is provided
        if self.inspect_type == 'only_inspection':
            if self.inspection_charge_type == 'paid' and not self.inspection_charge:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'message': _("Kindly include the inspection charge amount."),
                        'sticky': False,
                    }
                }
            # Add line section for Inspection Charges
            order_line.append((0, 0, {
                'display_type': 'line_section',
                'name': _("Inspection Charges"),
                'sequence': sequence_number,
            }))
            sequence_number += 1
            # Add inspection record details
            inspection_record = {
                'product_id': self.env.ref('tk_advance_vehicle_repair.vehicle_inspection').id,
                'name': _('Vehicle Inspection'),
                'price_unit': self.inspection_charge,
                'sequence': sequence_number,
            }
            order_line.append((0, 0, inspection_record))
            sequence_number += 1
        # Handle inspection and repair type
        if self.inspect_type == 'inspection_and_repair':
            if self.inspection_charge_type == 'paid' and not self.inspection_charge:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'message': _("Kindly include the inspection charge amount."),
                        'sticky': False,
                    }
                }
            # Add line section for Inspection Charges
            order_line.append((0, 0, {
                'display_type': 'line_section',
                'name': _("Inspection Charges"),
                'sequence': sequence_number,
            }))
            sequence_number += 1
            # Add inspection record details
            inspection_record = {
                'product_id': self.env.ref('tk_advance_vehicle_repair.vehicle_inspection').id,
                'name': _('Vehicle Inspection'),
                'price_unit': self.inspection_charge,
                'sequence': sequence_number,
            }
            order_line.append((0, 0, inspection_record))
            sequence_number += 1
            # Check if vehicle spare parts are added
            if not self.vehicle_spare_part_ids:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'message': _("Please add the necessary spare parts to the 'Required Vehicle Spare Parts' tab."),
                        'sticky': False,
                    }
                }
            # Add line section for Required Parts
            order_line.append((0, 0, {
                'display_type': 'line_section',
                'name': _("Required Parts"),
                'sequence': sequence_number,
            }))
            sequence_number += 1
            # Add each vehicle spare part
            for part in self.vehicle_spare_part_ids:
                order_line.append((0, 0, {
                    'product_id': part.product_id.id,
                    'product_uom_qty': part.qty,
                    'price_unit': part.unit_price,
                    'sequence': sequence_number,
                }))
                sequence_number += 1
            # Check if inspection repair services are added
            if not self.inspection_repair_team_ids:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'message': _("Please add the necessary service to the 'Required Vehicle Services' tab."),
                        'sticky': False,
                    }
                }
            # Add line section for Required Services
            order_line.append((0, 0, {
                'display_type': 'line_section',
                'name': _("Required Services"),
                'sequence': sequence_number,
            }))
            sequence_number += 1
            # Add each vehicle service
            for rec in self.inspection_repair_team_ids:
                order_line.append((0, 0, {
                    'product_id': rec.vehicle_service_id.product_id.id if rec.vehicle_service_id.product_id else self.env.ref(
                        'tk_advance_vehicle_repair.vehicle_service_charge').id,
                    'name': rec.vehicle_service_id.service_name,
                    'price_unit': rec.service_charge,
                    'sequence': sequence_number,
                }))
                sequence_number += 1
        # Create sale order data
        data = {
            'partner_id': self.customer_id.id,
            'date_order': fields.Datetime.now(),
            'order_line': order_line,
            'inspection_job_card_id': self.id,
        }
        # Create sale order
        sale_order_id = self.env['sale.order'].sudo().create(data)
        self.sale_order_id = sale_order_id.id
        # Send email based on inspection report type
        mail_template_ref = {
            'advanced_inspection': 'tk_advance_vehicle_repair.advanced_inspection_quotation_mail_template',
            'classic_inspection': 'tk_advance_vehicle_repair.classic_inspection_quotation_mail_template',
        }
        template_ref = mail_template_ref.get(self.inspection_report_type)
        if template_ref:
            mail_template = self.env.ref(template_ref)
            if mail_template:
                mail_template.send_mail(self.id, force_send=True)
        # Return action to open the created sale order
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sale Order'),
            'res_model': 'sale.order',
            'res_id': sale_order_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def update_inspection_repair_quotation(self):
        order_line = []
        sequence_number = 1
        # Check if inspection charge is provided
        if self.inspect_type in ['only_inspection', 'inspection_and_repair']:
            if self.inspection_charge_type == 'paid' and not self.inspection_charge:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'message': _("Kindly include the inspection charge amount."),
                        'sticky': False,
                    }
                }
            # Add line section for Inspection Charges
            order_line.append((0, 0, {
                'display_type': 'line_section',
                'name': _("Inspection Charges"),
                'sequence': sequence_number,
            }))
            sequence_number += 1
            # Add inspection record details
            inspection_record = {
                'product_id': self.env.ref('tk_advance_vehicle_repair.vehicle_inspection').id,
                'name': _('Vehicle Inspection'),
                'price_unit': self.inspection_charge,
                'sequence': sequence_number,
            }
            order_line.append((0, 0, inspection_record))
            sequence_number += 1
        # Handle inspection and repair type
        if self.inspect_type == 'inspection_and_repair':
            # Check if vehicle spare parts are added
            if not self.vehicle_spare_part_ids:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'message': _(
                            "Please add the necessary spare parts to the 'Required Vehicle Spare Parts' tab."),
                        'sticky': False,
                    }
                }
            # Add line section for Required Parts
            order_line.append((0, 0, {
                'display_type': 'line_section',
                'name': _("Required Parts"),
                'sequence': sequence_number,
            }))
            sequence_number += 1
            # Add each vehicle spare part
            for part in self.vehicle_spare_part_ids:
                order_line.append((0, 0, {
                    'product_id': part.product_id.id,
                    'product_uom_qty': part.qty,
                    'price_unit': part.unit_price,
                    'sequence': sequence_number,
                }))
                sequence_number += 1
            # Check if inspection repair services are added
            if not self.inspection_repair_team_ids:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'message': _("Please add the necessary service to the 'Required Vehicle Services' tab."),
                        'sticky': False,
                    }
                }
            # Add line section for Required Services
            order_line.append((0, 0, {
                'display_type': 'line_section',
                'name': _("Required Services"),
                'sequence': sequence_number,
            }))
            sequence_number += 1
            # Add each vehicle service
            for rec in self.inspection_repair_team_ids:
                order_line.append((0, 0, {
                    'product_id': rec.vehicle_service_id.product_id.id if rec.vehicle_service_id.product_id else self.env.ref(
                        'tk_advance_vehicle_repair.vehicle_service_charge').id,
                    'name': rec.vehicle_service_id.service_name,
                    'price_unit': rec.service_charge,
                    'sequence': sequence_number,
                }))
                sequence_number += 1
        # Update the existing sale order
        self.sale_order_id.sudo().write({
            'order_line': [(5, 0, 0)] + order_line  # Delete all existing lines and add the new ones
        })
        # Send email based on inspection report type
        mail_template_ref = {
            'advanced_inspection': 'tk_advance_vehicle_repair.advanced_inspection_quotation_mail_template',
            'classic_inspection': 'tk_advance_vehicle_repair.classic_inspection_quotation_mail_template',
        }
        template_ref = mail_template_ref.get(self.inspection_report_type)
        if template_ref:
            mail_template = self.env.ref(template_ref)
            if mail_template:
                mail_template.send_mail(self.id, force_send=True)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': _("Quotation is successfully updated"),
                'sticky': False,
            }
        }

    def unlink(self):
        """Unlink Method"""
        for rec in self:
            if rec.stages != 'locked':
                super(InspectionJobCard, rec).unlink()
            else:
                raise ValidationError(_('You cannot delete the locked order.'))

    # unused
    def _compute_team_task(self):
        """Task Count"""
        for rec in self:
            rec.team_task_count = self.env['project.task'].sudo().search_count(
                [('inspection_job_card_id', '=', rec.id)])
