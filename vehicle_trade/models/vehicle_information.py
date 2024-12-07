# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class VehicleFuelType(models.Model):
    """Vehicle Fuel Type"""
    _name = 'vehicle.fuel.type'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True)


class VehicleImage(models.Model):
    """Vehicle Image"""
    _name = 'vehicle.image'
    _description = __doc__

    vehicle_image = fields.Binary(string="Vehicle Image")
    vehicle_information_id = fields.Many2one('vehicle.information')


class VehicleInformation(models.Model):
    """Sold Vehicle Information"""
    _name = 'vehicle.information'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'vt_number'

    vt_number = fields.Char(string='Vehicle Trade', required=True, readonly=True, default=lambda self: _('New'),
                            copy=False)
    avatar = fields.Binary(string="Avatar")
    vehicle_brand_id = fields.Many2one('vehicle.brand', string="Brand", required=True)
    vehicle_model_id = fields.Many2one('vehicle.model', string="Model",
                                       domain="[('vehicle_brand_id', '=', vehicle_brand_id)]", required=True)
    vehicle_fuel_type_id = fields.Many2one('vehicle.fuel.type', string="Fuel Type")
    mfg_year = fields.Char(string="MFG Year")
    license_plate = fields.Char(string="License Plate")
    odometer_reading = fields.Integer(string="Odometer Reading")

    customer_id = fields.Many2one('res.partner', string="Customer", required=True)
    customer_phone = fields.Char()
    customer_email = fields.Char()
    vendor_id = fields.Many2one('res.partner', string="Vendor", domain=[('is_vendor', '=', True)], required=True)
    vendor_phone = fields.Char()
    vendor_email = fields.Char()
    responsible_id = fields.Many2one('res.users', default=lambda self: self.env.user, string="Responsible",
                                     required=True)

    inspection_template_id = fields.Many2one('inspection.template', string="Inspection Template")
    expert_inspection_template_ids = fields.One2many('expert.inspection.template', 'vehicle_information_id')

    vehicle_condition_ids = fields.One2many('vehicle.condition', 'vehicle_information_id')
    previous_service_history_ids = fields.One2many('previous.service.history', 'vehicle_information_id')
    vehicle_image_ids = fields.One2many("vehicle.image", "vehicle_information_id", string="Image")
    vehicle_specification_ids = fields.One2many("vehicle.specification.used", "vehicle_information_id")
    vehicle_insurance_ids = fields.One2many("vehicle.insurance", "vehicle_information_id")

    vehicle_document_id = fields.Many2one('vehicle.document', string="Document")
    document_count = fields.Integer(compute='_compute_document_count')

    condition = fields.Selection(
        [('showroom_condition', "Showroom Condition"), ('very_gently_used', "Very Gently Used (Default)"),
         ('wear_tear', "Normal Wear and Tear"), ('needs_some_attention', "Needs Some Attention")], string="Condition")
    sold_by = fields.Selection([('dealer', "Dealer"), ('private', "Private")], string="Sold By")
    sold_to = fields.Selection([('dealer', "Dealer"), ('private', "Private"), ('auction', "Auction")], string="Sold To")
    current_market_value = fields.Monetary(string="Current Market Value")

    seller_vehicle_price = fields.Monetary(string="Vehicle Selling Price")
    buyer_vehicle_price = fields.Monetary(string="Buyer Price")
    down_payment = fields.Monetary(string="Down Payment")
    due_amount = fields.Monetary(string="Total Due Amount", compute="_total_value_of_vehicle")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    buyer_invoice = fields.Monetary(related="buyer_invoice_id.amount_total", string="Total")
    seller_invoice = fields.Monetary(related="seller_invoice_id.amount_total", string=" Total")

    profit = fields.Monetary(string="Profit & Loss", compute="_vehicle_profit")

    total_vehicle_price = fields.Monetary(string="Total Vehicle Price")

    annual_running = fields.Char(string="Annual Running")
    highway = fields.Float(string="Highway (%)")
    city = fields.Float(string="City (%)")

    reported_stolen = fields.Boolean(string="Reported Stolen")
    stolen_description = fields.Text()
    reported_accident = fields.Boolean(string="Reported Accidents")
    accident_description = fields.Text()
    heavily_use_history = fields.Boolean(string="Heavily Use")
    heavily_use_description = fields.Text()
    registered_in_other_region = fields.Boolean(string="Registered in Other Region")
    region_name = fields.Char(string="Region Name")

    buyer_invoice_id = fields.Many2one('account.move')
    seller_invoice_id = fields.Many2one('account.move', string=' Sale Invoice')
    down_payment_id = fields.Many2one('account.move', string='Down Payment Invoice')
    seller_tax_ids = fields.Many2many('account.tax', string='Taxes')
    status = fields.Selection([('draft', "New"), ('available', "Available"), ('in_discussion', "In Discussion"),
                               ('sold', "Sold")], default="draft", string="Vehicle Status",
                              group_expand='_expand_groups')

    @api.model
    def _expand_groups(self, states, domain, order):
        return ['draft', 'available', 'in_discussion', 'sold']

    def draft_to_available(self):
        self.status = 'available'

    def available_to_in_discussion(self):
        self.status = 'in_discussion'

    def in_discussion_to_sold(self):
        self.status = 'sold'

    @api.onchange('customer_id')
    def customer_details(self):
        for rec in self:
            if rec.customer_id:
                rec.customer_phone = rec.customer_id.phone
                rec.customer_email = rec.customer_id.email

    @api.onchange('vehicle_condition_ids')
    def _vehicle_part_condition(self):
        for record in self:
            if record.vehicle_condition_ids:
                for rec in record.vehicle_condition_ids:
                    if rec.condition > 100:
                        raise ValidationError(_("Maximum vehicle part condition: 100 %"))

    @api.onchange('vendor_id')
    def vendor_details(self):
        for rec in self:
            if rec.vendor_id:
                rec.vendor_phone = rec.vendor_id.phone
                rec.vendor_email = rec.vendor_id.email

    @api.onchange('inspection_template_id')
    def get_solar_product_item_items(self):
        for rec in self:
            if rec.inspection_template_id:
                vehicle_items = []
                for item in rec.inspection_template_id.inspection_template_item_ids:
                    vehicle_items.append((0, 0, {'name': item.title}))
                rec.expert_inspection_template_ids = [(5, 0, 0)]
                rec.expert_inspection_template_ids = vehicle_items

    def _compute_document_count(self):
        for rec in self:
            document_count = self.env['vehicle.document'].search_count([('vehicle_information_id', '=', rec.id)])
            rec.document_count = document_count
        return True

    def view_vehicle_documents(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Documents'),
            'res_model': 'vehicle.document',
            'domain': [('vehicle_information_id', '=', self.id)],
            'context': {'default_vehicle_information_id': self.id},
            'view_mode': 'tree',
            'target': 'current',
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('vt_number', _('New')) == _('New'):
                vals['vt_number'] = self.env['ir.sequence'].next_by_code('vehicle.trade.number') or _('New')
        res = super(VehicleInformation, self).create(vals_list)
        return res

    @api.constrains('buyer_vehicle_price', 'down_payment')
    def _down_payment_values(self):
        for record in self:
            if record.down_payment:
                if record.down_payment > record.buyer_vehicle_price:
                    raise ValidationError(_("Down payment value cannot exceed vehicle price"))

    @api.depends('buyer_vehicle_price', 'down_payment')
    def _total_value_of_vehicle(self):
        for rec in self:
            rec.due_amount = rec.buyer_vehicle_price - rec.down_payment

    @api.depends('buyer_vehicle_price', 'seller_vehicle_price')
    def _vehicle_profit(self):
        for rec in self:
            rec.profit = rec.buyer_vehicle_price - rec.seller_vehicle_price

    def action_vendor_bill(self):
        for rec in self:
            if not rec.seller_vehicle_price:
                message = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'message': _("Invalid price. Please enter a non-zero value for the vehicle selling price."),
                        'sticky': False,
                    }
                }
                return message
            vehicle_brand = " ".join(brand.vehicle_brand_id.name for brand in rec)
            vehicle_model = " ".join(model.vehicle_model_id.name for model in rec)
            tax_ids = rec.seller_tax_ids.ids
            vehicle_sale_record = {
                'product_id': self.env.ref('vehicle_trade.vehicle_product_1').id,
                'name': f"{vehicle_brand} - {vehicle_model}",
                'quantity': 1,
                'price_unit': rec.seller_vehicle_price,
                'tax_ids': [(6, 0, tax_ids)],
            }
            invoice_lines = [(0, 0, vehicle_sale_record)]
            invoice_data = {
                'partner_id': rec.vendor_id.id,
                'move_type': 'in_invoice',
                'invoice_date': fields.Datetime.now(),
                'invoice_line_ids': invoice_lines,
                'vehicle_information_id': rec.id
            }
            seller_invoice_id = self.env['account.move'].sudo().create(invoice_data)
            rec.seller_invoice_id = seller_invoice_id.id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Vendor Bill',
                'res_model': 'account.move',
                'res_id': seller_invoice_id.id,
                'view_mode': 'form',
                'target': 'current'
            }

    def action_down_payment_invoice(self):
        for rec in self:
            if not rec.down_payment or not rec.buyer_vehicle_price:
                message = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'message': _("Please enter both down payment and buyer price for the vehicle."),
                        'sticky': False,
                    }
                }
                return message

            vehicle_brand = " ".join(brand.vehicle_brand_id.name for brand in rec)
            vehicle_model = " ".join(model.vehicle_model_id.name for model in rec)

            vehicle_down_payment = {
                'product_id': self.env.ref('vehicle_trade.vehicle_down_payment_product').id,
                'name': f"{vehicle_brand}-{vehicle_model}",
                'quantity': 1,
                'price_unit': rec.down_payment,
            }
            invoice_lines = [(0, 0, vehicle_down_payment)]
            data = {
                'partner_id': rec.customer_id.id,
                'move_type': 'out_invoice',
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': invoice_lines,
                'vehicle_information_id': rec.id
            }
            down_payment_id = self.env['account.move'].sudo().create(data)
            rec.down_payment_id = down_payment_id.id
            return {
                'type': 'ir.actions.act_window',
                'name': _('Down Payment'),
                'res_model': 'account.move',
                'res_id': down_payment_id.id,
                'view_mode': 'form',
                'target': 'current'
            }

    def action_buyer_invoice(self):
        for rec in self:
            if not rec.due_amount:
                message = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'message': _(
                            "The buyer's vehicle price cannot be zero. Please provide a valid price before proceeding."),
                        'sticky': False,
                    }
                }
                return message
            vehicle_brand = " ".join(brand.vehicle_brand_id.name for brand in rec)
            vehicle_model = " ".join(model.vehicle_model_id.name for model in rec)

            tax_ids = rec.seller_tax_ids.ids if rec.seller_tax_ids else []
            vehicle_record = {
                'product_id': self.env.ref('vehicle_trade.vehicle_product_1').id,
                'name': f"{vehicle_brand}-{vehicle_model}",
                'quantity': 1,
                'price_unit': rec.due_amount,
                'tax_ids': [(6, 0, tax_ids)],
            }
            invoice_lines = [(0, 0, vehicle_record)]
            data = {
                'partner_id': rec.customer_id.id,
                'move_type': 'out_invoice',
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': invoice_lines,
                'vehicle_information_id': rec.id
            }
            buyer_invoice_id = self.env['account.move'].sudo().create(data)
            rec.buyer_invoice_id = buyer_invoice_id.id
            rec.status = 'sold'
            mail_template = self.env.ref('vehicle_trade.vehicle_trade_completed_mail_template')
            if mail_template:
                mail_template.send_mail(rec.id, force_send=True)
            return {
                'type': 'ir.actions.act_window',
                'name': 'Customer Invoice',
                'res_model': 'account.move',
                'res_id': buyer_invoice_id.id,
                'view_mode': 'form',
                'target': 'current'
            }
