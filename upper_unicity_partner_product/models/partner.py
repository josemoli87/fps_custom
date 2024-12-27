# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class UniquePartner(models.Model):
    _inherit = 'res.partner'

    _sql_constraints = [('partner_vat_unique', 'unique(vat)',
                         'El número de CI o Rif ya esta registrado por favor revise los datos!')]

    @api.onchange('name')
    def _compute_maj_par(self):
        self.name = self.name.upper() if self.name else False


@api.constrains('vat')
def _check_vat_format(self):
    # Una letra mayúscula seguida de 9 dígitos
    pattern = r'^[A-Z]{1}\d{9}$'
    for record in self:
        if record.vat and not re.match(pattern, record.vat):
            raise ValidationError(
                "La CI o Rif debe comenzar con una Mayuscula seguida por 9 números (e.g V123456789).")
