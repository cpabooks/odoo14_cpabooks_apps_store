# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    contracting_invoice_default = fields.Boolean(
        related='company_id.contracting_invoice_default',
        readonly=False,
    )
