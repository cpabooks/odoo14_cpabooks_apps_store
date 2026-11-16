# -*- coding: utf-8 -*-
from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero

from .account_move import check_cancel_rights


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _cpa_free_destination_stock(self, ml, qty):
        """Unreserve other moves if the stock we take back is reserved."""
        location = ml.location_dest_id
        if location.usage not in ('internal', 'transit'):
            return
        Quant = self.env['stock.quant'].sudo()
        available = Quant._get_available_quantity(
            ml.product_id, location, lot_id=ml.lot_id,
            package_id=ml.result_package_id, owner_id=ml.owner_id, strict=True)
        rounding = ml.product_id.uom_id.rounding
        if float_compare(available, qty, precision_rounding=rounding) >= 0:
            return
        reserving = self.env['stock.move.line'].sudo().search([
            ('product_id', '=', ml.product_id.id),
            ('location_id', 'child_of', location.id),
            ('state', 'not in', ('done', 'cancel', 'draft')),
            ('product_qty', '>', 0),
        ]).mapped('move_id')
        reserving._do_unreserve()

    def _cpa_revert_done(self):
        """Undo done moves: put the stock back and remove their valuation."""
        done_moves = self.filtered(lambda m: m.state == 'done')
        if not done_moves:
            return
        Quant = self.env['stock.quant'].sudo()
        for move in done_moves:
            next_done = move.move_dest_ids.filtered(lambda m: m.state == 'done')
            if next_done:
                raise UserError(_(
                    'Cancel the next operation first: %s'
                ) % ', '.join(next_done.mapped('picking_id.name') or next_done.mapped('reference')))
            move.move_dest_ids.filtered(
                lambda m: m.state not in ('done', 'cancel'))._do_unreserve()
            for ml in move.move_line_ids:
                if ml.product_id.type != 'product':
                    continue
                qty = ml.product_uom_id._compute_quantity(
                    ml.qty_done, ml.product_id.uom_id, rounding_method='HALF-UP')
                if float_is_zero(qty, precision_rounding=ml.product_id.uom_id.rounding):
                    continue
                move._cpa_free_destination_stock(ml, qty)
                Quant._update_available_quantity(
                    ml.product_id, ml.location_dest_id, -qty, lot_id=ml.lot_id,
                    package_id=ml.result_package_id, owner_id=ml.owner_id)
                Quant._update_available_quantity(
                    ml.product_id, ml.location_id, qty, lot_id=ml.lot_id,
                    package_id=ml.package_id, owner_id=ml.owner_id)
            # Valuation (stock_account), only when that module is installed.
            if 'account_move_ids' in move._fields:
                valuation_moves = move.sudo().account_move_ids
                posted = valuation_moves.filtered(lambda m: m.state == 'posted')
                posted.button_draft()
                valuation_moves.filtered(lambda m: m.state != 'cancel').button_cancel()
            if 'stock_valuation_layer_ids' in move._fields:
                move.sudo().stock_valuation_layer_ids.unlink()
        # Done move lines are kept on the cancelled picking as history.
        done_moves.write({'state': 'cancel'})


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def cpa_cancel_pickings(self, mode='cancel'):
        """mode: 'cancel' | 'draft' | 'delete'."""
        check_cancel_rights(self.env)
        pickings = self.exists()
        done = pickings.filtered(lambda p: p.state == 'done')
        done.mapped('move_lines')._cpa_revert_done()
        open_pickings = pickings.filtered(lambda p: p.state not in ('cancel', 'done'))
        if open_pickings:
            open_pickings.action_cancel()
        if mode == 'draft':
            pickings.action_cpa_set_draft()
        elif mode == 'delete':
            pickings.action_cpa_set_draft()
            pickings.unlink()
        return True

    def action_cpa_cancel(self):
        return self.cpa_cancel_pickings('cancel')

    def action_cpa_set_draft(self):
        check_cancel_rights(self.env)
        moves = self.filtered(lambda p: p.state == 'cancel').mapped('move_lines')
        moves = moves.filtered(lambda m: m.state == 'cancel')
        # Move lines of a cancelled move cannot be deleted, so set the
        # moves to draft first (stock was already put back on cancel).
        moves.write({'state': 'draft'})
        moves.mapped('move_line_ids').unlink()
        return True
