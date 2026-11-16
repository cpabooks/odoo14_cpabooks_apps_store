# -*- coding: utf-8 -*-
from odoo import fields, models

INVOICE_MODES = [
    ('cancel', 'Cancel'),
    ('draft', 'Cancel and Reset to Draft'),
    ('delete', 'Cancel and Delete'),
]
PAYMENT_MODES = [
    ('keep', 'Keep (only unreconcile)'),
    ('cancel', 'Cancel'),
    ('draft', 'Cancel and Reset to Draft'),
    ('delete', 'Cancel and Delete'),
]


class ResCompany(models.Model):
    _inherit = 'res.company'

    cpa_invoice_cancel_mode = fields.Selection(
        INVOICE_MODES, string='Invoice Cancel Mode', default='cancel',
        help='What the "Cancel Entry" button does with a posted invoice or journal entry.')
    cpa_payment_cancel_mode = fields.Selection(
        PAYMENT_MODES, string='Linked Payment Mode', default='keep',
        help='What happens to the payments reconciled with an invoice when '
             'that invoice is cancelled.')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cpa_invoice_cancel_mode = fields.Selection(
        related='company_id.cpa_invoice_cancel_mode', readonly=False)
    cpa_payment_cancel_mode = fields.Selection(
        related='company_id.cpa_payment_cancel_mode', readonly=False)
