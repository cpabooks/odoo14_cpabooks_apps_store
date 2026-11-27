# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    style = fields.Char(string='Style')
    # Odoo 19 removed res.partner.mobile; CAFM tenants, calls, SOA and reports
    # still use it. Same column name, so data from Odoo 14 databases is kept.
    mobile = fields.Char(string='Mobile')
    delivery_instructions = fields.Text(string='Delivery Instructions')
