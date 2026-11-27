/** @odoo-module **/
/**
 * "Labour Supply Invoice | Construction Invoice" switch on customer invoices
 * and credit notes. It edits the is_construction_invoice field; the server
 * keeps the invoice lines in sync (see account_move.py).
 */
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class ContractingInvoiceKindToggle extends Component {
    static template = "cpabooks_contracting_invoice.InvoiceKindToggle";
    static props = { ...standardFieldProps };

    get isConstruction() {
        return Boolean(this.props.record.data[this.props.name]);
    }

    async setKind(isConstruction) {
        if (this.props.readonly || isConstruction === this.isConstruction) {
            return;
        }
        await this.props.record.update({ [this.props.name]: isConstruction });
    }
}

registry.category("fields").add("contracting_invoice_kind", {
    component: ContractingInvoiceKindToggle,
    displayName: "Labour Supply / Construction switch",
    supportedTypes: ["boolean"],
});
