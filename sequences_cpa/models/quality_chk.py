from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class QualityCheck(models.Model):
    _inherit = 'quality.check'

    @api.model_create_multi
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
        records = self.browse()
        for vals in vals_list:
            records |= self._create_single_QualityCheck(vals)
        return records

    def _create_single_QualityCheck(self, vals_list):
        print(vals_list)
        res = super(QualityCheck, self).create(vals_list)
        get_sequence = self.env['ir.sequence'].next_by_sequence_for('quality_chk')
        if not get_sequence:
            raise ValidationError(_("Sequence is not set for Quality Check"))
        res.name = get_sequence or _('/')
        return res