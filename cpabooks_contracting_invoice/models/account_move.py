# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError

CONTRACTING_MOVE_TYPES = ('out_invoice', 'out_refund')


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_construction_invoice = fields.Boolean(
        string='Construction Invoice',
        default=False,
        copy=True,
        tracking=True,
        help='On: Construction invoice. Each line is billed at its Work Done %.\n'
             'Off: Labour Supply invoice (standard quantity x price billing).',
    )
    contract_amount_total = fields.Monetary(
        string='Contract Amount',
        currency_field='currency_id',
        compute='_compute_contract_amount_total',
    )

    @api.depends('invoice_line_ids.contract_amount')
    def _compute_contract_amount_total(self):
        for move in self:
            move.contract_amount_total = sum(move.invoice_line_ids.mapped('contract_amount'))

    @api.model
    def default_get(self, fields_list):
        res = super(AccountMove, self).default_get(fields_list)
        if 'is_construction_invoice' in fields_list:
            move_type = res.get('move_type') or self.env.context.get('default_move_type')
            company = self.env['res.company'].browse(res.get('company_id')) if res.get('company_id') \
                else self.env.company
            res['is_construction_invoice'] = bool(
                move_type in CONTRACTING_MOVE_TYPES and company.contracting_invoice_default
            )
        return res

    # ------------------------------------------------------------------
    # Keep the lines in line with the Labour Supply / Construction switch
    # ------------------------------------------------------------------

    def _contracting_product_lines(self):
        return self.invoice_line_ids.filtered(lambda line: line._contracting_is_product_line())

    @api.onchange('is_construction_invoice')
    def _onchange_is_construction_invoice(self):
        if self.move_type not in CONTRACTING_MOVE_TYPES and self.is_construction_invoice:
            self.is_construction_invoice = False
            return
        lines = self._contracting_product_lines()
        if self.is_construction_invoice:
            changed = lines._contracting_sync_discount(True)
        else:
            # Back to Labour Supply: give the lines their real discount again.
            changed = lines.browse()
            for line in lines:
                if line.discount != line.contract_discount:
                    line.discount = line.contract_discount
                    changed |= line
        if changed:
            changed.recompute_tax_line = True
            changed._onchange_price_subtotal()
            self._onchange_invoice_line_ids()

    def _move_autocomplete_invoice_lines_values(self):
        # Server-side create / write with invoice_line_ids (API, sales order
        # invoicing, "Next Progress Claim"): align the discount first, Odoo
        # then recomputes subtotals, taxes and payment terms.
        # Here the lines are in line_ids (invoice_line_ids is not filled yet on
        # the new record built by Odoo).
        lines = self.line_ids.filtered(lambda line: line._contracting_is_product_line())
        lines._contracting_sync_discount(self.is_construction_invoice)
        return super(AccountMove, self)._move_autocomplete_invoice_lines_values()

    def write(self, vals):
        switch = 'is_construction_invoice' in vals \
            and 'invoice_line_ids' not in vals and 'line_ids' not in vals
        to_resync = self.browse()
        if switch:
            for move in self:
                if bool(vals['is_construction_invoice']) == move.is_construction_invoice:
                    continue
                if vals['is_construction_invoice'] and move.move_type not in CONTRACTING_MOVE_TYPES:
                    raise UserError(_('Construction invoices are available on customer invoices '
                                      'and credit notes only.'))
                if move.state != 'draft':
                    raise UserError(_('Reset %s to draft before switching between Labour Supply '
                                      'and Construction.') % (move.name or _('the invoice')))
                to_resync |= move
        res = super(AccountMove, self).write(vals)
        for move in to_resync:
            move._contracting_resync_lines()
        return res

    def _contracting_resync_lines(self):
        """Re-run Odoo's invoice line autocomplete after a Labour/Construction switch."""
        self.ensure_one()
        lines = self._contracting_product_lines()
        if not lines:
            return
        # Pass every value explicitly: Odoo reuses the cache of the record
        # built by new(origin=...) inside one transaction, so values left out
        # here could be stale.
        construction = self.is_construction_invoice
        commands = []
        for line in lines:
            commands.append((1, line.id, {
                'contract_discount': line.contract_discount,
                'contract_work_done_pct': line.contract_work_done_pct,
                'discount': line._contracting_effective_discount() if construction else line.contract_discount,
            }))
        self.write({'is_construction_invoice': construction, 'invoice_line_ids': commands})

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def action_contracting_next_claim(self):
        """Copy a Construction invoice for the next progress claim.

        Previous % becomes Previous % + Work Done %, Work Done % starts at 0.
        """
        self.ensure_one()
        if not self.is_construction_invoice:
            raise UserError(_('Next Progress Claim is available on Construction invoices only.'))
        new_move = self.copy({'is_construction_invoice': True})
        old_lines = self._contracting_product_lines().sorted(lambda l: (l.sequence, l.id))
        new_lines = new_move._contracting_product_lines().sorted(lambda l: (l.sequence, l.id))
        commands = []
        for old, new in zip(old_lines, new_lines):
            commands.append((1, new.id, {
                'contract_discount': old.contract_discount,
                'contract_previous_pct': min(100.0, old.contract_previous_pct + old.contract_work_done_pct),
                'contract_work_done_pct': 0.0,
            }))
        if commands:
            new_move.write({'invoice_line_ids': commands})
        new_move.message_post(body=_('Next progress claim created from %s.') % (self.name or self.display_name))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': new_move.id,
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'current',
        }

    def action_print_contracting_invoice(self):
        return self.env.ref('cpabooks_contracting_invoice.action_report_contracting_invoice').report_action(self)
