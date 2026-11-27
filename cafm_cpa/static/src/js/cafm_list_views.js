/** @odoo-module **/
/**
 * CAFM list views for Odoo 19 (were Odoo 14 ListController.extend / include):
 *  - cafm_tally_list        : AMC Invoice Register / VAR Work Report (Expand/Collapse,
 *                             Print Report, Format = import template wizard)
 *  - cafm_amc_register_list : AMC register month lines (Create AMC Contract, Format,
 *                             Print, X View, Next Invoice month filter, grand totals,
 *                             row click opens the AMC contract)
 *  - cafm_amc_invoice_list  : CAFM customer invoices (Status View, Yearly View)
 * plus the VAR Work import "create missing related records?" confirmation.
 */
import { onWillStart, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import { BaseImportModel } from "@base_import/import_model";
import {
    readStatusViewMode,
    readYearlyViewMode,
    setCafmInvoiceScreenActive,
    storeStatusViewMode,
    storeYearlyViewMode,
} from "@cafm_cpa/js/cafm_amc_invoice_toolbar";

const FORMAT_WIZARDS = {
    "cpabooks.cafm.amc.invoice.reg": ["cpabooks.cafm.amc.invoice.import", _t("Import AMC Invoices")],
    "cpabooks.cafm.var.work": ["cpabooks.cafm.var.import", _t("Import VAR Work")],
};

function plainDomain(domain) {
    try {
        return JSON.parse(JSON.stringify(domain || []));
    } catch {
        return [];
    }
}

async function walkGroups(groups, fn) {
    for (const group of groups || []) {
        await fn(group);
        if (!group.isFolded && group.list && group.list.groups) {
            await walkGroups(group.list.groups, fn);
        }
    }
}

function hasFoldedGroup(groups) {
    for (const group of groups || []) {
        if (group.isFolded) {
            return true;
        }
        if (group.list && group.list.groups && hasFoldedGroup(group.list.groups)) {
            return true;
        }
    }
    return false;
}

/* ---------------------------------------------------------------- tally */

export class CafmTallyListController extends ListController {
    setup() {
        super.setup();
        this.cafmAction = useService("action");
    }

    get cafmHasFolded() {
        return hasFoldedGroup(this.model.root.groups);
    }

    get cafmFormatWizard() {
        return FORMAT_WIZARDS[this.props.resModel];
    }

    async onCafmToggleExpand() {
        const expand = this.cafmHasFolded;
        for (let pass = 0; pass < 12; pass++) {
            let changed = false;
            await walkGroups(this.model.root.groups, async (group) => {
                if (expand && group.isFolded) {
                    await group.toggle();
                    changed = true;
                } else if (!expand && !group.isFolded) {
                    await group.toggle();
                    changed = true;
                }
            });
            if (!expand || !changed || !this.cafmHasFolded) {
                break;
            }
        }
    }

    onCafmPrintReport() {
        const isAmcInvoice = this.props.resModel === "cpabooks.cafm.amc.invoice.reg";
        return this.cafmAction.doAction({
            name: isAmcInvoice ? _t("Print AMC Invoices") : _t("Print VAR Work Statement"),
            type: "ir.actions.act_window",
            res_model: isAmcInvoice ? "cpabooks.amc.invoice.print.wizard" : "cpabooks.var.print.wizard",
            views: [[false, "form"]],
            target: "new",
            context: {},
        });
    }

    onCafmFormat() {
        const [resModel, name] = this.cafmFormatWizard;
        return this.cafmAction.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: resModel,
            views: [[false, "form"]],
            target: "new",
        });
    }
}

registry.category("views").add("cafm_tally_list", {
    ...listView,
    Controller: CafmTallyListController,
    buttonTemplate: "cafm_cpa.TallyListButtons",
});

/* ------------------------------------------------------ AMC register list */

const MONTH_FILTER_KEY = "cpa_cafm_amc_register_month_key";
const NEXT_INVOICE_MODE_KEY = "cpa_cafm_amc_next_invoice_mode";
const MONTH_ALL = "all";

function sessionGet(key) {
    try {
        return window.sessionStorage.getItem(key);
    } catch {
        return null;
    }
}

function sessionSet(key, value) {
    try {
        window.sessionStorage.setItem(key, value);
    } catch {
        // ignore
    }
}

function formatAmount(value) {
    const n = parseFloat(value);
    if (isNaN(n)) {
        return "0.00";
    }
    return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export class CafmAmcRegisterListController extends ListController {
    setup() {
        super.setup();
        this.cafmAction = useService("action");
        this.cafmOrm = useService("orm");
        this.cafmNotification = useService("notification");
        this.cafm = useState({
            nextInvoice: sessionGet(NEXT_INVOICE_MODE_KEY) === "1",
            monthKey: sessionGet(MONTH_FILTER_KEY) || MONTH_ALL,
            monthOptions: [],
            totals: null,
        });
        onWillStart(async () => {
            try {
                this.cafm.monthOptions =
                    (await this.cafmOrm.call(
                        "cpabooks.cafm.contract.month.line",
                        "cafm_register_month_filter_options",
                        []
                    )) || [];
            } catch {
                this.cafm.monthOptions = [];
            }
        });
        onWillStart(() => (this.cafm.nextInvoice ? this.cafmApplyViewMode() : null));
    }

    formatAmount(value) {
        return formatAmount(value);
    }

    get cafmDomain() {
        return plainDomain(this.model.root.domain);
    }

    async cafmApplyViewMode() {
        const domain = [...(this.props.domain || [])];
        let groupBy = [];
        if (this.cafm.nextInvoice) {
            if (this.cafm.monthKey === MONTH_ALL) {
                groupBy = ["month_label"];
                const keys = await this.cafmOrm.call(
                    "cpabooks.cafm.contract.month.line",
                    "cafm_register_rolling_month_keys",
                    []
                );
                if (keys && keys.length) {
                    domain.push(["month_key", "in", keys]);
                }
            } else {
                domain.push(["month_key", "=", this.cafm.monthKey]);
            }
        }
        await this.model.load({ domain, groupBy });
        await this.cafmLoadTotals();
    }

    async cafmLoadTotals() {
        this.cafm.totals = null;
        if (!this.cafm.nextInvoice || this.cafm.monthKey !== MONTH_ALL) {
            return;
        }
        try {
            this.cafm.totals = await this.cafmOrm.call(
                "cpabooks.cafm.contract.month.line",
                "cafm_register_amount_totals",
                [this.cafmDomain]
            );
        } catch {
            this.cafm.totals = null;
        }
    }

    async onCafmToggleNextInvoice() {
        this.cafm.nextInvoice = !this.cafm.nextInvoice;
        sessionSet(NEXT_INVOICE_MODE_KEY, this.cafm.nextInvoice ? "1" : "0");
        await this.cafmApplyViewMode();
    }

    async onCafmMonthChange(ev) {
        this.cafm.monthKey = ev.target.value || MONTH_ALL;
        sessionSet(MONTH_FILTER_KEY, this.cafm.monthKey);
        if (this.cafm.nextInvoice) {
            await this.cafmApplyViewMode();
        }
    }

    onCafmCreateContract() {
        return this.cafmAction.doAction({
            type: "ir.actions.act_window",
            name: _t("Create AMC Contract"),
            res_model: "cpabooks.cafm.contract",
            views: [[false, "form"]],
            target: "current",
        });
    }

    onCafmFormat() {
        return this.cafmAction.doAction({
            type: "ir.actions.act_window",
            name: _t("Import AMC Contracts"),
            res_model: "cpabooks.cafm.amc.import",
            views: [[false, "form"]],
            target: "new",
        });
    }

    async onCafmPrint() {
        try {
            const action = await this.cafmOrm.call(
                "cpabooks.cafm.contract",
                "action_open_next_invoice_print_wizard",
                [this.cafmDomain]
            );
            if (!action) {
                this.cafmNotification.add(_t("Could not open print wizard."), { type: "danger" });
                return;
            }
            action.views = action.views || [[false, "form"]];
            action.target = "new";
            return this.cafmAction.doAction(action);
        } catch {
            this.cafmNotification.add(_t("Print wizard failed. Check access rights and try again."), {
                type: "danger",
            });
        }
    }

    onCafmXView() {
        return this.cafmAction.doAction("cafm_cpa.action_cafm_cpa_amc_x_view", {
            additionalContext: { cafm_x_view_domain: this.cafmDomain },
        });
    }

    async openRecord(record) {
        // Rows are month lines: open the linked AMC contract.
        let contractId = record.data.contract_id && record.data.contract_id.id;
        if (!contractId && record.resId) {
            const rows = await this.cafmOrm.read(
                "cpabooks.cafm.contract.month.line",
                [record.resId],
                ["contract_id"]
            );
            contractId = rows[0] && rows[0].contract_id && rows[0].contract_id[0];
        }
        if (!contractId) {
            this.cafmNotification.add(_t("No linked contract found for this row."), { type: "warning" });
            return;
        }
        return this.cafmAction.doAction({
            type: "ir.actions.act_window",
            name: _t("AMC Contract"),
            res_model: "cpabooks.cafm.contract",
            res_id: contractId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("views").add("cafm_amc_register_list", {
    ...listView,
    Controller: CafmAmcRegisterListController,
    buttonTemplate: "cafm_cpa.AmcRegisterListButtons",
});

/* ----------------------------------------------------- CAFM invoice list */

export class CafmAmcInvoiceListController extends ListController {
    setup() {
        super.setup();
        this.cafmAction = useService("action");
        this.cafmOrm = useService("orm");
        this.cafmInvoice = useState({ yearly: readYearlyViewMode() });
        setCafmInvoiceScreenActive(true);
        storeStatusViewMode(false);
        onWillStart(() => {
            const ctx = this.props.context || {};
            if (ctx.cafm_yearly_view_on) {
                this.cafmInvoice.yearly = true;
                storeYearlyViewMode(true);
            }
            if (this.cafmInvoice.yearly && !(this.props.groupBy || []).includes("invoice_date:year")) {
                return this.model.load({ groupBy: ["invoice_date:year"] });
            }
        });
    }

    get cafmStatusOn() {
        return readStatusViewMode();
    }

    async onCafmStatusView() {
        storeStatusViewMode(true);
        const domain = plainDomain(this.model.root.domain);
        if (!domain.length) {
            const action = await this.cafmOrm.call("account.move", "action_cafm_open_status_view", []);
            return this.cafmAction.doAction(action);
        }
        return this.cafmAction.doAction({
            type: "ir.actions.client",
            tag: "cafm_cpa_amc_invoice_status",
            name: _t("AMC Invoice Status"),
            target: "current",
            params: { domain },
            context: { cafm_invoice_status_domain: domain, cafm_amc_invoice_list: 1 },
        });
    }

    async onCafmYearlyView() {
        this.cafmInvoice.yearly = !this.cafmInvoice.yearly;
        storeYearlyViewMode(this.cafmInvoice.yearly);
        await this.model.load({ groupBy: this.cafmInvoice.yearly ? ["invoice_date:year"] : [] });
    }
}

registry.category("views").add("cafm_amc_invoice_list", {
    ...listView,
    Controller: CafmAmcInvoiceListController,
    buttonTemplate: "cafm_cpa.AmcInvoiceListButtons",
});

/* ------------------------------------------- VAR Work import confirmation */

patch(BaseImportModel.prototype, {
    async executeImport(isTest = false, totalSteps, importProgress) {
        if (this.resModel === "cpabooks.cafm.var.work" && !isTest) {
            const fields = this.columns.map((c) => Boolean(c.fieldInfo) && c.fieldInfo.fieldPath);
            const columns = this.columns.map((c) => (c.name || "").trim().toLowerCase());
            try {
                const preview = await this.orm.call("base_import.import", "var_preview_missing_related", [
                    this.id,
                    fields,
                    columns,
                    this.formattedImportOptions,
                ]);
                if (preview && preview.message && !window.confirm(preview.message)) {
                    return { res: false };
                }
            } catch {
                // fall back to the standard import
            }
        }
        return super.executeImport(...arguments);
    },
});
