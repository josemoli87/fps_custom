# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class AdvanceVehicleRepairDashboard(models.Model):
    """Advance Vehicle Repair Dashboard"""
    _name = "advance.vehicle.repair.dashboard"
    _description = __doc__

    @api.model
    def get_advance_vehicle_repair_dashboard(self):
        """Advance Vehicle Dashboard Static"""
        vehicle_bookings = self.env['vehicle.booking'].sudo()
        inspection_job_cards = self.env['inspection.job.card'].sudo()
        repair_job_cards = self.env['repair.job.card'].sudo()

        # Booking
        total_vehicle_booking = vehicle_bookings.search_count([])
        vehicle_inspection = vehicle_bookings.search_count([('booking_stages', '=', 'vehicle_inspection')])
        vehicle_repair = vehicle_bookings.search_count([('booking_stages', '=', 'vehicle_repair')])
        vehicle_inspection_repair = vehicle_bookings.search_count(
            [('booking_stages', '=', 'vehicle_inspection_repair')])
        booking_cancel = vehicle_bookings.search_count([('booking_stages', '=', 'cancel')])
        booking_source_direct = vehicle_bookings.search_count([('booking_source', '=', 'direct')])
        booking_source_website = vehicle_bookings.search_count([('booking_source', '=', 'website')])
        booking_details = [['Vehicle Inspection', 'Vehicle Repair', 'Vehicle Inspection and Repair'],
                           [vehicle_inspection, vehicle_repair, vehicle_inspection_repair]]
        booking_source = [['Direct', 'Website'], [booking_source_direct, booking_source_website]]

        # Inspection Job Cards
        total_inspection_job_card = inspection_job_cards.search_count([])
        inspection_draft = inspection_job_cards.search_count([('stages', '=', 'a_draft')])
        inspection_in_progress = inspection_job_cards.search_count([('stages', '=', 'b_in_progress')])
        inspection_complete = inspection_job_cards.search_count([('stages', '=', 'c_complete')])
        inspection_cancel = inspection_job_cards.search_count([('stages', '=', 'd_cancel')])
        inspection_job_card_full_inspection = inspection_job_cards.search_count(
            [('inspection_type', '=', 'full_inspection')])
        inspection_job_card_specific_inspection = inspection_job_cards.search_count(
            [('inspection_type', '=', 'specific_inspection')])
        inspection_job_card_details = [['Full Inspection', 'Specific Inspection'],
                                       [inspection_job_card_full_inspection, inspection_job_card_specific_inspection]]

        # Repair Job Cards
        repair_job_card = repair_job_cards.search_count([])
        assign_to_technician = repair_job_cards.search_count([('stages', '=', 'assign_to_technician')])
        in_diagnosis = repair_job_cards.search_count([('stages', '=', 'in_diagnosis')])
        supervisor_inspection = repair_job_cards.search_count([('stages', '=', 'supervisor_inspection')])
        hold = repair_job_cards.search_count([('stages', '=', 'hold')])
        complete = repair_job_cards.search_count([('stages', '=', 'complete')])
        cancel = repair_job_cards.search_count([('stages', '=', 'cancel')])
        repair_job_card_details = [['Assign', 'In Diagnosis', 'In Inspection', 'Hold', 'Completed', 'Cancelled'],
                                   [assign_to_technician, in_diagnosis, supervisor_inspection, hold, complete, cancel]]

        service_teams = self.env['service.team'].sudo().search_count([])
        vehicle_customers = self.env['res.partner'].sudo().search_count([])

        data = {
            'total_vehicle_booking': total_vehicle_booking,
            'vehicle_inspection': vehicle_inspection,
            'vehicle_repair': vehicle_repair,
            'vehicle_inspection_repair': vehicle_inspection_repair,
            'booking_cancel': booking_cancel,
            'total_inspection_job_card': total_inspection_job_card,
            'inspection_in_progress': inspection_in_progress,
            'inspection_complete': inspection_complete,
            'inspection_cancel': inspection_cancel,
            'repair_job_card_details': repair_job_card_details,
            'booking_details': booking_details,
            'booking_source': booking_source,

            'inspection_draft': inspection_draft,
            'repair_job_card': repair_job_card,
            'service_teams': service_teams,
            'vehicle_customers': vehicle_customers,
            'booking_source_direct': booking_source_direct,
            'booking_source_website': booking_source_website,
            'inspection_job_card_details': inspection_job_card_details,
            'type_full_inspection': inspection_job_card_full_inspection,
            'type_specific_inspection': inspection_job_card_specific_inspection,
            'common_fuel_used_in_vehicle': self.get_most_common_fuels(),
        }
        return data

    def get_most_common_fuels(self):
        top_five_fuel = {}
        # Reading group data from vehicle.booking model
        for group in self.env['vehicle.booking'].read_group([],
                                                            ['vehicle_fuel_type_id'],
                                                            ['vehicle_fuel_type_id'],
                                                            orderby="vehicle_fuel_type_id DESC"):
            fuel_type_id = group['vehicle_fuel_type_id']
            if fuel_type_id:
                # Fetching fuel type name from vehicle.fuel.type model
                fuel_type = self.env['vehicle.fuel.type'].sudo().browse(int(fuel_type_id[0])).name
                top_five_fuel[fuel_type] = group['vehicle_fuel_type_id_count']
        # Sorting the fuel types by their count in descending order
        sorted_fuel = dict(sorted(top_five_fuel.items(), key=lambda item: item[1], reverse=True))
        return [list(sorted_fuel.keys()), list(sorted_fuel.values())]
