/** @odoo-module **/
/**
 * Readonly HTML for CAFM report tables (Monthly Billing, PPM grid, ...).
 * The server sends ready-made HTML (sometimes entity-encoded); render it as markup.
 */
import { Component, markup } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

function decodeHtmlMarkup(value) {
    value = value || "";
    if (value.indexOf("<div") !== -1 || value.indexOf("<table") !== -1) {
        return value;
    }
    if (value.indexOf("&lt;") === -1) {
        return value;
    }
    const textarea = document.createElement("textarea");
    textarea.innerHTML = value;
    return textarea.value;
}

export class CafmReadonlyHtml extends Component {
    static template = "cafm_cpa.CafmReadonlyHtml";
    static props = { ...standardFieldProps };

    get html() {
        return markup(decodeHtmlMarkup(String(this.props.record.data[this.props.name] || "")));
    }
}

registry.category("fields").add("cafm_readonly_html", {
    component: CafmReadonlyHtml,
    supportedTypes: ["html", "char", "text"],
});
