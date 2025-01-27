# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import http, _
from odoo.http import request
from datetime import datetime
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.http_routing.models.ir_http import slug


def validate_mandatory_fields(mandate_fields, kw):
    error, data = None, {}
    for key, value in mandate_fields.items():
        if not kw.get(key):
            error = "Mandatory fields " + value + " Missing"
            break
        else:
            data[key] = kw.get(key)
    return error, data


def validate_optional_fields(opt_fields, kw):
    data = {}
    for fld in opt_fields:
        if kw.get(fld):
            data[fld] = kw.get(fld)
    return data


def _get_initial_values():
    customer_state = request.env['res.country.state'].sudo().search([])
    customer_country = request.env['res.country'].sudo().search([])
    vehicle_brands = request.env['vehicle.brand'].sudo().search([])
    vehicle_models = request.env['vehicle.model'].sudo().search([])
    vehicle_fuel_types = request.env['vehicle.fuel.type'].sudo().search([])
    register_vehicles = request.env['register.vehicle'].sudo().search(
        [('customer_id', '=', request.env.user.partner_id.id)])
    booking_appointment = request.env['booking.appointment'].sudo().search([])
    website_slot_booking = request.env['ir.config_parameter'].sudo().get_param(
        'tk_advance_vehicle_repair.website_slot_booking')
    return {
        'customer_state': customer_state,
        'customer_country': customer_country,
        'vehicle_brands': vehicle_brands,
        'vehicle_models': vehicle_models,
        'vehicle_fuel_types': vehicle_fuel_types,
        'register_vehicles': register_vehicles,
        'booking_appointment': booking_appointment,
        'website_slot_booking': website_slot_booking,
    }


class VehicleBookingWebsite(http.Controller):
    @http.route('/get_country_wise_state', type='json', auth='public')
    def get_country_state(self, country_id):
        """get state from country"""
        country_wise_state = {}
        if not country_id:
            return
        customer_state = request.env['res.country.state'].sudo().search([('country_id', '=', int(country_id))])
        for data in customer_state:
            country_wise_state[data.id] = data.name
        return country_wise_state

    @http.route('/get_vehicle_model', type='json', auth='public')
    def get_vehicle_brand_wise_models(self, vehicle_brand_id):
        vehicle_model = {}
        if not vehicle_brand_id:
            return
        vehicle_models = request.env['vehicle.model'].sudo().search([('vehicle_brand_id', '=', int(vehicle_brand_id))])
        for data in vehicle_models:
            vehicle_model[data.id] = data.name
        return vehicle_model

    @http.route('/get_booking_day', type='json', auth='public')
    def get_booking_day(self, **kw):
        selected_date_str = kw.get('selected_date')
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d")
        day = selected_date.strftime("%A").lower()
        booking = request.env['booking.appointment'].sudo()
        day_appointment = booking.search([('appointment_day', '=', day)])

        booking_appointment = request.env['vehicle.booking'].sudo().search(
            [('booking_date', '=', selected_date_str)]).mapped('booking_appointment_slot_id').mapped('id')
        total_slots = day_appointment.mapped('booking_appointment_slot_ids').mapped('id')
        result = [data for data in total_slots if data not in booking_appointment]

        slot_details = request.env['booking.appointment.slot'].sudo().browse(result)
        from_time, to_time, slot_id = [], [], []
        for slots in slot_details:
            from_time.append(slots.from_time)
            to_time.append(slots.to_time)
            slot_id.append(slots.id)

        return {
            'appointment': booking_appointment,
            'slot_id': slot_id,
            'from_time': from_time,
            'to_time': to_time,
        }

    @http.route('/get_registered_vehicles', type='json', auth='public')
    def get_vehicle_details(self, register_vehicle_id):
        if not register_vehicle_id:
            return False
        vehicle = request.env['register.vehicle'].sudo().browse(int(register_vehicle_id))
        if not vehicle:
            return False
        details = {
            'vehicle_brand_id': vehicle.vehicle_brand_id.id,
            'vehicle_model_id': vehicle.vehicle_model_id.id,
            'vehicle_fuel_type_id': vehicle.vehicle_fuel_type_id.id,
            'registration_no': vehicle.registration_no,
            'transmission_type': vehicle.transmission_type,
            'vin_no': vehicle.vin_no,
        }
        return details

    @http.route('/vehicle/booking', type='http', auth='user', website=True)
    def get_vehicle_booking(self, **kw):
        values = _get_initial_values()
        return request.render('tk_advance_vehicle_repair.vehicle_booking_form', values)

    @http.route('/create/vehicle-booking', type='http', auth='user', website=True)
    def create_web_vehicle_booking(self, **kw):
        values = _get_initial_values()
        mandatory_fields = {'vehicle_brand_id': 'Vehicle Brand', 'vehicle_model_id': 'Vehicle Model',
                            'registration_no': 'Registration No', 'vehicle_fuel_type_id': 'Fuel Type'}
        optional_fields = ['transmission_type', 'vin_no', 'vehicle_from', 'booking_date', 'booking_type', 'phone',
                           'register_vehicle_id', 'customer_id', 'customer_observation', 'phone', 'email', 'street',
                           'street2', 'city', 'zip', 'state_id', 'country_id', 'booking_appointment_slot_id']

        error, booking_data = validate_mandatory_fields(mandatory_fields, kw)
        if error:
            values['error'] = error
            kw.update(values)
            return request.render('tk_advance_vehicle_repair.vehicle_booking_form', kw)
        opt_data = validate_optional_fields(optional_fields, kw)
        booking_data.update(opt_data)

        booking_data.update({
            'customer_id': request.env.user.partner_id.id,
            'phone': request.env.user.partner_id.phone,
            'email': request.env.user.partner_id.email,
            'booking_source': 'website',
        })

        booking_details = request.env['vehicle.booking'].sudo().create(booking_data)
        return request.render('tk_advance_vehicle_repair.repair_order_created', {'booking_details': booking_details})

    @http.route('/booking/vehicle-booking-details', website=True, auth="public")
    def get_repair_request(self, **kw):
        booking_requests = request.env['vehicle.booking'].sudo().search([
            ('customer_id', '=', request.env.user.partner_id.id), ('booking_source', '=', 'website')
        ])
        return request.render('tk_advance_vehicle_repair.vehicle_booking_view', {
            'booking_requests': booking_requests,
            'page_name': 'booking_request_tree'
        })

    @http.route(['/booking/request-information/<model("vehicle.booking"):bookings>'], type='http', auth="user",
                website=True)
    def booking_request_information_detail(self, bookings, **kw):
        # Ensure the current user is the customer who made the booking
        if bookings.customer_id.id != request.env.user.partner_id.id:
            return request.redirect('/')
        vehicle_book = request.env['vehicle.booking'].sudo()
        # Find all booking records related to the current user
        booking_ids = vehicle_book.search([
            ('customer_id', '=', request.env.user.partner_id.id)
        ]).ids
        booking_index = booking_ids.index(bookings.id) if bookings.id in booking_ids else -1
        prev_url = next_url = None
        if booking_index > 0:
            prev_record = vehicle_book.browse(booking_ids[booking_index - 1])
            prev_url = f"/booking/request-information/{slug(prev_record)}"
        if booking_index < len(booking_ids) - 1:
            next_record = vehicle_book.browse(booking_ids[booking_index + 1])
            next_url = f"/booking/request-information/{slug(next_record)}"
        return request.render('tk_advance_vehicle_repair.vehicle_booking_details', {
            'vehicle_bookings': bookings,
            'page_name': 'booking_request_form',
            'prev_record': prev_url,
            'next_record': next_url,
        })


class VehicleBookingPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        count = request.env['vehicle.booking'].sudo().search_count(
            [('customer_id', '=', request.env.user.partner_id.id)])
        values['count'] = count
        return values
