/** @odoo-module **/
/**
 * CAFM app helpers. The CAFM chrome (left sidebar / dark shell) is provided by
 * the optional cpabooks_leftsidebar_view module; these helpers keep the CAFM
 * screens working without it on Odoo 19.
 */
import { currentAppXmlid } from "@cafm_cpa/js/legacy_compat";

const CAFM_APP_NAME = "CAFM";
const ROOT_MENU_XMLID = "cafm_cpa.menu_cafm_cpa_root";

export function isNavbarCafmBrand() {
    const brand = document.querySelector(".o_main_navbar .o_menu_brand");
    if (!brand) {
        return false;
    }
    const text = (brand.textContent || "").trim();
    return text === CAFM_APP_NAME || text.indexOf(CAFM_APP_NAME) === 0;
}

export function isCafmAppActive() {
    if (document.body.classList.contains("o_cafm_app_active")) {
        return true;
    }
    if (currentAppXmlid() === ROOT_MENU_XMLID) {
        return true;
    }
    if (
        document.querySelector(
            ".o_cfd_dashboard_main, .o_cafm_amc_register_tree, .o_cafm_x_view_action, " +
                ".o_cafm_invoice_status_action, .o_cafm_amc_invoice_screen"
        )
    ) {
        return true;
    }
    return isNavbarCafmBrand();
}

export function requestSyncSidebar() {
    // Sidebar lives in cpabooks_leftsidebar_view (optional); nothing to sync here.
}

export const syncSidebar = requestSyncSidebar;
