# -*- coding: utf-8 -*-
from odoo import _, models
from odoo.exceptions import AccessError

CANCEL_GROUP = 'cpabooks_all_cancel_extend.group_cpa_cancel_posted'


def check_cancel_rights(env):
    if not env.su and not env.user.has_group(CANCEL_GROUP):
        raise AccessError(_('Only users in the group "Cancel Posted Documents" '
                            'can cancel posted documents.'))


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _cpa_reconciled_payments(self):
        """Payments reconciled with these moves (not the moves' own payment)."""
        lines = self.line_ids.filtered(
            lambda l: l.account_id.account_type in ('asset_receivable', 'liability_payable'))
        counterparts = (lines.mapped('matched_debit_ids.debit_move_id')
                        | lines.mapped('matched_credit_ids.credit_move_id'))
        payments = counterparts.mapped('move_id.origin_payment_id')
        return (payments - self.mapped('origin_payment_id')).exists()

    def cpa_cancel_moves(self, mode=None, payment_mode=None):
        """Cancel posted moves.

        mode: 'cancel' | 'draft' | 'delete' (default: company setting)
        payment_mode: 'keep' | 'cancel' | 'draft' | 'delete' (default: company setting)
        """
        check_cancel_rights(self.env)
        for move in self.exists():
            company = move.company_id
            move_mode = mode or company.cpa_invoice_cancel_mode or 'cancel'
            pay_mode = payment_mode or company.cpa_payment_cancel_mode or 'keep'
            payments = move._cpa_reconciled_payments()
            if move.state == 'posted':
                # button_draft also removes the reconciliation.
                move.button_draft()
            if payments and pay_mode != 'keep':
                payments.cpa_cancel_payments(mode=pay_mode)
            if move_mode == 'draft':
                if move.state == 'cancel':
                    move.button_draft()
                continue
            if move.state != 'cancel':
                move.button_cancel()
            if move_mode == 'delete':
                if move.origin_payment_id:
                    move.origin_payment_id.with_context(force_delete=True).unlink()
                else:
                    move.with_context(force_delete=True).unlink()
        return True

    def action_cpa_cancel(self):
        self.cpa_cancel_moves()
        if not self.exists():
            return {'type': 'ir.actions.act_window_close'}
        return True
