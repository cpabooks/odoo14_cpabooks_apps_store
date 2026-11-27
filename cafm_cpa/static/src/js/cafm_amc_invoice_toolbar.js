/** @odoo-module **/
/**
 * CAFM invoice screen state shared by the invoice list (cafm_amc_invoice_list)
 * and the AMC Invoice Status client action. In Odoo 19 the toolbar buttons are
 * rendered by the list controller itself (see cafm_list_views.js).
 */
const YEARLY_VIEW_KEY = "cpa_cafm_invoice_yearly_view";
const STATUS_VIEW_KEY = "cpa_cafm_invoice_status_view";

function read(key) {
    try {
        return window.sessionStorage.getItem(key);
    } catch {
        return null;
    }
}

function write(key, value) {
    try {
        window.sessionStorage.setItem(key, value);
    } catch {
        // ignore
    }
}

export function readYearlyViewMode() {
    const value = read(YEARLY_VIEW_KEY);
    return value === "1" || value === "true";
}

export function storeYearlyViewMode(on) {
    write(YEARLY_VIEW_KEY, on ? "1" : "0");
}

export function readStatusViewMode() {
    return read(STATUS_VIEW_KEY) === "1";
}

export function storeStatusViewMode(on) {
    write(STATUS_VIEW_KEY, on ? "1" : "0");
}

export function setCafmInvoiceScreenActive(active) {
    document.body.classList.toggle("o_cafm_amc_invoice_screen", Boolean(active));
}

export function scheduleEnhanceInvoiceToolbar() {
    setCafmInvoiceScreenActive(true);
}
