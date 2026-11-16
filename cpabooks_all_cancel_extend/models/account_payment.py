# -*- coding: utf-8 -*-
from odoo import models

from .account_move import check_cancel_rights


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def cpa_cancel_payments(self, mode=None):
        """mode: 'cancel' | 'draft' | 'delete' (default: company payment mode)."""
        check_cancel_rights(self.env)
        for payment in self.exists():
            pay_mode = mode or payment.company_id.cpa_payment_cancel_mode or 'cancel'
            if pay_mode == 'keep':
                pay_mode = 'cancel'
            if payment.state == 'posted':
                payment.action_draft()
            if pay_mode == 'draft':
                if payment.state == 'cancel':
                    payment.action_draft()
                continue
            if payment.state != 'cancel':
                payment.action_cancel()
            if pay_mode == 'delete':
                payment.with_context(force_delete=True).unlink()
        return True

    def action_cpa_cancel(self):
        self.cpa_cancel_payments()
        if not self.exists():
            return {'type': 'ir.actions.act_window_close'}
        return True
