# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    contracting_invoice_default = fields.Boolean(
        string='New Customer Invoices as Construction',
        default=True,
        help='New customer invoices and credit notes open as Construction invoices '
             '(Work Done % billing). Switch to Labour Supply on the invoice when needed.',
    )
