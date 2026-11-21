odoo.define('cpabooks_contracting_invoice.invoice_kind_toggle', function (require) {
    "use strict";

    /**
     * "Labour Supply Invoice | Construction Invoice" switch in the control
     * panel of customer invoices and credit notes. It writes the
     * is_construction_invoice field; the server keeps the lines in sync.
     */
    var FormController = require('web.FormController');
    var core = require('web.core');
    var _t = core._t;

    var TOGGLE_CLASS = 'o_cpa_contracting_invoice_kind_toggle';
    var CUSTOMER_TYPES = {out_invoice: true, out_refund: true};

    FormController.include({
        _cpaContractingData: function () {
            var state = this.renderer && this.renderer.state;
            return state && state.data;
        },

        _cpaRemoveKindToggle: function () {
            if (this.$buttons) {
                this.$buttons.find('.' + TOGGLE_CLASS).remove();
            }
        },

        _cpaSyncKindToggle: function ($wrap, data) {
            var isConstruction = Boolean(data.is_construction_invoice);
            var editable = data.state === 'draft';
            $wrap.find('.o_cpa_kind_labour').toggleClass('o_cpa_kind_selected', !isConstruction)
                .prop('disabled', !editable);
            $wrap.find('.o_cpa_kind_construction').toggleClass('o_cpa_kind_selected', isConstruction)
                .prop('disabled', !editable);
        },

        _cpaSetInvoiceKind: function (isConstruction) {
            var self = this;
            var state = this.renderer && this.renderer.state;
            if (!state || !state.data || Boolean(state.data.is_construction_invoice) === isConstruction) {
                return Promise.resolve();
            }
            var changes = {is_construction_invoice: isConstruction};
            if (!state.res_id || this.mode === 'edit') {
                return this._applyChanges(state.id, changes, {});
            }
            return this._rpc({
                model: 'account.move',
                method: 'write',
                args: [[state.res_id], changes],
            }).then(function () {
                return self.reload();
            });
        },

        _cpaRenderKindToggle: function () {
            if (this.modelName !== 'account.move' || !this.$buttons) {
                return;
            }
            var data = this._cpaContractingData();
            if (!data || data.is_construction_invoice === undefined || !CUSTOMER_TYPES[data.move_type]) {
                this._cpaRemoveKindToggle();
                return;
            }
            var $wrap = this.$buttons.find('.' + TOGGLE_CLASS);
            if (!$wrap.length) {
                var self = this;
                $wrap = $('<div/>', {'class': 'btn-group ' + TOGGLE_CLASS, role: 'group'});
                $('<button/>', {type: 'button', 'class': 'btn btn-sm o_cpa_kind_labour', 'data-kind': 'labour'})
                    .text(_t('Labour Supply Invoice')).appendTo($wrap);
                $('<button/>', {type: 'button', 'class': 'btn btn-sm o_cpa_kind_construction', 'data-kind': 'construction'})
                    .text(_t('Construction Invoice')).appendTo($wrap);
                $wrap.on('click', 'button[data-kind]', function (ev) {
                    ev.preventDefault();
                    ev.stopPropagation();
                    self._cpaSetInvoiceKind($(ev.currentTarget).data('kind') === 'construction');
                });
                var $create = this.$buttons.find('.o_form_button_create');
                if ($create.length) {
                    $wrap.insertAfter($create);
                } else {
                    this.$buttons.append($wrap);
                }
            }
            this._cpaSyncKindToggle($wrap, data);
        },

        renderButtons: function () {
            this._super.apply(this, arguments);
            this._cpaRenderKindToggle();
        },

        updateButtons: function () {
            this._super.apply(this, arguments);
            this._cpaRenderKindToggle();
        },

        _applyChanges: function () {
            var self = this;
            return Promise.resolve(this._super.apply(this, arguments)).then(function (res) {
                self._cpaRenderKindToggle();
                return res;
            });
        },
    });
});
