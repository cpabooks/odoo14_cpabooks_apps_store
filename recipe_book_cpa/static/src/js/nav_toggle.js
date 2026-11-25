/** @odoo-module **/
/**
 * Recipe Book: "Sidebar | Top bar" switch in the systray. In Sidebar mode the
 * Recipe Book menus are shown in a left sidebar while the Recipe Book app is
 * open. The choice is kept in the browser (localStorage).
 */
import { Component, useState } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { useBus, useService } from "@web/core/utils/hooks";

const STORAGE_KEY = "cpabooks_nav_mode";
const APP_XMLID = "recipe_book_cpa.menu_recipe_root";
const MODE_EVENT = "RECIPE_BOOK:NAV_MODE";

function getMode() {
    try {
        return browser.localStorage.getItem(STORAGE_KEY) || "top";
    } catch {
        return "top";
    }
}

function setMode(mode) {
    try {
        browser.localStorage.setItem(STORAGE_KEY, mode);
    } catch {
        // ignore (private window)
    }
}

function bySequence(menus) {
    return [...(menus || [])].sort((a, b) => (a.sequence || 0) - (b.sequence || 0));
}

function useRecipeNav(component) {
    const menu = useService("menu");
    const state = useState({ mode: getMode(), inRecipe: false, activeMenuId: false });
    const refresh = () => {
        const app = menu.getCurrentApp();
        state.inRecipe = Boolean(app && app.xmlid === APP_XMLID);
        state.mode = getMode();
        const show = state.mode === "side" && state.inRecipe;
        document.body.classList.toggle("o_cpa_nav_side", show);
    };
    useBus(component.env.bus, "MENUS:APP-CHANGED", refresh);
    useBus(component.env.bus, MODE_EVENT, refresh);
    refresh();
    return { menu, state, refresh };
}

export class RecipeNavToggle extends Component {
    static template = "recipe_book_cpa.RecipeNavToggle";
    static props = {};

    setup() {
        this.nav = useRecipeNav(this);
    }

    apply(mode) {
        setMode(mode);
        this.env.bus.trigger(MODE_EVENT);
    }
}

export class RecipeAppSidebar extends Component {
    static template = "recipe_book_cpa.RecipeAppSidebar";
    static props = {};

    setup() {
        this.nav = useRecipeNav(this);
    }

    get visible() {
        return this.nav.state.mode === "side" && this.nav.state.inRecipe;
    }

    get sections() {
        const app = this.nav.menu.getApps().find((a) => a.xmlid === APP_XMLID);
        if (!app) {
            return [];
        }
        const tree = this.nav.menu.getMenuAsTree(app.id);
        const kids = bySequence(tree.childrenTree);
        const find = (xmlid) => kids.find((m) => m.xmlid === xmlid);
        const dashboard = find("recipe_book_cpa.menu_dashboard");
        const daily = find("recipe_book_cpa.menu_daily_reports");
        const stock = find("recipe_book_cpa.menu_daily_closing_stock");
        const rest = kids.filter((m) => m !== dashboard && m !== daily && m !== stock);
        const sections = [];
        sections.push({ key: "home", label: "Home", tone: "home", items: dashboard ? [{ menu: dashboard, tier: "main" }] : [] });
        const book = { key: "book", label: "Recipe Book", tone: "book", items: [] };
        sections.push(book);
        for (const menu of rest) {
            if (menu.childrenTree && menu.childrenTree.length) {
                sections.push({
                    key: `cfg_${menu.id}`,
                    label: menu.name,
                    tone: "config",
                    items: bySequence(menu.childrenTree).map((child) => ({ menu: child, tier: "sub" })),
                });
            } else {
                book.items.push({ menu, tier: "sub" });
            }
        }
        sections.push({
            key: "stock",
            label: "Daily Closing Stock",
            tone: "stock",
            items: bySequence(stock && stock.childrenTree).map((child) => ({ menu: child, tier: "sub" })),
        });
        const dailyItems = [];
        const dailySections = [];
        for (const child of bySequence(daily && daily.childrenTree)) {
            if (child.childrenTree && child.childrenTree.length) {
                dailySections.push({
                    key: `daily_${child.id}`,
                    label: child.name,
                    tone: "daily",
                    items: bySequence(child.childrenTree).map((leaf) => ({ menu: leaf, tier: "sub" })),
                });
            } else {
                dailyItems.push({ menu: child, tier: "sub" });
            }
        }
        sections.push({ key: "daily", label: "Daily Reports", tone: "daily", items: dailyItems });
        sections.push(...dailySections);
        return sections.map((s) => ({ ...s, items: s.items.filter((i) => i.menu.actionID) }));
    }

    open(menu) {
        this.nav.state.activeMenuId = menu.id;
        this.nav.menu.selectMenu(menu);
    }
}

registry.category("systray").add("recipe_book_cpa.nav_toggle", { Component: RecipeNavToggle }, { sequence: 200 });
registry.category("main_components").add("recipe_book_cpa.app_sidebar", { Component: RecipeAppSidebar });
