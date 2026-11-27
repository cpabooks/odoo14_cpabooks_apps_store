# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_is_zero


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Work Done % is applied to the accounting through the standard `discount`
    # field: discount = 100 - (100 - line discount) * Work Done % / 100.
    # Both values use 2 decimals, so the claimed amount, the taxes and the
    # journal entry stay exact. `contract_discount` keeps the real discount.
    contract_discount = fields.Float(
        string='Line Disc.%',
        digits='Discount',
        default=0.0,
        help='Commercial discount of the line. On a Construction invoice the '
             'standard discount column holds the Work Done % factor instead.',
    )
    contract_previous_pct = fields.Float(
        string='Previous %',
        digits=(16, 2),
        default=0.0,
        help='Percentage of this line already claimed on earlier invoices.',
    )
    contract_work_done_pct = fields.Float(
        string='Work Done %',
        digits=(16, 2),
        default=100.0,
        help='Percentage of the contract amount claimed on this invoice.',
    )
    contract_guaranteed = fields.Boolean(string='Gtee')
    contract_amount = fields.Monetary(
        string='Contract Amount',
        currency_field='currency_id',
        compute='_compute_contract_amounts',
        help='Full line value excluding tax (quantity x unit price, less the line discount).',
    )
    contract_tax_amount = fields.Monetary(
        string='Tax Amt',
        currency_field='currency_id',
        compute='_compute_contract_amounts',
        help='Tax on the Work Done amount of the line.',
    )

    @api.depends('quantity', 'price_unit', 'contract_discount', 'tax_ids',
                 'price_subtotal', 'price_total', 'currency_id')
    def _compute_contract_amounts(self):
        for line in self:
            amount = 0.0
            if line.display_type == 'product':
                price = line.price_unit * (1 - (line.contract_discount or 0.0) / 100.0)
                if line.tax_ids:
                    res = line.tax_ids._origin.with_context(force_sign=1).compute_all(
                        price,
                        currency=line.currency_id,
                        quantity=line.quantity,
                        product=line.product_id,
                        partner=line.partner_id,
                        is_refund=line.move_id.move_type in ('out_refund', 'in_refund'),
                    )
                    amount = res['total_excluded']
                else:
                    amount = line.quantity * price
            line.contract_amount = amount
            line.contract_tax_amount = (line.price_total or 0.0) - (line.price_subtotal or 0.0)

    @api.constrains('contract_previous_pct', 'contract_work_done_pct')
    def _check_contract_percentages(self):
        for line in self:
            for value, label in ((line.contract_previous_pct, _('Previous %')),
                                 (line.contract_work_done_pct, _('Work Done %'))):
                if float_compare(value, 0.0, precision_digits=2) < 0 or \
                        float_compare(value, 100.0, precision_digits=2) > 0:
                    raise ValidationError(_('%s must be between 0 and 100 (line "%s").')
                                          % (label, line.name or line.product_id.display_name or ''))

    # ------------------------------------------------------------------
    # Work Done % <-> discount synchronisation
    # ------------------------------------------------------------------

    def _contracting_effective_discount(self):
        self.ensure_one()
        pct = min(max(self.contract_work_done_pct or 0.0, 0.0), 100.0)
        return 100.0 - (100.0 - (self.contract_discount or 0.0)) * pct / 100.0

    def _contracting_is_product_line(self):
        self.ensure_one()
        return self.display_type == 'product'

    def _contracting_sync_discount(self, construction):
        """Make `discount` follow the Contracting values (or the reverse in Labour Supply).

        Works on real and on new (onchange) records. Returns the lines whose
        discount changed.
        """
        changed = self.browse()
        for line in self:
            if not line._contracting_is_product_line():
                continue
            if not construction:
                if float_compare(line.contract_discount, line.discount, precision_digits=4):
                    line.contract_discount = line.discount
                continue
            if float_compare(line.contract_work_done_pct, 100.0, precision_digits=2) == 0 \
                    and float_is_zero(line.contract_discount, precision_digits=4) \
                    and not float_is_zero(line.discount, precision_digits=4):
                # Untouched line at 100 %: its discount is the real discount
                # (e.g. a line created from a sales order).
                line.contract_discount = line.discount
                continue
            effective = line._contracting_effective_discount()
            if float_compare(line.discount, effective, precision_digits=4):
                line.discount = effective
                changed |= line
        return changed

    @api.onchange('contract_work_done_pct', 'contract_discount')
    def _onchange_contracting_values(self):
        for line in self:
            if not line.move_id.is_construction_invoice or not line._contracting_is_product_line():
                continue
            line.discount = line._contracting_effective_discount()
            if float_compare(line.contract_previous_pct + line.contract_work_done_pct, 100.0,
                             precision_digits=2) > 0:
                return {'warning': {
                    'title': _('Work Done above 100 %'),
                    'message': _('Previous % plus Work Done % is above 100 % on "%s".')
                               % (line.name or line.product_id.display_name or ''),
                }}

    @api.onchange('discount')
    def _onchange_contracting_discount(self):
        for line in self:
            if not line.move_id.is_construction_invoice:
                line.contract_discount = line.discount
