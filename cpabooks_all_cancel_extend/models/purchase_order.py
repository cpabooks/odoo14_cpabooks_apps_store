# -*- coding: utf-8 -*-
from odoo import models

from .account_move import CANCEL_GROUP, check_cancel_rights


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _cpa_needs_full_cancel(self):
        return any(
            order.invoice_ids.filtered(lambda m: m.state == 'posted')
            or order.picking_ids.filtered(lambda p: p.state == 'done')
            for order in self)

    def button_cancel(self):
        # Users with the cancel group: the standard Cancel button also
        # cancels posted bills and done receipts.
        if self.env.user.has_group(CANCEL_GROUP) and self._cpa_needs_full_cancel():
            self._cpa_cancel_related('cancel')
        return super().button_cancel()

    def _cpa_cancel_related(self, mode):
        bills = self.mapped('invoice_ids').filtered(lambda m: m.state != 'cancel')
        if bills:
            bills.cpa_cancel_moves(mode='delete' if mode == 'delete' else 'cancel')
        done = self.mapped('picking_ids').filtered(lambda p: p.state == 'done')
        if done:
            done.cpa_cancel_pickings('cancel')

    def cpa_cancel_orders(self, mode='cancel'):
        """mode: 'cancel' | 'draft' | 'delete'."""
        check_cancel_rights(self.env)
        orders = self.exists()
        orders._cpa_cancel_related(mode)
        to_cancel = orders.filtered(lambda o: o.state != 'cancel')
        if to_cancel:
            super(PurchaseOrder, to_cancel).button_cancel()
        if mode == 'draft':
            orders.button_draft()
        elif mode == 'delete':
            pickings = orders.mapped('picking_ids')
            if pickings:
                pickings.cpa_cancel_pickings('delete')
            orders.unlink()
        return True
