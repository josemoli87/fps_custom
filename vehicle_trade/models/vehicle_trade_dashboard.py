# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class VehicleTradeDashboard(models.Model):
    """Vehicle Trade Dashboard"""
    _name = "vehicle.trade.dashboard"
    _description = __doc__

    @api.model
    def get_vehicle_trade_dashboard(self):
        total_vehicle = self.env['vehicle.information'].sudo().search_count([])
        available_vehicle = self.env['vehicle.information'].sudo().search_count([('status', '=', 'available')])
        in_discussion_vehicle = self.env['vehicle.information'].sudo().search_count([('status', '=', 'in_discussion')])
        sold_vehicle = self.env['vehicle.information'].sudo().search_count([('status', '=', 'sold')])

        vehicle_status = [['Total', 'Available', 'In Discussion', 'Sold'],
                          [total_vehicle, available_vehicle, in_discussion_vehicle, sold_vehicle]]

        vehicle_customers = self.env['res.partner'].sudo().search_count([])
        vehicle_vendors = self.env['res.partner'].sudo().search_count([('is_vendor', '=', True)])

        data = {
            'total_vehicle': total_vehicle,
            'available_vehicle': available_vehicle,
            'in_discussion_vehicle': in_discussion_vehicle,
            'sold_vehicle': sold_vehicle,
            'vehicle_status': vehicle_status,
            'vehicle_customers': vehicle_customers,
            'vehicle_vendors': vehicle_vendors,
            'vendor_bill_month': self.get_bill_month(),
            'invoice_status': self.get_invoice_due_paid_status(),
        }
        return data

    def get_bill_month(self):
        year = fields.date.today().year
        data_dict = {'January': 0,
                     'February': 0,
                     'March': 0,
                     'April': 0,
                     'May': 0,
                     'June': 0,
                     'July': 0,
                     'August': 0,
                     'September': 0,
                     'October': 0,
                     'November': 0,
                     'December': 0,
                     }
        invoice_id = self.env['account.move'].search(
            [('vehicle_information_id', '!=', False), ('move_type', '=', 'in_invoice')])
        for data in invoice_id:
            if data.invoice_date.year == year:
                if data.vehicle_information_id.status == 'sold':
                    data_dict[data.invoice_date.strftime("%B")] = data_dict[data.invoice_date.strftime(
                        "%B")] + data.amount_total
        return [list(data_dict.keys()), list(data_dict.values())]

    def get_invoice_due_paid_status(self):
        vehicle_data = {'Amount Paid': 0.0, 'Amount Due': 0.0}
        invoice_ids = self.env['account.move'].sudo().search(
            [('vehicle_information_id', '!=', False), ('move_type', '=', 'out_invoice')])
        for rec in invoice_ids:
            if rec.payment_state == 'paid':
                vehicle_data['Amount Paid'] += rec.amount_total
            else:
                vehicle_data['Amount Due'] += rec.amount_total
        return [list(vehicle_data.keys()), list(vehicle_data.values())]
