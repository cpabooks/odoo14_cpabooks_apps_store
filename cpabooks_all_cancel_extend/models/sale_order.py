# -*- coding: utf-8 -*-
from odoo import models

from .account_move import CANCEL_GROUP, check_cancel_rights


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _cpa_needs_full_cancel(self):
        return any(
            order.invoice_ids.filtered(lambda m: m.state == 'posted')
            or order.picking_ids.filtered(lambda p: p.state == 'done')
            for order in self)

    def action_cancel(self):
        # Users with the cancel group: the standard Cancel button also
        # cancels posted invoices and done deliveries.
        if self.env.user.has_group(CANCEL_GROUP) and self._cpa_needs_full_cancel():
            self.cpa_cancel_orders('cancel')
            return True
        return super().action_cancel()

    def cpa_cancel_orders(self, mode='cancel'):
        """mode: 'cancel' | 'draft' | 'delete'."""
        check_cancel_rights(self.env)
        orders = self.exists()
        invoices = orders.mapped('invoice_ids').filtered(lambda m: m.state != 'cancel')
        if invoices:
            invoices.cpa_cancel_moves(mode='delete' if mode == 'delete' else 'cancel')
        pickings = orders.mapped('picking_ids')
        if pickings:
            pickings.cpa_cancel_pickings('delete' if mode == 'delete' else 'cancel')
        to_cancel = orders.filtered(lambda o: o.state != 'cancel')
        if to_cancel:
            to_cancel.with_context(disable_cancel_warning=True)._action_cancel()
        if mode == 'draft':
            orders.action_draft()
        elif mode == 'delete':
            orders.unlink()
        return True
