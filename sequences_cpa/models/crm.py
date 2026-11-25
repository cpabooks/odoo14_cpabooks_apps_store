from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class CRMLeadInheritance(models.Model):
    _inherit = 'crm.lead'

    @api.model_create_multi
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
        records = self.browse()
        for vals in vals_list:
            records |= self._create_single_CRMLeadInheritance(vals)
        return records

    def _create_single_CRMLeadInheritance(self, vals_list):
        print(vals_list)
        res = super(CRMLeadInheritance, self).create(vals_list)
        get_sequence = self.env['ir.sequence'].next_by_sequence_for('crm')
        if not get_sequence:
            raise ValidationError(_("Sequence is not set for CRM"))
        res.enquiry_number = get_sequence or _('/')
        return res