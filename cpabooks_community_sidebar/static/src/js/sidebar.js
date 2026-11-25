/** @odoo-module **/
/**
 * Community App Sidebar (Odoo 19)
 *
 * Fixed left sidebar listing every installed app with its sub menus and a
 * search box. "Default menu" (systray button or user menu) switches back to
 * the standard Odoo top menu bar; the choice is remembered in the browser.
 */
import { Component, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { useBus, useService } from "@web/core/utils/hooks";

const STORAGE_KEY = "cpabooks_community_sidebar.default_menu";
const COLORS = ["#0f766e", "#1d4ed8", "#7c3aed", "#be185d", "#c2410c", "#15803d", "#0369a1", "#4338ca"];

function letterColor(name) {
    let n = 0;
    for (const ch of name || "") {
        n = (n + ch.charCodeAt(0)) % COLORS.length;
    }
    return COLORS[n];
}

function isDefaultMenu() {
    try {
        return browser.localStorage.getItem(STORAGE_KEY) === "1";
    } catch {
        return false;
    }
}

function applyMode(defaultMenu) {
    document.body.classList.add("o_ccs_enabled");
    document.body.classList.toggle("o_ccs_show_default_menu", defaultMenu);
}

export function toggleDefaultMenu() {
    const defaultMenu = !isDefaultMenu();
    try {
        browser.localStorage.setItem(STORAGE_KEY, defaultMenu ? "1" : "0");
    } catch {
        // private window: keep the choice for this page only
    }
    applyMode(defaultMenu);
}

function menuMatches(menu, query) {
    if ((menu.name || "").toLowerCase().includes(query)) {
        return true;
    }
    return (menu.childrenTree || []).some((child) => menuMatches(child, query));
}

export class SidebarMenuNode extends Component {
    static template = "cpabooks_community_sidebar.SidebarMenuNode";
    static props = {
        menu: Object,
        query: String,
        activeMenuId: { optional: true },
        onOpenMenu: Function,
    };

    setup() {
        this.state = useState({ open: false });
    }

    get children() {
        const children = this.props.menu.childrenTree || [];
        if (!this.props.query) {
            return children;
        }
        return children.filter((child) => menuMatches(child, this.props.query));
    }

    get isOpen() {
        return this.state.open || Boolean(this.props.query);
    }

    onClick() {
        if (this.children.length) {
            this.state.open = !this.state.open;
        }
        if (this.props.menu.actionID) {
            this.props.onOpenMenu(this.props.menu);
        }
    }
}
SidebarMenuNode.components = { SidebarMenuNode };

export class CommunitySidebar extends Component {
    static template = "cpabooks_community_sidebar.CommunitySidebar";
    static components = { SidebarMenuNode };
    static props = {};

    setup() {
        this.menuService = useService("menu");
        const current = this.menuService.getCurrentApp();
        this.state = useState({
            search: "",
            openAppId: current ? current.id : false,
            currentAppId: current ? current.id : false,
            activeMenuId: false,
        });
        useBus(this.env.bus, "MENUS:APP-CHANGED", () => {
            const app = this.menuService.getCurrentApp();
            this.state.currentAppId = app ? app.id : false;
            if (app) {
                this.state.openAppId = app.id;
            }
        });
        applyMode(isDefaultMenu());
    }

    get query() {
        return this.state.search.trim().toLowerCase();
    }

    get apps() {
        const apps = this.menuService.getApps().map((app) => this.menuService.getMenuAsTree(app.id));
        if (!this.query) {
            return apps;
        }
        return apps.filter((app) => menuMatches(app, this.query));
    }

    appChildren(app) {
        const children = app.childrenTree || [];
        if (!this.query) {
            return children;
        }
        return children.filter((child) => menuMatches(child, this.query));
    }

    isAppOpen(app) {
        return Boolean(this.query) || this.state.openAppId === app.id;
    }

    letter(app) {
        return (app.name || "A").charAt(0).toUpperCase();
    }

    color(app) {
        return letterColor(app.name);
    }

    onSearch(ev) {
        this.state.search = ev.target.value || "";
    }

    toggleApp(app) {
        this.state.openAppId = this.state.openAppId === app.id ? false : app.id;
    }

    openApp(app) {
        this.state.openAppId = app.id;
        this.state.activeMenuId = false;
        this.menuService.selectMenu(app);
    }

    openMenu(menu) {
        this.state.activeMenuId = menu.id;
        this.menuService.selectMenu(menu);
    }

    showDefaultMenu() {
        toggleDefaultMenu();
    }
}

export class CommunitySidebarSystray extends Component {
    static template = "cpabooks_community_sidebar.SystrayToggle";
    static props = {};

    get title() {
        return _t("Switch between the app sidebar and the default menu bar");
    }

    onClick() {
        toggleDefaultMenu();
    }
}

registry.category("main_components").add("cpabooks_community_sidebar", {
    Component: CommunitySidebar,
});

registry.category("systray").add(
    "cpabooks_community_sidebar.toggle",
    { Component: CommunitySidebarSystray },
    { sequence: 100 }
);

registry.category("user_menuitems").add("cpabooks_community_sidebar_default_menu", () => ({
    type: "item",
    id: "cpabooks_community_sidebar_default_menu",
    description: _t("Default menu"),
    callback: toggleDefaultMenu,
    sequence: 45,
}));
