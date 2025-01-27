# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class BookingAppointment(models.Model):
    """Booking Appointment"""
    _name = 'booking.appointment'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name")
    appointment_day = fields.Selection([('monday', "Monday"), ('tuesday', "Tuesday"), ('wednesday', "Wednesday"),
                                        ('thursday', "Thursday"), ('friday', "Friday"), ('saturday', "Saturday"),
                                        ('sunday', "Sunday")], string="Appointment Day")
    booking_appointment_slot_ids = fields.One2many(comodel_name='booking.appointment.slot',
                                                   inverse_name='booking_appointment_id')


class BookingAppointmentSlot(models.Model):
    """Booking Appointment Slot"""
    _name = 'booking.appointment.slot'
    _description = __doc__
    _rec_name = 'title'

    title = fields.Char(string="Title", required=True)
    from_time = fields.Float(string="Starting Time")
    to_time = fields.Float(string="Closing Time")
    booking_appointment_id = fields.Many2one('booking.appointment', string="Booking Appointment")
