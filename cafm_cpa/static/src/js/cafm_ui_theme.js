/** @odoo-module **/
/** CAFM UI theme (Default / Dark), kept in the browser (localStorage). */
const $ = window.jQuery;

export const THEME_KEY = "cpa_cafm_ui_theme";
const LEGACY_KEY = "cpa_cafm_dashboard_theme";
export const LAYOUT_KEY = "cpa_cafm_nav_layout";
const NAV_CLASS = "o_cpa_cafm_navbar_theme";

export function readTheme() {
    try {
        let t = window.localStorage.getItem(THEME_KEY);
        if (t === "dark" || t === "default") {
            return t;
        }
        t = window.localStorage.getItem(LEGACY_KEY);
        if (t === "dark" || t === "default") {
            window.localStorage.setItem(THEME_KEY, t);
            return t;
        }
    } catch {
        // ignore
    }
    return "default";
}

export function readLayout() {
    try {
        const layout = window.localStorage.getItem(LAYOUT_KEY);
        if (layout === "topbar" || layout === "sidebar") {
            return layout;
        }
    } catch {
        // ignore
    }
    return "topbar";
}

export function setLayout(layout) {
    const value = layout === "sidebar" ? "sidebar" : "topbar";
    try {
        window.localStorage.setItem(LAYOUT_KEY, value);
    } catch {
        // ignore
    }
    return value;
}

export function applyUiTheme(theme) {
    theme = theme === "dark" ? "dark" : "default";
    const body = document.body;
    if (!body) {
        return theme;
    }
    body.classList.remove("o_cafm_ui_default", "o_cafm_ui_dark");
    body.classList.add(theme === "dark" ? "o_cafm_ui_dark" : "o_cafm_ui_default");
    try {
        window.localStorage.setItem(THEME_KEY, theme);
        window.localStorage.setItem(LEGACY_KEY, theme);
    } catch {
        // ignore
    }
    const $root = $(".cfd_root, .o_cfd_dashboard_main");
    if ($root.length) {
        $root
            .removeClass("cpa-cafm-theme-default cpa-cafm-theme-dark")
            .addClass(theme === "dark" ? "cpa-cafm-theme-dark" : "cpa-cafm-theme-default");
    }
    return theme;
}

export function injectNavbarThemeToggle() {
    $(".o_main_navbar ." + NAV_CLASS).remove();
}

export function syncNavbarToggleState() {
    return readTheme();
}

export function syncShellTheme() {
    injectNavbarThemeToggle();
    return applyUiTheme(readTheme());
}
