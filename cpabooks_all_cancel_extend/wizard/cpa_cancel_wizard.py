# -*- coding: utf-8 -*-
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..models.account_move import check_cancel_rights

_logger = logging.getLogger(__name__)

SUPPORTED_MODELS = {
    'account.move': 'Invoices / Journal Entries',
    'account.payment': 'Payments',
    'sale.order': 'Sale Orders',
    'purchase.order': 'Purchase Orders',
    'stock.picking': 'Transfers',
    'hr.expense.sheet': 'Expense Reports',
}
# Models from optional apps: the "Cancel / Reset / Delete" action is bound
# at runtime when the app is installed (see _register_hook).
OPTIONAL_BINDINGS = {
    'hr.expense.sheet': 'action_cpa_cancel_wizard_expense_sheet',
}


class CpaCancelWizard(models.TransientModel):
    _name = 'cpa.cancel.wizard'
    _description = 'Cancel / Reset / Delete Posted Documents'

    res_model = fields.Char(required=True, readonly=True)
    res_ids = fields.Text(required=True, readonly=True)
    record_count = fields.Integer(readonly=True)
    model_label = fields.Char(readonly=True)
    operation = fields.Selection([
        ('cancel', 'Cancel'),
        ('draft', 'Cancel and Reset to Draft'),
        ('delete', 'Cancel and Delete'),
    ], required=True, default='cancel')
    payment_mode = fields.Selection([
        ('keep', 'Keep (only unreconcile)'),
        ('cancel', 'Cancel'),
        ('draft', 'Cancel and Reset to Draft'),
        ('delete', 'Cancel and Delete'),
    ], string='Linked Payments',
        default=lambda self: self.env.company.cpa_payment_cancel_mode or 'keep')

    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        model = self.env.context.get('active_model')
        ids = self.env.context.get('active_ids') or (
            [self.env.context['active_id']] if self.env.context.get('active_id') else [])
        if model in SUPPORTED_MODELS and ids:
            res.update({
                'res_model': model,
                'res_ids': ','.join(str(i) for i in ids),
                'record_count': len(ids),
                'model_label': _(SUPPORTED_MODELS[model]),
            })
        return res

    def _records(self):
        self.ensure_one()
        if self.res_model not in SUPPORTED_MODELS or self.res_model not in self.env:
            raise UserError(_('This document type is not supported.'))
        ids = [int(i) for i in (self.res_ids or '').split(',') if i.strip()]
        return self.env[self.res_model].browse(ids).exists()

    def action_apply(self):
        self.ensure_one()
        check_cancel_rights(self.env)
        records = self._records()
        if not records:
            return {'type': 'ir.actions.act_window_close'}
        op = self.operation
        if self.res_model == 'account.move':
            records.cpa_cancel_moves(mode=op, payment_mode=self.payment_mode)
        elif self.res_model == 'account.payment':
            records.cpa_cancel_payments(mode=op)
        elif self.res_model in ('sale.order', 'purchase.order', 'stock.picking'):
            if self.res_model == 'stock.picking':
                records.cpa_cancel_pickings(op)
            else:
                records.cpa_cancel_orders(op)
        elif self.res_model == 'hr.expense.sheet':
            self._cancel_expense_sheets(records, op)
        if op == 'delete':
            return {'type': 'ir.actions.client', 'tag': 'reload'}
        return {'type': 'ir.actions.act_window_close'}

    def _cancel_expense_sheets(self, sheets, op):
        for sheet in sheets:
            move = sheet.account_move_id
            if move:
                lines = move.line_ids.filtered(
                    lambda l: l.account_id.internal_type in ('receivable', 'payable'))
                payments = (lines.mapped('matched_debit_ids.debit_move_id.move_id.payment_id')
                            | lines.mapped('matched_credit_ids.credit_move_id.move_id.payment_id'))
                if move.state == 'posted':
                    move.button_draft()
                if payments:
                    payments.cpa_cancel_payments(mode='delete')
                sheet.write({'account_move_id': False})
                move.with_context(force_delete=True).unlink()
            # Back to draft so the report can be edited or deleted.
            sheet.reset_expense_sheets()
            if op == 'cancel':
                sheet.write({'state': 'cancel'})
            elif op == 'delete':
                expenses = sheet.expense_line_ids
                sheet.unlink()
                expenses.unlink()

    # ------------------------------------------------------------------
    # Bind the action on models of optional apps (e.g. Expenses)
    # ------------------------------------------------------------------
    def _register_hook(self):
        res = super()._register_hook()
        try:
            self._cpa_bind_optional_models()
        except Exception:
            _logger.warning('All in One Cancel: optional bindings skipped', exc_info=True)
        return res

    @api.model
    def _cpa_bind_optional_models(self):
        IrModel = self.env['ir.model'].sudo()
        Data = self.env['ir.model.data'].sudo()
        group = self.env.ref(
            'cpabooks_all_cancel_extend.group_cpa_cancel_posted', raise_if_not_found=False)
        for model_name, xml_name in OPTIONAL_BINDINGS.items():
            if model_name not in self.env:
                continue
            xmlid = 'cpabooks_all_cancel_extend.%s' % xml_name
            if self.env.ref(xmlid, raise_if_not_found=False):
                continue
            model = IrModel.search([('model', '=', model_name)], limit=1)
            if not model:
                continue
            action = self.env['ir.actions.act_window'].sudo().create({
                'name': _('Cancel / Reset / Delete'),
                'res_model': 'cpa.cancel.wizard',
                'view_mode': 'form',
                'target': 'new',
                'binding_model_id': model.id,
                'binding_view_types': 'list,form',
                'groups_id': [(6, 0, group.ids)] if group else [],
            })
            Data.create({
                'module': 'cpabooks_all_cancel_extend',
                'name': xml_name,
                'model': 'ir.actions.act_window',
                'res_id': action.id,
                'noupdate': True,
            })
