# -*- coding: utf-8 -*-
"""Odoo 14 account model compatibility for Odoo 19 (shared by CPABooks apps).

Odoo 16 replaced the ``account.account.type`` model by the ``account_type``
selection, and Odoo 17/18 replaced ``account.account.company_id`` by
``company_ids``, ``deprecated`` by ``active`` and made ``group_id`` a
non-stored compute. CPABooks accounting apps were written on the Odoo 14 API;
this module gives the old names back as compatible fields, in one place so
several apps can rely on them together.
"""
from odoo import api, fields, models

# code (= Odoo 19 account_type), Odoo 14 name, internal group, legacy type,
# include initial balance, xml id of the Odoo 14 type
STANDARD_ACCOUNT_TYPES = (
    ("asset_receivable", "Receivable", "asset", "receivable", True, "data_account_type_receivable"),
    ("asset_cash", "Bank and Cash", "asset", "liquidity", True, "data_account_type_liquidity"),
    ("asset_current", "Current Assets", "asset", "other", True, "data_account_type_current_assets"),
    ("asset_non_current", "Non-current Assets", "asset", "other", True, "data_account_type_non_current_assets"),
    ("asset_prepayments", "Prepayments", "asset", "other", True, "data_account_type_prepayments"),
    ("asset_fixed", "Fixed Assets", "asset", "other", True, "data_account_type_fixed_assets"),
    ("liability_payable", "Payable", "liability", "payable", True, "data_account_type_payable"),
    ("liability_credit_card", "Credit Card", "liability", "liquidity", True, "data_account_type_credit_card"),
    ("liability_current", "Current Liabilities", "liability", "other", True, "data_account_type_current_liabilities"),
    ("liability_non_current", "Non-current Liabilities", "liability", "other", True, "data_account_type_non_current_liabilities"),
    ("equity", "Equity", "equity", "other", True, "data_account_type_equity"),
    ("equity_unaffected", "Current Year Earnings", "equity", "other", True, "data_unaffected_earnings"),
    ("income", "Income", "income", "other", False, "data_account_type_revenue"),
    ("income_other", "Other Income", "income", "other", False, "data_account_type_other_income"),
    ("expense", "Expenses", "expense", "other", False, "data_account_type_expenses"),
    ("expense_depreciation", "Depreciation", "expense", "other", False, "data_account_type_depreciation"),
    ("expense_direct_cost", "Cost of Revenue", "expense", "other", False, "data_account_type_direct_costs"),
    ("off_balance", "Off-Balance Sheet", "off", "other", False, "data_account_off_sheet"),
)


class AccountAccountType(models.Model):
    _name = "account.account.type"
    _description = "Account Type"
    _order = "sequence, name, id"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True, index=True, help="Odoo 19 account type (account_type) of this type.")
    sequence = fields.Integer(default=10)
    internal_group = fields.Selection(
        [
            ("asset", "Asset"),
            ("liability", "Liability"),
            ("equity", "Equity"),
            ("income", "Income"),
            ("expense", "Expense"),
            ("off", "Off Balance"),
        ],
        string="Internal Group",
    )
    type = fields.Selection(
        [
            ("receivable", "Receivable"),
            ("payable", "Payable"),
            ("liquidity", "Liquidity"),
            ("other", "Regular"),
        ],
        string="Legacy type",
        default="other",
    )
    include_initial_balance = fields.Boolean(string="Bring Balance Forward")
    account_type = fields.Char(related="code", string="Account Type Code")
    note = fields.Text()

    _code_uniq = models.Constraint("unique(code)", "Account type code must be unique.")

    @api.model
    def _cpa_ensure_standard_types(self):
        existing = {rec.code: rec for rec in self.sudo().with_context(active_test=False).search([])}
        for seq, (code, name, internal_group, legacy, initial, _xmlid) in enumerate(STANDARD_ACCOUNT_TYPES, 1):
            if code in existing:
                continue
            self.sudo().create({
                "code": code,
                "name": name,
                "sequence": seq * 10,
                "internal_group": internal_group,
                "type": legacy,
                "include_initial_balance": initial,
            })
        return True

    @api.model
    def _cpa_by_code(self):
        return {rec.code: rec for rec in self.sudo().search([])}


class AccountAccount(models.Model):
    _inherit = "account.account"

    user_type_id = fields.Many2one(
        "account.account.type",
        string="Account Type (legacy)",
        index=True,
        compute="_compute_cpa_user_type_id",
        inverse="_inverse_cpa_user_type_id",
        store=True,
        readonly=False,
        ondelete="restrict",
    )
    internal_type = fields.Selection(related="user_type_id.type", string="Internal Type")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        compute="_compute_cpa_company_id",
        inverse="_inverse_cpa_company_id",
        search="_search_cpa_company_id",
    )
    deprecated = fields.Boolean(
        string="Deprecated",
        compute="_compute_cpa_deprecated",
        inverse="_inverse_cpa_deprecated",
        store=True,
    )
    # Odoo 19 computes the group from the code prefix; CPABooks apps also assign
    # it directly, so keep it stored and editable (still recomputed on code change).
    group_id = fields.Many2one(store=True, readonly=False, index=True)

    @api.depends("account_type")
    def _compute_cpa_user_type_id(self):
        by_code = self.env["account.account.type"]._cpa_by_code()
        for acc in self:
            acc.user_type_id = by_code.get(acc.account_type, False)

    def _inverse_cpa_user_type_id(self):
        for acc in self:
            code = acc.user_type_id.code
            if code and acc.account_type != code:
                acc.account_type = code

    @api.depends("company_ids")
    @api.depends_context("allowed_company_ids", "company")
    def _compute_cpa_company_id(self):
        current = self.env.company
        for acc in self:
            companies = acc.company_ids
            if current and current in companies:
                acc.company_id = current
            elif companies:
                acc.company_id = companies[0]
            else:
                acc.company_id = False

    def _inverse_cpa_company_id(self):
        for acc in self:
            if acc.company_id and acc.company_id not in acc.company_ids:
                acc.company_ids = [(6, 0, acc.company_id.ids)]

    def _search_cpa_company_id(self, operator, value):
        return [("company_ids", operator, value)]

    @api.depends("active")
    def _compute_cpa_deprecated(self):
        for acc in self:
            acc.deprecated = not acc.active

    def _inverse_cpa_deprecated(self):
        for acc in self:
            acc.active = not acc.deprecated

    @api.model_create_multi
    def create(self, vals_list):
        types = None
        for vals in vals_list:
            # Odoo 14 style vals: user_type_id / company_id / deprecated
            if vals.get("user_type_id") and not vals.get("account_type"):
                if types is None:
                    types = {t.id: t for t in self.env["account.account.type"].sudo().search([])}
                legacy = types.get(vals["user_type_id"])
                if legacy:
                    vals["account_type"] = legacy.code
            if vals.get("company_id") and not vals.get("company_ids"):
                vals["company_ids"] = [(6, 0, [vals["company_id"]])]
            if "deprecated" in vals and "active" not in vals:
                vals["active"] = not vals["deprecated"]
        return super().create(vals_list)
