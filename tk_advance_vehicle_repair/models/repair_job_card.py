# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class RepairImage(models.Model):
    """Repair Image"""
    _name = "repair.image"
    _description = __doc__
    _rec_name = 'name'

    avatar = fields.Binary(string="Avatar")
    name = fields.Char(string="Name", required=True, translate=True, size=36)
    repair_job_card_id = fields.Many2one('repair.job.card', ondelete='cascade')


class RepairJobCard(models.Model):
    """Repair Job Card"""
    _name = 'repair.job.card'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'sequence_number'

    sequence_number = fields.Char(string='Sequence No', readonly=True,
                                  default=lambda self: _('New'), copy=False)
    vehicle_brand_id = fields.Many2one('vehicle.brand', string="Brand")
    vehicle_model_id = fields.Many2one('vehicle.model', string="Model",
                                       domain="[('vehicle_brand_id', '=', vehicle_brand_id)]")
    vehicle_fuel_type_id = fields.Many2one('vehicle.fuel.type', string="Fuel Type")
    registration_no = fields.Char(string="Registration No", translate=True)
    vin_no = fields.Char(string="VIN No", translate=True)
    transmission_type = fields.Selection([
        ('manual', "Manual"),
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
    responsible_id = fields.Many2one('res.users', default=lambda self: self.env.user,
                                     string="Responsible")

    inspect_repair_date = fields.Date(string="Date", default=fields.Date.today)
    inspection_job_card_id = fields.Many2one('inspection.job.card', string="Inspection Job Card",
                                             compute='_compute_vehicle_inspection_job_card')
    vehicle_booking_id = fields.Many2one('vehicle.booking', compute="_compute_vehicle_booking",
                                         string="Booking No")

    vehicle_order_spare_part_ids = fields.One2many(comodel_name='vehicle.order.spare.part',
                                                   inverse_name='repair_job_card_id')
    vehicle_service_team_ids = fields.One2many(comodel_name='vehicle.service.team',
                                               inverse_name='repair_job_card_id')

    part_price = fields.Monetary(compute="_compute_spare_part_price",
                                 string="Part Price", store=True)
    service_charge = fields.Monetary(compute="_compute_service_charge",
                                     string="Service Charges", store=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  related="company_id.currency_id")
    sub_total = fields.Monetary(string="Sub Total", compute="_compute_sub_total")
    team_task_count = fields.Integer(compute="_compute_team_task_count", string="Task")
    repair_sale_order_id = fields.Many2one('sale.order', string=" Sale Order")
    repair_order_state = fields.Selection(related='repair_sale_order_id.state')
    repair_amount = fields.Monetary(related='repair_sale_order_id.amount_total',
                                    string=" Total Amount")
    repair_sale_invoiced = fields.Monetary()
    check_list_template_id = fields.Many2one('checklist.template',
                                             string="Checklist Template")
    repair_checklist_ids = fields.One2many(comodel_name='repair.checklist',
                                           inverse_name='repair_job_card_id',
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
    reject_reasons = fields.Text(string="Reject Reasons")
    date = fields.Date(string=" Date")
    signature = fields.Binary(string="Authorized Signature")
    is_scratch_report = fields.Boolean(string="Custom Scratch Report")
    scratch_report_id = fields.Many2one('scratch.report', string="Scratch Report")
    repair_image_ids = fields.One2many(comodel_name='repair.image',
                                       inverse_name='repair_job_card_id')
    is_skip_quotation = fields.Boolean(string="Skip Quotation")
    stages = fields.Selection(
        [('draft', "New"), ('assign_to_technician', "Assign to Technician"),
         ('in_diagnosis', "In Diagnosis"), ('supervisor_inspection', "In Supervisor Inspection"),
         ('reject', "Reject"), ('complete', "Complete"),
         ('hold', "Hold"), ('cancel', "Cancel"),
         ('locked', "Locked")], default='draft', string="Stages",
        group_expand='_expand_groups', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sequence_number', _('New')) == _('New'):
                vals['sequence_number'] = self.env['ir.sequence'].next_by_code('repair.job.card') or _('New')
        res = super(RepairJobCard, self).create(vals_list)
        return res

    def write(self, vals_list):
        rec = super(RepairJobCard, self).write(vals_list)
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
        return ['draft', 'assign_to_technician', 'in_diagnosis', 'supervisor_inspection', 'reject', 'complete', 'hold',
                'locked', 'cancel']

    def _repair_notification(self, message):
        """Repair Notification"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'warning',
                'message': message,
                'sticky': False,
            }
        }

    def draft_to_assign_to_technician(self):
        """Required Services Check"""
        if not self.vehicle_service_team_ids:
            return self._repair_notification("Please choose the required service")
        for record in self.vehicle_service_team_ids:
            if not record.service_team_id or not record.vehicle_service_team_members_ids:
                return self._repair_notification(
                    "In service tab: Please assign a team and team members each listed service")
        self.stages = 'assign_to_technician'

    def assign_to_technician_to_in_diagnosis(self):
        """Check Task Created"""
        if self.vehicle_service_team_ids:
            task_created = all(rec.team_task_id for rec in self.vehicle_service_team_ids)
            if not task_created:
                return self._repair_notification("First, create tasks for all listed services.")
        self.stages = 'in_diagnosis'

    def in_diagnosis_to_supervisor_inspection(self):
        """Team Task Check"""
        team_work_complete = all(rec.work_is_done for rec in self.vehicle_service_team_ids)
        if not team_work_complete:
            return self._repair_notification("Please complete all team tasks")
        self.stages = 'supervisor_inspection'

    def supervisor_inspection_to_reject(self):
        """Reject Stage"""
        self.stages = 'reject'

    def reject_to_complete(self):
        """Checklist Template Check"""
        if any(not rec.is_check and not rec.display_type for rec in self.repair_checklist_ids):
            return self._repair_notification("Please complete the checklist template")
        self.stages = 'complete'
        mail_template = self.env.ref('tk_advance_vehicle_repair.repair_job_card_mail_template')
        if mail_template:
            mail_template.send_mail(self.id, force_send=True)

    def complete_to_hold(self):
        """Hold Stage"""
        self.stages = 'hold'

    def complete_to_locked(self):
        """Locked Stage"""
        self.stages = 'locked'

    def hold_to_cancel(self):
        """Cancel Stage"""
        self.stages = 'cancel'

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
        """Repair Checklist Template"""
        for rec in self:
            rec.repair_checklist_ids = [(5, 0, 0)]  # Clear existing lines
            # Prepare new checklist items
            lines = []
            for data in rec.check_list_template_id.checklist_template_item_ids.sorted('sequence'):
                lines.append((0, 0, {
                    'name': data.name,
                    'sequence': data.sequence,
                    'display_type': data.display_type,
                }))
            # Update the checklist items
            rec.repair_checklist_ids = lines

    @api.depends('vehicle_service_team_ids.service_charge')
    def _compute_service_charge(self):
        """Total Service Charges"""
        for rec in self:
            rec.service_charge = sum(service.service_charge for service in rec.vehicle_service_team_ids)

    @api.depends('vehicle_order_spare_part_ids.unit_price', 'vehicle_order_spare_part_ids.qty')
    def _compute_spare_part_price(self):
        """Total Spare Parts Price"""
        for rec in self:
            rec.part_price = sum(part.unit_price * part.qty for part in rec.vehicle_order_spare_part_ids)

    @api.depends('sub_total', 'service_charge', 'part_price')
    def _compute_sub_total(self):
        """Total Service and Spare Parts Price"""
        for rec in self:
            rec.sub_total = rec.service_charge + rec.part_price

    def _compute_vehicle_booking(self):
        """Vehicle Booking Details"""
        for rec in self:
            vehicle_booking_id = self.env['vehicle.booking'].search([('repair_job_card_id', '=', rec.id)], limit=1)
            rec.vehicle_booking_id = vehicle_booking_id.id

    def action_create_vehicle_registration(self):
        """Register Vehicle In Customer"""
        if not self.vehicle_brand_id or not self.vehicle_model_id:
            return self._repair_notification(
                "Please provide the vehicle name and model along with any other relevant vehicle details.")
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

    def _compute_team_task_count(self):
        """Task Count"""
        for rec in self:
            rec.team_task_count = self.env['project.task'].search_count([('repair_job_card_id', '=', rec.id)])

    def view_team_tasks(self):
        """View Team Task"""
        team_task_ids = self.inspection_job_card_id.inspection_repair_team_ids.mapped('team_task_id').ids
        domain = ['|', ('repair_job_card_id', '=', self.id), ('id', 'in', team_task_ids)]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tasks'),
            'view_mode': 'tree,form,kanban,calendar,pivot,graph,activity',
            'res_model': 'project.task',
            'domain': domain,
            'context': {
                'create': False,
            }
        }

    def _compute_vehicle_inspection_job_card(self):
        """Inspection Job Card ID"""
        inspection_job_card_id = self.env['inspection.job.card'].search(
            [('repair_job_card_id', '=', self.id)], limit=1)
        self.inspection_job_card_id = inspection_job_card_id.id

    def _repair_quote_notification(self, message):
        """Repair Quote Notification"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'warning',
                'message': message,
                'sticky': False,
            }
        }

    def action_repair_sale_order(self):
        order_line = []
        sequence_number = 1
        # Check if there are Parts
        if not self.vehicle_order_spare_part_ids:
            return self._repair_quote_notification(
                "Please add the necessary spare parts to the 'Vehicle Spare Parts' tab."
            )
        # Check if there are Services
        if not self.vehicle_service_team_ids:
            return self._repair_quote_notification(
                "Please add the necessary services."
            )
        # Add Spare Parts to the Order Line
        order_line.append((0, 0, {
            'display_type': 'line_section',
            'name': "Required Parts",
            'sequence': sequence_number,
        }))
        sequence_number += 1
        for part in self.vehicle_order_spare_part_ids:
            order_line.append((0, 0, {
                'product_id': part.product_id.id,
                'product_uom_qty': part.qty,
                'price_unit': part.unit_price,
                'sequence': sequence_number,
            }))
            sequence_number += 1
        # Add Services to the Order Line
        order_line.append((0, 0, {
            'display_type': 'line_section',
            'name': "Required Services",
            'sequence': sequence_number,
        }))
        sequence_number += 1
        for rec in self.vehicle_service_team_ids:
            order_line.append((0, 0, {
                'product_id': rec.vehicle_service_id.product_id.id if rec.vehicle_service_id.product_id else self.env.ref(
                    'tk_advance_vehicle_repair.vehicle_service_charge').id,
                'name': rec.vehicle_service_id.service_name,
                'price_unit': rec.service_charge,
                'sequence': sequence_number,
            }))
            sequence_number += 1
        # Prepare the Sale Order Data
        data = {
            'partner_id': self.customer_id.id,
            'date_order': fields.Datetime.now(),
            'order_line': order_line,
            'repair_job_card_id': self.id,
        }
        # Ensure there are Order Lines
        if not order_line:
            return self._repair_quote_notification(
                "The total value of the sale order cannot be zero. Please ensure all required parts and services are correctly entered."
            )
        # Create the Sale Order
        repair_sale_order_id = self.env['sale.order'].sudo().create(data)
        # Update the Repair Job Card with Sale Order details
        self.write({
            'repair_sale_order_id': repair_sale_order_id.id,
            'repair_sale_invoiced': repair_sale_order_id.amount_total,
        })
        # Send Notification Email
        mail_template = self.env.ref('tk_advance_vehicle_repair.vehicle_repair_quotation_mail_template')
        if mail_template:
            mail_template.send_mail(self.id, force_send=True)
        # Return the Created Sale Order
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sale Order'),
            'res_model': 'sale.order',
            'res_id': repair_sale_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def update_repair_quotation(self):
        # Delete old sale order lines
        if self.repair_sale_order_id:
            self.repair_sale_order_id.order_line.sudo().unlink()
        # Prepare new order lines
        order_line = []
        sequence_number = 1
        # Add Spare Parts Section
        order_line.append((0, 0, {
            'display_type': 'line_section',
            'name': "Required Parts",
            'sequence': sequence_number,
        }))
        sequence_number += 1
        for part in self.vehicle_order_spare_part_ids:
            order_line.append((0, 0, {
                'product_id': part.product_id.id,
                'product_uom_qty': part.qty,
                'price_unit': part.unit_price,
                'sequence': sequence_number,
            }))
            sequence_number += 1
        # Add Services Section
        order_line.append((0, 0, {
            'display_type': 'line_section',
            'name': "Required Services",
            'sequence': sequence_number,
        }))
        sequence_number += 1
        for rec in self.vehicle_service_team_ids:
            order_line.append((0, 0, {
                'product_id': rec.vehicle_service_id.product_id.id if rec.vehicle_service_id.product_id else self.env.ref(
                    'tk_advance_vehicle_repair.vehicle_service_charge').id,
                'name': rec.vehicle_service_id.service_name,
                'price_unit': rec.service_charge,
                'sequence': sequence_number,
            }))
            sequence_number += 1
        # Update sale order with new order lines
        if self.repair_sale_order_id:
            self.repair_sale_order_id.write({
                'order_line': order_line,
            })
        # Send mail notification
        mail_template = self.env.ref('tk_advance_vehicle_repair.vehicle_repair_quotation_mail_template')
        if mail_template:
            mail_template.send_mail(self.id, force_send=True)
        # Return success notification
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
                super(RepairJobCard, rec).unlink()
            else:
                raise ValidationError(_('You cannot delete the locked order.'))
