/** @odoo-module **/
/**
 * Odoo 19 compatibility layer for CPABooks client actions written in the
 * Odoo 14 AbstractAction / Widget style (jQuery + QWeb string templates).
 *
 * - legacyAction(definition) builds a controller class from an
 *   AbstractAction.extend({...}) style object (init / willStart / start /
 *   events / template / _super are supported).
 * - registerLegacyAction(tag, Controller) wraps it in an OWL component and
 *   registers it as a client action.
 * - _ is a small underscore replacement for the helpers these files use.
 * - LegacyDialog mimics web.Dialog with the Odoo 19 dialog service.
 *
 * jQuery comes from the web._assets_jquery bundle included in the module
 * manifest (Odoo 19 no longer ships it in the backend by default).
 */
import { Component, markup, onMounted, onWillStart, onWillUnmount, useRef, xml } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { user } from "@web/core/user";
import { useService } from "@web/core/utils/hooks";
import { renderToString } from "@web/core/utils/render";
import { Dialog } from "@web/core/dialog/dialog";
import { loadBundle } from "@web/core/assets";

const $ = window.jQuery;

// Odoo 14 promises had guardedCatch(); keep legacy call sites working.
if (!Promise.prototype.guardedCatch) {
    // eslint-disable-next-line no-extend-native
    Promise.prototype.guardedCatch = function (onRejected) {
        return this.catch(onRejected);
    };
}

function callKw(params) {
    const kwargs = Object.assign({}, params.kwargs || {});
    if (params.context && !kwargs.context) {
        kwargs.context = params.context;
    }
    return rpc(`/web/dataset/call_kw/${params.model}/${params.method}`, {
        model: params.model,
        method: params.method,
        args: params.args || [],
        kwargs: Object.assign({ context: user.context }, kwargs),
    });
}

/** web.rpc replacement: rpc.query({model, method, args, kwargs} | {route, params}) */
export const legacyRpc = {
    query(params) {
        if (params.route) {
            return rpc(params.route, params.params || {});
        }
        return callKw(params);
    },
};

/** Load Chart.js (v4 in Odoo 19) once; resolves to the Chart class. */
export async function loadChartJs() {
    if (!window.Chart) {
        await loadBundle("web.chartjs_lib");
    }
    return window.Chart;
}

function convertAxis(axis) {
    const out = Object.assign({}, axis || {});
    const ticks = Object.assign({}, out.ticks || {});
    if (ticks.beginAtZero !== undefined) {
        out.beginAtZero = ticks.beginAtZero;
        delete ticks.beginAtZero;
    }
    if (ticks.fontColor) {
        ticks.color = ticks.fontColor;
        delete ticks.fontColor;
    }
    if (ticks.fontSize) {
        ticks.font = { size: ticks.fontSize };
        delete ticks.fontSize;
    }
    out.ticks = ticks;
    if (out.gridLines) {
        out.grid = Object.assign({}, out.gridLines);
        if (out.grid.zeroLineColor) {
            delete out.grid.zeroLineColor;
        }
        delete out.gridLines;
    }
    if (out.scaleLabel) {
        out.title = { display: !!out.scaleLabel.display, text: out.scaleLabel.labelString };
        delete out.scaleLabel;
    }
    delete out.id;
    return out;
}

/** Convert an Odoo 14 era Chart.js v2 config to Chart.js v4. */
export function chartV2ToV4(config) {
    const cfg = Object.assign({}, config);
    const options = Object.assign({}, cfg.options || {});
    if (cfg.type === "horizontalBar") {
        cfg.type = "bar";
        options.indexAxis = "y";
    }
    const plugins = Object.assign({}, options.plugins || {});
    if (options.legend) {
        const legend = Object.assign({}, options.legend);
        if (legend.labels && legend.labels.fontColor) {
            legend.labels = Object.assign({}, legend.labels, { color: legend.labels.fontColor });
            delete legend.labels.fontColor;
        }
        plugins.legend = legend;
        delete options.legend;
    }
    if (options.tooltips) {
        plugins.tooltip = options.tooltips;
        delete options.tooltips;
    }
    if (options.title && options.title.text !== undefined) {
        plugins.title = options.title;
        delete options.title;
    }
    options.plugins = plugins;
    if (options.scales && (options.scales.xAxes || options.scales.yAxes)) {
        const scales = {};
        if (options.scales.xAxes) {
            scales.x = convertAxis(options.scales.xAxes[0]);
        }
        if (options.scales.yAxes) {
            scales.y = convertAxis(options.scales.yAxes[0]);
        }
        options.scales = scales;
    }
    if (cfg.type === "pie" || cfg.type === "doughnut") {
        delete options.scales;
    }
    cfg.options = options;
    return cfg;
}

/** Services captured at web client start (for plain DOM scripts: shells, themes). */
export const shellBridge = { env: null, ready: [] };
registry.category("services").add(
    `cpa_legacy_bridge_${Math.random().toString(36).slice(2)}`,
    {
        dependencies: ["menu", "action"],
        start(env) {
            if (!shellBridge.env) {
                shellBridge.env = env;
                for (const cb of shellBridge.ready.splice(0)) {
                    cb(env);
                }
            }
            return {};
        },
    }
);

/** Open a menu by its xml id through the Odoo 19 menu service. */
export function openMenuByXmlid(xmlid) {
    const env = shellBridge.env;
    if (!env) {
        return false;
    }
    const menu = env.services.menu.getAll().find((m) => m.xmlid === xmlid);
    if (!menu) {
        return false;
    }
    env.services.menu.selectMenu(menu);
    return true;
}

/** xml id of the app currently open in the web client (or false). */
export function currentAppXmlid() {
    const env = shellBridge.env;
    const app = env && env.services.menu.getCurrentApp();
    return (app && app.xmlid) || false;
}

/** Run cb on web client UI updates (app switch, action load). */
export function onShellUpdate(cb) {
    const subscribe = (env) => {
        env.bus.addEventListener("MENUS:APP-CHANGED", () => cb());
        env.bus.addEventListener("ACTION_MANAGER:UI-UPDATED", () => cb());
    };
    if (shellBridge.env) {
        subscribe(shellBridge.env);
    } else {
        shellBridge.ready.push(subscribe);
    }
}

const ESCAPE = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#x27;", "`": "&#x60;" };

function toArray(list) {
    if (!list) {
        return [];
    }
    return Array.isArray(list) ? list : Object.values(list);
}

function iteratee(fn) {
    if (typeof fn === "function") {
        return fn;
    }
    if (typeof fn === "string") {
        return (item) => item && item[fn];
    }
    if (fn && typeof fn === "object") {
        return (item) => Object.entries(fn).every(([k, v]) => item && item[k] === v);
    }
    return (item) => item;
}

export const _ = {
    escape(value) {
        return String(value === undefined || value === null ? "" : value).replace(/[&<>"'`]/g, (c) => ESCAPE[c]);
    },
    each(list, fn, ctx) {
        if (!list) {
            return list;
        }
        if (Array.isArray(list)) {
            list.forEach((v, i) => fn.call(ctx, v, i, list));
        } else {
            Object.keys(list).forEach((k) => fn.call(ctx, list[k], k, list));
        }
        return list;
    },
    map(list, fn, ctx) {
        const f = iteratee(fn);
        if (list && !Array.isArray(list)) {
            return Object.keys(list).map((k) => f.call(ctx, list[k], k, list));
        }
        return toArray(list).map((v, i) => f.call(ctx, v, i, list));
    },
    find(list, fn, ctx) {
        const f = iteratee(fn);
        return toArray(list).find((v, i) => f.call(ctx, v, i));
    },
    filter(list, fn, ctx) {
        const f = iteratee(fn);
        return toArray(list).filter((v, i) => f.call(ctx, v, i));
    },
    some(list, fn, ctx) {
        const f = iteratee(fn);
        return toArray(list).some((v, i) => f.call(ctx, v, i));
    },
    every(list, fn, ctx) {
        const f = iteratee(fn);
        return toArray(list).every((v, i) => f.call(ctx, v, i));
    },
    sortBy(list, fn) {
        const f = iteratee(fn);
        return toArray(list)
            .map((v, i) => ({ v, i, k: f(v) }))
            .sort((a, b) => (a.k < b.k ? -1 : a.k > b.k ? 1 : a.i - b.i))
            .map((x) => x.v);
    },
    uniq(list) {
        return [...new Set(toArray(list))];
    },
    contains(list, value) {
        return toArray(list).includes(value);
    },
    extend(target, ...sources) {
        return Object.assign(target, ...sources);
    },
    isArray: Array.isArray,
    isNumber(v) {
        return typeof v === "number" && !Number.isNaN(v);
    },
    isEmpty(v) {
        if (v === null || v === undefined) {
            return true;
        }
        if (Array.isArray(v) || typeof v === "string") {
            return v.length === 0;
        }
        return Object.keys(v).length === 0;
    },
    keys: Object.keys,
    values: Object.values,
    debounce(fn, wait) {
        let timer;
        return function (...args) {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), wait);
        };
    },
};

/** core-like helpers: core._t, core.qweb.render */
export const core = {
    _t,
    qweb: {
        render(template, ctx) {
            return renderToString(template, ctx || {});
        },
    },
};

class HtmlDialog extends Component {
    static template = xml`
        <Dialog title="props.title" size="props.size">
            <div class="o_cpa_legacy_dialog" t-out="props.content"/>
            <t t-set-slot="footer">
                <t t-foreach="props.buttons" t-as="btn" t-key="btn_index">
                    <button type="button" t-att-class="btn.classes || 'btn btn-secondary'" t-on-click="() => this.onButton(btn)" t-esc="btn.text"/>
                </t>
                <button t-if="!props.buttons.length" type="button" class="btn btn-primary" t-on-click="props.close">Close</button>
            </t>
        </Dialog>`;
    static components = { Dialog };
    static props = ["*"];

    async onButton(btn) {
        if (btn.click) {
            await btn.click.call(this.props.legacy, { currentTarget: null });
        }
        if (btn.close) {
            this.props.close();
        }
    }
}

/** Minimal web.Dialog replacement: new LegacyDialog(parent, {title, $content, buttons, size}).open() */
export class LegacyDialog {
    constructor(parent, options) {
        this.parent = parent;
        this.options = options || {};
    }

    open() {
        const opts = this.options;
        let content = opts.$content;
        if (content && content.jquery) {
            content = content.prop("outerHTML") || content.html();
        }
        const dialog = this.parent && this.parent._services ? this.parent._services.dialog : null;
        const sizes = { large: "lg", extra_large: "xl", medium: "md", small: "sm" };
        if (!dialog) {
            return this;
        }
        this._close = dialog.add(HtmlDialog, {
            title: opts.title || "",
            size: sizes[opts.size] || "lg",
            content: markup(content || ""),
            buttons: opts.buttons || [],
            legacy: this,
        });
        return this;
    }

    close() {
        if (this._close) {
            this._close();
        }
    }
}

const BASE = {
    init(parent, action, options) {
        this.action = action || {};
        this.actionOptions = options || {};
    },
    willStart() {
        return Promise.resolve();
    },
    start() {
        return Promise.resolve();
    },
    destroy() {
        if (this.$el) {
            this.$el.off();
        }
    },
    getTitle() {
        return this.action && this.action.name;
    },
    on_attach_callback() {},
};

const HELPERS = {
    $(selector) {
        return this.$el.find(selector);
    },
    _rpc(params) {
        return legacyRpc.query(params);
    },
    set(key, value) {
        this[`_prop_${key}`] = value;
    },
    get(key) {
        return this[`_prop_${key}`];
    },
    do_action(action, options) {
        return this._services.action.doAction(action, options || {});
    },
    do_notify(title, message, sticky) {
        this._services.notification.add(message || title, { title: message ? title : undefined, sticky: !!sticky });
    },
    do_warn(title, message, sticky) {
        this._services.notification.add(message || title, {
            title: message ? title : undefined,
            type: "danger",
            sticky: !!sticky,
        });
    },
    trigger_up(name, data) {
        if (name === "menu_clicked" && data && data.action_id) {
            return this._services.menu.selectMenu(data.id);
        }
        if (name === "do_action" && data && data.action) {
            return this.do_action(data.action, data.options);
        }
    },
    userHasGroup(group) {
        return user.hasGroup(group);
    },
    renderElement() {
        let el;
        if (this.template) {
            const html = renderToString(this.template, { widget: this }).trim();
            el = $(html)[0] || document.createElement("div");
        } else if (this.contentTemplate) {
            // Odoo 14 contentTemplate: rendered inside .o_content
            el = document.createElement("div");
            el.className = "o_action o_content_wrapper h-100";
            const content = document.createElement("div");
            content.className = "o_content h-100 overflow-auto";
            content.innerHTML = renderToString(this.contentTemplate, { widget: this });
            el.appendChild(content);
        } else {
            el = document.createElement("div");
        }
        const old = this.el;
        this.el = el;
        this.$el = $(el);
        if (old && old.parentNode) {
            old.parentNode.replaceChild(el, old);
        }
        this._bindEvents();
    },
    _bindEvents() {
        const events = this.events || {};
        for (const [key, handler] of Object.entries(events)) {
            const idx = key.indexOf(" ");
            const evName = idx === -1 ? key : key.slice(0, idx);
            const selector = idx === -1 ? null : key.slice(idx + 1);
            const fn = typeof handler === "string" ? this[handler] : handler;
            if (!fn) {
                continue;
            }
            if (selector) {
                this.$el.on(evName, selector, fn.bind(this));
            } else {
                this.$el.on(evName, fn.bind(this));
            }
        }
    },
};

/** Build a controller class from an AbstractAction.extend({...}) definition. */
export function legacyAction(definition, Parent) {
    const parentProto = Parent ? Parent.prototype : null;
    class Controller extends (Parent || Object) {}
    if (!Parent) {
        Object.assign(Controller.prototype, BASE, HELPERS);
    }
    for (const [key, value] of Object.entries(definition)) {
        if (typeof value === "function" && /\b_super\b/.test(value.toString())) {
            const superFn = (parentProto && parentProto[key]) || BASE[key] || function () {};
            Controller.prototype[key] = function (...args) {
                const prev = this._super;
                this._super = superFn;
                try {
                    return value.apply(this, args);
                } finally {
                    this._super = prev;
                }
            };
        } else {
            Controller.prototype[key] = value;
        }
    }
    Controller.extend = (def) => legacyAction(def, Controller);
    return Controller;
}

export class LegacyActionWrapper extends Component {
    static template = xml`<div class="o_action o_cpa_legacy_action h-100 overflow-auto" t-ref="root"/>`;
    static props = ["*"];

    setup() {
        this.root = useRef("root");
        const Controller = this.constructor.Controller;
        const ctrl = (this.ctrl = new Controller());
        ctrl._services = {
            orm: useService("orm"),
            action: useService("action"),
            dialog: useService("dialog"),
            notification: useService("notification"),
            menu: useService("menu"),
        };
        ctrl._component = this;
        ctrl.env = this.env;
        ctrl.init(null, this.props.action, this.props.options || {});
        onWillStart(() => ctrl.willStart());
        onMounted(async () => {
            ctrl.renderElement();
            this.root.el.appendChild(ctrl.el);
            await ctrl.start();
            ctrl.on_attach_callback();
        });
        onWillUnmount(() => ctrl.destroy());
    }
}

export function registerLegacyAction(tag, Controller) {
    class Wrapper extends LegacyActionWrapper {
        static Controller = Controller;
    }
    registry.category("actions").add(tag, Wrapper, { force: true });
    return Wrapper;
}
