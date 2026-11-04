# -*- coding: utf-8 -*-

from odoo import api, models


class TaskCustomCustomerCopyReport(models.AbstractModel):
    _inherit = 'report.field_service_cpa.worksheet_custom_customer'

    @api.model
    def _get_report_values(self, docids, data=None):
        res = super()._get_report_values(docids, data)
        res['report_copy_label'] = 'TMC Customer'
        return res
