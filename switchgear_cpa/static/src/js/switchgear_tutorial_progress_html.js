/** @odoo-module **/
/** Render the tutorial wizard progress HTML (decode escaped markup). */
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

export class SgTutorialProgressHtml extends Component {
    static template = "switchgear_cpa.SgTutorialProgressHtml";
    static props = { ...standardFieldProps };

    get html() {
        return markup(decodeEntities(this.props.record.data[this.props.name] || ""));
    }
}

registry.category("fields").add("sg_tutorial_progress_html", {
    component: SgTutorialProgressHtml,
    supportedTypes: ["html", "char", "text"],
});
