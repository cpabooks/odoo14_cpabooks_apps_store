/** @odoo-module **/
/**
 * Read-only HTML progress block of the FAFF job wizard. The server sends the
 * HTML (sometimes entity-encoded); it is decoded and rendered as markup.
 */
import { Component, markup } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

function decodeEntities(value) {
    if (!value) {
        return "";
    }
    const text = String(value);
    if (text.indexOf("&lt;") === -1 && text.indexOf("&#") === -1) {
        return text;
    }
    const textarea = document.createElement("textarea");
    textarea.innerHTML = text;
    return textarea.value;
}

export class FaffWizardProgressHtml extends Component {
    static template = "faff_cpa.FaffWizardProgressHtml";
    static props = { ...standardFieldProps };

    get html() {
        return markup(decodeEntities(this.props.record.data[this.props.name] || ""));
    }
}

registry.category("fields").add("faff_wizard_progress_html", {
    component: FaffWizardProgressHtml,
    supportedTypes: ["html", "char", "text"],
});
