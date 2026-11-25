/** @odoo-module **/
/**
 * Complaint Registration Management (CRN / Field Service) app shell, Odoo 19.
 *
 * Odoo 14 wrapped each action's .o_content in a layout with a left sidebar.
 * In Odoo 19 the sidebar is one fixed OWL component (main_components) and the
 * action area is shifted with CSS (body.o_crn_app_shell). Sidebar entries whose
 * action is not installed (Enterprise industry_fsm, optional CPABooks apps)
 * are hidden. AppShell keeps the API used by the CRN client actions.
 */
import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { user } from "@web/core/user";
import { useBus, useService } from "@web/core/utils/hooks";
import { _ } from "@field_service_cpa/js/legacy_compat";

const $ = window.jQuery;

var SHELL_CLASS = 'o_crn_app_shell';
var MAIN_MENU_CLASS = 'o_crn_show_main_menu';
var FSM_ROOT_XMLID = 'field_service_cpa.menu_fsm_root';

var NAV_ITEMS = [
    {section: 'Home', sectionClass: 'o_crn_section_home', items: [
        {key: 'dashboard', label: 'Dashboard', xmlid: 'field_service_cpa.action_crn_service_dashboard', tier: 'home'},
        {key: 'processing_cycle', label: 'CRN Processing Cycle', xmlid: 'field_service_cpa.action_crn_processing_cycle', tier: 'home'},
    ]},
    {section: 'CRNs', sectionClass: 'o_crn_section_crns', items: [
        {key: 'my_crns', label: 'My CRNs', xmlid: 'industry_fsm.project_task_action_fsm'},
        {key: 'all_crns', label: 'All CRNs', xmlid: 'industry_fsm.project_task_action_all_fsm'},
        {key: 'crn_map', label: 'CRN Map', xmlid: 'industry_fsm.project_task_action_fsm_map'},
        {key: 'to_quotation', label: 'To Quotation / Issue', xmlid: 'field_service_cpa.action_fsm_project_task_to_quotation_issue'},
        {key: 'to_invoice', label: 'To Invoice', xmlid: 'field_service_cpa.action_fsm_project_task_to_invoice'},
    ]},
    {section: 'Reporting', sectionClass: 'o_crn_section_reporting', items: [
        {key: 'service_dashboard', label: 'Service Charts Dashboard', xmlid: 'field_service_cpa.action_fsm_service_monitor_dashboard'},
        {key: 'task_analysis', label: 'CRN Analysis', xmlid: 'field_service_cpa.action_fsm_task_analysis_monitor'},
        {key: 'timesheet_analysis', label: 'Timesheet Analysis', xmlid: 'field_service_cpa.action_fsm_timesheet_analysis_monitor'},
        {key: 'material_consumption', label: 'Material Consumption Analysis', xmlid: 'field_service_cpa.action_fsm_material_consumption_analysis'},
    ]},
    {section: 'Approvals', sectionClass: 'o_crn_section_approvals', items: [
        {key: 'approval_waiting', label: 'CRN Waiting for Approval', xmlid: 'cpabooks_approval.action_crn_followup_waiting'},
        {key: 'approval_approved', label: 'Approved CRNs', xmlid: 'cpabooks_approval.action_crn_followup_approved'},
        {key: 'approval_rejected', label: 'Rejected CRNs', xmlid: 'cpabooks_approval.action_crn_followup_rejected'},
    ]},
    {section: 'Store', sectionClass: 'o_crn_section_store', items: [
        {key: 'stock_issue', label: 'Material Issue Note', xmlid: 'cpabooks_project_issue_note.issue_action'},
        {key: 'stock_return', label: 'Material Return Note', xmlid: 'cpabooks_project_issue_note.return_issue_action'},
        {key: 'mat_request', label: 'Material Request Pending', xmlid: 'field_service_cpa.action_fsm_store_material_request_pending'},
        {key: 'mat_issued', label: 'Material Issued', xmlid: 'field_service_cpa.action_fsm_store_material_issued'},
        {key: 'do_pending', label: 'DO Pending', xmlid: 'field_service_cpa.action_fsm_store_do_pending'},
        {key: 'do_issued', label: 'DO Issued', xmlid: 'field_service_cpa.action_fsm_store_do_issued'},
    ]},
    {section: 'Timesheets', sectionClass: 'o_crn_section_timesheet', items: [
        {key: 'timesheet_mine', label: 'My Timesheets', xmlid: 'hr_timesheet.act_hr_timesheet_line'},
        {key: 'timesheet_all', label: 'All Timesheets', xmlid: 'hr_timesheet.timesheet_action_all'},
    ]},
    {section: 'Settings', sectionClass: 'o_crn_section_settings', items: [
        {key: 'test_data', label: 'FSM Test Data', xmlid: 'field_service_cpa.action_fsm_test_data_wizard', admin_only: true},
        {key: 'all_apps', label: 'All Odoo Apps', special: 'open_app_menu'},
    ]},
];

var XMLID_TO_KEY = {};
_.each(NAV_ITEMS, function (block) {
    _.each(block.items, function (item) {
        if (item.xmlid) {
            XMLID_TO_KEY[item.xmlid] = item.key;
        }
    });
});

function filterNavItems(options) {
    options = options || {};
    var isAdmin = !!options.isSystemAdmin;
    return _.map(NAV_ITEMS, function (block) {
        var items = _.filter(block.items, function (item) {
            return !item.admin_only || isAdmin;
        });
        if (!items.length) {
            return null;
        }
        return _.extend({}, block, {items: items});
    }).filter(Boolean);
}

function getActionContext(action) {
    var ctx = action && action.context;
    if (!ctx) {
        return {};
    }
    if (typeof ctx === 'string') {
        if (ctx.indexOf('fsm_mode') !== -1 || ctx.indexOf('default_is_fsm') !== -1 ||
                ctx.indexOf('default_check_fsm') !== -1) {
            return {fsm_mode: true};
        }
        return {};
    }
    return ctx;
}

function activeKeyFromAction(action) {
    if (!action) {
        return 'dashboard';
    }
    if (action.tag === 'crn_processing_cycle') {
        return 'processing_cycle';
    }
    if (action.tag === 'crn_service_dashboard') {
        return 'dashboard';
    }
    if (action.xml_id && XMLID_TO_KEY[action.xml_id]) {
        return XMLID_TO_KEY[action.xml_id];
    }
    if (action.res_model === 'project.task') {
        var name = String(action.name || '').toLowerCase();
        if (name.indexOf('my crn') !== -1) {
            return 'my_crns';
        }
        return 'all_crns';
    }
    if (action.res_model === 'material.request.line') {
        return 'mat_request';
    }
    if (action.res_model === 'stock.picking') {
        var domainStr = JSON.stringify(action.domain || []);
        var actName = String(action.name || '').toLowerCase();
        if (domainStr.indexOf('is_stock_return_note') !== -1 || actName.indexOf('return') !== -1) {
            return 'stock_return';
        }
        if (domainStr.indexOf('is_stock_issue_note') !== -1 || actName.indexOf('issue note') !== -1) {
            return 'stock_issue';
        }
        if (domainStr.indexOf('outgoing') !== -1 || actName.indexOf('do pending') !== -1 || actName.indexOf('do issued') !== -1) {
            if (actName.indexOf('issued') !== -1 || actName.indexOf('done') !== -1) {
                return 'do_issued';
            }
            return 'do_pending';
        }
        return 'mat_issued';
    }
    if (action.res_model === 'account.analytic.line') {
        return 'timesheet_analysis';
    }
    if (action.tag === 'fsm_service_monitor_dashboard') {
        return 'service_dashboard';
    }
    if (action.res_model === 'cpabooks.fsm.test.data.wizard') {
        return 'test_data';
    }
    if (action.res_model === 'fsm.material.consumption.report') {
        return 'material_consumption';
    }
    if (action.name && String(action.name).toLowerCase().indexOf('waiting for approval') !== -1) {
        return 'approval_waiting';
    }
    if (action.name && String(action.name).toLowerCase().indexOf('approved crn') !== -1) {
        return 'approval_approved';
    }
    if (action.name && String(action.name).toLowerCase().indexOf('rejected crn') !== -1) {
        return 'approval_rejected';
    }
    return 'dashboard';
}

/**
 * True for Field Service / CRN screens that should use the left app shell.
 * Does not require global Settings → Menu layout = crm_fsm.
 */
function isFsmShellAction(action) {
    if (!action) {
        return false;
    }
    if (action.tag === 'crn_service_dashboard' || action.tag === 'crn_processing_cycle' ||
            action.tag === 'fsm_service_monitor_dashboard') {
        return true;
    }
    if (action.xml_id && XMLID_TO_KEY[action.xml_id]) {
        return true;
    }
    var ctx = getActionContext(action);
    if (ctx.fsm_mode || ctx.default_is_fsm || ctx.default_check_fsm) {
        return true;
    }
    if (action.res_model === 'material.request.line' ||
            action.res_model === 'crn.service.dashboard' ||
            action.res_model === 'cpabooks.fsm.test.data.wizard' ||
            action.res_model === 'fsm.material.consumption.report') {
        return true;
    }
    if (action.res_model === 'project.task') {
        var name = String(action.name || '').toLowerCase();
        if (name.indexOf('crn') !== -1 || name.indexOf('field service') !== -1) {
            return true;
        }
        var domainStr = JSON.stringify(action.domain || []);
        if (domainStr.indexOf('is_fsm') !== -1 || domainStr.indexOf('check_fsm') !== -1 ||
                domainStr.indexOf('CRN') !== -1) {
            return true;
        }
    }
    if (action.name && String(action.name).toLowerCase().indexOf('waiting for approval') !== -1) {
        return true;
    }
    if (action.name && String(action.name).toLowerCase().indexOf('approved crn') !== -1) {
        return true;
    }
    if (action.name && String(action.name).toLowerCase().indexOf('rejected crn') !== -1) {
        return true;
    }
    return false;
}


function openAppsMenu() {
    const toggle = document.querySelector(
        ".o_navbar_apps_menu button, .o_navbar_apps_menu .dropdown-toggle, .o_main_navbar .o_menu_toggle"
    );
    if (toggle) {
        toggle.click();
    }
    return Promise.resolve();
}

export const AppShell = {
    SHELL_CLASS: SHELL_CLASS,
    MAIN_MENU_CLASS: MAIN_MENU_CLASS,
    NAV_ITEMS: NAV_ITEMS,
    activate() {
        document.body.classList.add(SHELL_CLASS);
        document.body.classList.remove(MAIN_MENU_CLASS);
    },
    showMainMenuBar() {
        document.body.classList.remove(MAIN_MENU_CLASS);
    },
    hideMainMenuBar() {
        document.body.classList.remove(MAIN_MENU_CLASS);
    },
    openMainMenu: openAppsMenu,
    deactivate() {
        document.body.classList.remove(SHELL_CLASS, MAIN_MENU_CLASS);
    },
    isCrmSidebarMode() {
        return true;
    },
    isNativeBackendScreen(action) {
        return action && action.res_model === "res.config.settings";
    },
    isFsmShellAction: isFsmShellAction,
    activeKeyFromAction: activeKeyFromAction,
    setSidebarActive() {},
    // Global sidebar component in Odoo 19: nothing to mount per action.
    mountSidebar() {
        return $();
    },
    wrapActionContent($content) {
        return $content || $();
    },
    getSidebarOptions() {
        return Promise.resolve({ isSystemAdmin: user.isSystem });
    },
    listFirstOptions(options) {
        return options || {};
    },
    ensureTreeViewFirst(action) {
        return action;
    },
};

export class CrnShellSidebar extends Component {
    static template = "field_service_cpa.CrnShellSidebar";
    static props = {};

    setup() {
        this.menu = useService("menu");
        this.actionService = useService("action");
        this.orm = useService("orm");
        this.state = useState({ active: false, activeKey: "dashboard", available: null });
        const sync = () => this.sync();
        useBus(this.env.bus, "ACTION_MANAGER:UI-UPDATED", sync);
        useBus(this.env.bus, "MENUS:APP-CHANGED", sync);
        onWillStart(async () => {
            const xmlids = [];
            for (const block of NAV_ITEMS) {
                for (const item of block.items) {
                    if (item.xmlid) {
                        xmlids.push(item.xmlid);
                    }
                }
            }
            try {
                this.state.available = await this.orm.call("project.task", "crn_shell_existing_xmlids", [xmlids]);
            } catch {
                this.state.available = xmlids;
            }
        });
        sync();
    }

    get blocks() {
        const available = new Set(this.state.available || []);
        return filterNavItems({ isSystemAdmin: user.isSystem })
            .map((block) => ({
                ...block,
                items: block.items.filter((item) => !item.xmlid || available.has(item.xmlid)),
            }))
            .filter((block) => block.items.length);
    }

    sync() {
        const app = this.menu.getCurrentApp();
        const controller = this.actionService.currentController;
        const action = controller && controller.action;
        let active;
        if (action && action.res_model === "res.config.settings") {
            active = false;
        } else if (app) {
            active = app.xmlid === FSM_ROOT_XMLID;
        } else {
            active = Boolean(action && ["crn_service_dashboard", "crn_processing_cycle"].includes(action.tag));
        }
        this.state.active = active;
        this.state.activeKey = activeKeyFromAction(action);
        if (active) {
            AppShell.activate();
        } else {
            AppShell.deactivate();
        }
    }

    itemClass(block, item) {
        const main = block.sectionClass === "o_crn_section_home";
        return {
            "list-group-item": true,
            o_crn_app_sidebar_item_main: main,
            o_crn_app_sidebar_item_sub: !main,
            active: item.key === this.state.activeKey,
        };
    }

    async onItem(item) {
        if (item.special === "open_app_menu") {
            return openAppsMenu();
        }
        if (item.xmlid) {
            this.state.activeKey = item.key;
            await this.actionService.doAction(item.xmlid, { clearBreadcrumbs: true });
        }
    }
}

registry.category("main_components").add("field_service_cpa.crn_shell_sidebar", {
    Component: CrnShellSidebar,
});

export default AppShell;
