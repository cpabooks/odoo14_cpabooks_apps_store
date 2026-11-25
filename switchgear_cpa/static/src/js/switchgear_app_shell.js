/** @odoo-module **/
/**
 * Switchgear app shell (Odoo 19).
 *
 * Odoo 14 wrapped every action's .o_content in a layout with a left sidebar.
 * Moving OWL-rendered DOM is unsafe in Odoo 19, so the sidebar is now one
 * fixed OWL component (registry main_components) and the action area is
 * shifted with CSS (body.o_switchgear_app_shell). The public AppShell API is
 * kept for the Switchgear client actions; mountSidebar / wrapActionContent
 * are no-ops because the sidebar is global.
 */
import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { user } from "@web/core/user";
import { useBus, useService } from "@web/core/utils/hooks";
import { _ } from "@switchgear_cpa/js/legacy_compat";

const $ = window.jQuery;
const ROOT_MENU_XMLID = "switchgear_cpa.menu_flowchart_kanban_root";

var SHELL_CLASS = 'o_switchgear_app_shell';
var MAIN_MENU_CLASS = 'o_switchgear_show_main_menu';

var NAV_ITEMS = [
    {section: 'Home', sectionClass: 'o_switchgear_section_home', items: [
        {key: 'dashboard', label: 'Dashboard', xmlid: 'switchgear_cpa.action_switchgear_dashboard'},
        {key: 'tutorial', label: 'Tutorial Wizard', xmlid: 'switchgear_cpa.action_switchgear_tutorial_wizard'},
        {key: 'processing_cycle', label: 'CPA Switchgear processing cycle', xmlid: 'switchgear_cpa.action_switchgear_processing_cycle'},
        {key: 'flowchart', label: 'Process Flowchart', xmlid: 'switchgear_cpa.action_flowchart_kanban'},
        {key: 'main_menu', label: 'Apps Home', special: 'open_app_menu'},
    ]},
    {section: 'CRM', sectionClass: 'o_switchgear_section_crm', items: [
        {key: 'enquiry', label: 'Pipeline (Opportunities)', xmlid: 'crm.crm_lead_action_pipeline'},
        {key: 'crm_leads', label: 'Leads', xmlid: 'crm.crm_lead_all_leads'},
        {key: 'estimation', label: 'Estimation', xmlid: 'switchgear_cpa.action_job_estimate'},
        {key: 'quotation', label: 'Quotation (Sales)', xmlid: 'sale.action_quotations_with_onboarding'},
    ]},
    {section: 'Manufacturing', sectionClass: 'o_switchgear_section_manufacturing', items: [
        {key: 'mrp_order', label: 'Manufacturing Orders', xmlid: 'mrp.mrp_production_action'},
        {key: 'mrp_workorders', label: 'Work Orders', xmlid: 'mrp.mrp_workorder_todo'},
        {key: 'bom', label: 'Bills of Materials', xmlid: 'mrp.mrp_bom_form_action'},
        {key: 'design', label: 'Design (Documents)', xmlid: 'switchgear_cpa.action_switchgear_design_document'},
        {key: 'purchase_req', label: 'Purchase Requisition', xmlid: 'switchgear_cpa.action_material_purchase_requisition'},
    ]},
    {section: 'Inventory', sectionClass: 'o_switchgear_section_inventory', items: [
        {key: 'stock_check', label: 'Operations Overview', xmlid: 'stock.stock_picking_type_action'},
        {key: 'stock_transfers', label: 'Transfers', xmlid: 'stock.action_picking_tree_all'},
        {key: 'grn', label: 'Receipts (GRN)', xmlid: 'switchgear_cpa.action_switchgear_stock_incoming'},
        {key: 'delivery', label: 'Delivery Orders', xmlid: 'switchgear_cpa.action_switchgear_stock_outgoing'},
        {key: 'stock_adjustments', label: 'Inventory Adjustments', xmlid: 'stock.action_view_inventory_tree'},
        {key: 'stock_replenish', label: 'Reordering Rules', xmlid: 'stock.action_orderpoint'},
        {key: 'stock_products', label: 'Products', xmlid: 'stock.product_template_action_product'},
        {key: 'inv_valuation_live', label: 'Inventory Valuation — Live', xmlid: 'stock.action_view_quants'},
        {key: 'lpo_purchase', label: 'Purchase (LPO / RFQ)', xmlid: 'purchase.purchase_rfq'},
    ]},
    {section: 'Quality', sectionClass: 'o_switchgear_section_quality', items: [
        {key: 'quality', label: 'Quality Overview', xmlid: 'switchgear_cpa.quality_alert_team_action'},
        {key: 'quality_checks', label: 'Quality Checks', xmlid: 'switchgear_cpa.quality_check_action_main'},
        {key: 'quality_alerts', label: 'Quality Alerts', xmlid: 'switchgear_cpa.quality_alert_action'},
        {key: 'quality_points', label: 'Control Points', xmlid: 'switchgear_cpa.quality_point_action'},
    ]},
    {section: 'Timesheet', sectionClass: 'o_switchgear_section_timesheet', items: [
        {key: 'timesheet_mine', label: 'My Timesheets', xmlid: 'hr_timesheet.act_hr_timesheet_line'},
        {key: 'timesheet_all', label: 'All Timesheets', xmlid: 'hr_timesheet.timesheet_action_all'},
        {key: 'timesheet_report', label: 'Timesheet Analysis', xmlid: 'hr_timesheet.act_hr_timesheet_report'},
    ]},
    {section: 'Employees', sectionClass: 'o_switchgear_section_employees', items: [
        {key: 'hr_employees', label: 'Employees', xmlid: 'hr.open_view_employee_list_my'},
        {key: 'hr_directory', label: 'Employee Directory', xmlid: 'hr.hr_employee_public_action'},
        {key: 'hr_departments', label: 'Departments', xmlid: 'hr.hr_department_tree_action'},
        {key: 'hr_jobs', label: 'Job Positions', xmlid: 'hr.action_hr_job'},
    ]},
    {section: 'Projects', sectionClass: 'o_switchgear_section_projects', items: [
        {key: 'project_list', label: 'Project List', xmlid: 'switchgear_cpa.action_switchgear_project_list'},
        {key: 'tasks_by_client', label: 'Tasks by Customer', xmlid: 'switchgear_cpa.action_switchgear_tasks_by_client'},
    ]},
    {section: 'Activities', sectionClass: 'o_switchgear_section_activities', items: [
        {key: 'all_activities', label: 'Activities', xmlid: 'mail.mail_activity_action'},
        {key: 'my_tasks', label: 'Tasks', xmlid: 'project.action_view_all_task'},
    ]},
    {section: 'Accounting', sectionClass: 'o_switchgear_section_accounting', items: [
        {key: 'tax_invoice', label: 'Tax Invoice', xmlid: 'account.action_move_out_invoice_type'},
        {key: 'customer_payment', label: 'Customer Payment Receipt', xmlid: 'account.action_account_payments'},
        {key: 'vendor_bill', label: 'Bills Entry', xmlid: 'account.action_move_in_invoice_type'},
        {key: 'vendor_payment', label: 'Vendor Payment', xmlid: 'account.action_account_payments_payable'},
    ]},
    {section: 'Settings', sectionClass: 'o_switchgear_section_settings', items: [
        {
            key: 'configuration',
            label: 'Configuration',
            xmlid: 'switchgear_cpa.action_switchgear_configuration',
            admin_only: true,
        },
    ]},
];

var XMLID_TO_KEY = {};
var SWITCHGEAR_RES_MODELS = {
    'flowchart.kanban': true,
    'crm.lead': true,
    'job.estimate': true,
    'sale.order': true,
    'mrp.bom': true,
    'mrp.production': true,
    'mrp.workorder': true,
    'stock.picking': true,
    'stock.picking.type': true,
    'stock.warehouse.orderpoint': true,
    'stock.inventory': true,
    'purchase.order': true,
    'account.move': true,
    'account.payment': true,
    'switchgear.design.document': true,
    'material.purchase.requisition': true,
    'quality.alert': true,
    'quality.alert.team': true,
    'quality.check': true,
    'quality.point': true,
    'hr.employee': true,
    'hr.employee.public': true,
    'hr.department': true,
    'hr.job': true,
    'hr.payslip': true,
    'hr.payslip.run': true,
    'account.analytic.line': true,
    'product.template': true,
    'switchgear.dashboard': true,
    'switchgear.tutorial.wizard': true,
    'project.project': true,
    'project.task': true,
    'mail.activity': true,
    'cpa.issue': true,
};

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

function findNavItemByKey(navKey) {
    var found = null;
    _.each(NAV_ITEMS, function (block) {
        _.each(block.items, function (item) {
            if (!found && item.key === navKey) {
                found = item;
            }
        });
    });
    return found;
}

function activeKeyFromAction(action) {
    if (!action) {
        return 'dashboard';
    }
    if (action.tag === 'switchgear_processing_cycle') {
        return 'processing_cycle';
    }
    if (action.tag === 'switchgear_dashboard' || action.tag === 'switchgear_flowchart') {
        return 'dashboard';
    }
    if (action.xml_id === 'switchgear_cpa.action_flowchart_kanban' ||
            action.res_model === 'flowchart.kanban') {
        return 'flowchart';
    }
    if (action.xml_id && XMLID_TO_KEY[action.xml_id]) {
        return XMLID_TO_KEY[action.xml_id];
    }
    if (action.res_model === 'switchgear.tutorial.wizard') {
        return 'tutorial';
    }
    if (action.res_model === 'job.estimate') {
        return 'estimation';
    }
    if (action.res_model === 'crm.lead') {
        return 'enquiry';
    }
    if (action.res_model === 'sale.order') {
        return 'quotation';
    }
    if (action.res_model === 'mrp.bom') {
        return 'bom';
    }
    if (action.res_model === 'mrp.production') {
        return 'mrp_order';
    }
    if (action.res_model === 'mrp.workorder') {
        return 'mrp_workorders';
    }
    if (action.res_model === 'purchase.order') {
        return 'lpo_purchase';
    }
    if (action.res_model === 'stock.picking') {
        var domain = action.domain || [];
        var domainStr = JSON.stringify(domain);
        if (domainStr.indexOf('incoming') !== -1) {
            return 'grn';
        }
        if (domainStr.indexOf('outgoing') !== -1) {
            return 'delivery';
        }
        return 'stock_transfers';
    }
    if (action.res_model === 'stock.picking.type') {
        return 'stock_check';
    }
    if (action.res_model === 'account.move') {
        if (action.name && String(action.name).toLowerCase().indexOf('bill') !== -1) {
            return 'vendor_bill';
        }
        return 'tax_invoice';
    }
    if (action.res_model === 'account.payment') {
        return action.name && String(action.name).toLowerCase().indexOf('vendor') !== -1 ?
            'vendor_payment' : 'customer_payment';
    }
    if (action.res_model === 'switchgear.design.document') {
        return 'design';
    }
    if (action.res_model === 'quality.check') {
        return 'quality_checks';
    }
    if (action.res_model === 'quality.alert') {
        return 'quality_alerts';
    }
    if (action.res_model === 'quality.point') {
        return 'quality_points';
    }
    if (action.res_model === 'quality.alert.team') {
        return 'quality';
    }
    if (action.res_model === 'hr.employee' || action.res_model === 'hr.employee.public') {
        return 'hr_employees';
    }
    if (action.res_model === 'hr.department') {
        return 'hr_departments';
    }
    if (action.res_model === 'hr.job') {
        return 'hr_jobs';
    }
    if (action.res_model === 'hr.payslip') {
        return 'payroll_payslips';
    }
    if (action.res_model === 'hr.payslip.run') {
        return 'payroll_batches';
    }
    if (action.res_model === 'account.analytic.line') {
        return 'timesheet_mine';
    }
    if (action.res_model === 'product.template') {
        return 'stock_products';
    }
    if (action.res_model === 'stock.warehouse.orderpoint') {
        return 'stock_replenish';
    }
    if (action.res_model === 'stock.inventory') {
        return 'stock_adjustments';
    }
    if (action.res_model === 'mail.activity') {
        if (action.xml_id && XMLID_TO_KEY[action.xml_id]) {
            return XMLID_TO_KEY[action.xml_id];
        }
        return 'all_activities';
    }
    if (action.tag === 'activity_dashboard' || action.tag === 'activity_dashboard_new') {
        return 'activity_dashboard';
    }
    if (action.res_model === 'cpabooks.demo.config') {
        return 'configuration';
    }
    if (action.xml_id === 'switchgear_cpa.action_switchgear_configuration') {
        return 'configuration';
    }
    return 'dashboard';
}

function isSwitchgearAction(action) {
    if (!action) {
        return false;
    }
    if (action.tag === 'switchgear_dashboard' || action.tag === 'switchgear_flowchart' ||
            action.tag === 'switchgear_processing_cycle') {
        return true;
    }
    if (action.xml_id && XMLID_TO_KEY[action.xml_id]) {
        return true;
    }
    if (action.res_model && SWITCHGEAR_RES_MODELS[action.res_model]) {
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
    isSwitchgearAction: isSwitchgearAction,
    activeKeyFromAction: activeKeyFromAction,
    findNavItemByKey: findNavItemByKey,
    setSidebarActive() {},
    // The sidebar is the global SwitchgearShellSidebar component in Odoo 19.
    mountSidebar() {
        return $();
    },
    wrapActionContent($content) {
        return $content || $();
    },
    getSidebarOptions() {
        return Promise.resolve({ isSystemAdmin: user.isSystem });
    },
    isDefaultOdooMode() {
        return false;
    },
    isSwitchgearSidebarMode() {
        return true;
    },
    isNativeBackendScreen(action) {
        return action && action.res_model === "res.config.settings";
    },
};

export class SwitchgearShellSidebar extends Component {
    static template = "switchgear_cpa.SwitchgearShellSidebar";
    static props = {};

    setup() {
        this.menu = useService("menu");
        this.actionService = useService("action");
        this.state = useState({ active: false, activeKey: "dashboard" });
        const sync = () => this.sync();
        useBus(this.env.bus, "ACTION_MANAGER:UI-UPDATED", sync);
        useBus(this.env.bus, "MENUS:APP-CHANGED", sync);
        sync();
    }

    get blocks() {
        return filterNavItems({ isSystemAdmin: user.isSystem });
    }

    currentAction() {
        const controller = this.actionService.currentController;
        return controller && controller.action;
    }

    sync() {
        const app = this.menu.getCurrentApp();
        const action = this.currentAction();
        let active;
        if (action && action.res_model === "res.config.settings") {
            active = false;
        } else if (app) {
            active = app.xmlid === ROOT_MENU_XMLID;
        } else {
            active = Boolean(action && (action.tag || "").startsWith("switchgear_"));
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
        const main = block.sectionClass === "o_switchgear_section_home";
        return {
            "list-group-item": true,
            o_switchgear_app_sidebar_item_main: main,
            o_switchgear_app_sidebar_item_sub: !main,
            active: item.key === this.state.activeKey,
        };
    }

    async onItem(item) {
        if (item.special === "open_app_menu") {
            return openAppsMenu();
        }
        if (item.xmlid) {
            this.state.activeKey = item.key;
            try {
                await this.actionService.doAction(item.xmlid, { clearBreadcrumbs: true });
            } catch (e) {
                console.warn("Switchgear sidebar: cannot open", item.xmlid, e);
            }
        }
    }
}

registry.category("main_components").add("switchgear_cpa.shell_sidebar", {
    Component: SwitchgearShellSidebar,
});

export default AppShell;
