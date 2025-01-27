# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class ProjectTask(models.Model):
    """Project Task"""
    _inherit = 'project.task'
    _description = __doc__

    repair_job_card_id = fields.Many2one('repair.job.card',
                                         string=" Job Card")
    r_vehicle_brand_id = fields.Many2one(related='repair_job_card_id.vehicle_brand_id',
                                         string=" Brand")
    r_vehicle_model_id = fields.Many2one(related='repair_job_card_id.vehicle_model_id',
                                         string=" Model")
    r_vehicle_fuel_type_id = fields.Many2one(related='repair_job_card_id.vehicle_fuel_type_id',
                                             string=" Fuel Type")
    r_registration_no = fields.Char(related='repair_job_card_id.registration_no',
                                    string=" Registration No", translate=True)
    r_vin_no = fields.Char(related='repair_job_card_id.vin_no',
                           string=" VIN No", translate=True)
    r_transmission_type = fields.Selection(related='repair_job_card_id.transmission_type',
                                           string=" Transmission Type")
    work_is_done = fields.Boolean(string="Work is Done")

    # unused
    inspection_job_card_id = fields.Many2one('inspection.job.card',
                                             string="Job Card")
    i_vehicle_brand_id = fields.Many2one(related='inspection_job_card_id.vehicle_brand_id',
                                         string="Brand")
    i_vehicle_model_id = fields.Many2one(related='inspection_job_card_id.vehicle_model_id',
                                         string="Model")
    i_vehicle_fuel_type_id = fields.Many2one(related='inspection_job_card_id.vehicle_fuel_type_id',
                                             string="Fuel Type")
    i_registration_no = fields.Char(related='inspection_job_card_id.registration_no',
                                    string="Registration No",
                                    translate=True)
    i_vin_no = fields.Char(related='inspection_job_card_id.vin_no',
                           string="VIN No", translate=True)
    i_transmission_type = fields.Selection(related='inspection_job_card_id.transmission_type',
                                           string="Transmission Type")

    vehicle_service_id = fields.Many2one('vehicle.service', string="Service")
    task_spare_parts_ids = fields.One2many(comodel_name='task.spare.parts',
                                           inverse_name='project_task_id',
                                           string="Task Spare Parts")

    def repair_service_work_done(self):
        """Repair service work done"""
        self.work_is_done = True
