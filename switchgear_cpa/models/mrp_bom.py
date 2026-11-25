# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    name = fields.Char(string='Number', required=True, copy=False, index=True, default=lambda self: _('New'))
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    mo_count = fields.Integer('# Manufacturing Order', compute='_compute_mo_count')
    estimate_id = fields.Many2one('job.estimate', string='Job Estimation')
    project_id = fields.Many2one('project.project', string='Job Order')
    partner_id = fields.Many2one('res.partner', string='Customer')
    estimate_reference = fields.Char(string='Estimation Reference', related='estimate_id.name')
    create_product_variant_id = fields.Many2one('product.template', string="Create Product Variants")

    def _compute_mo_count(self):
        for bom in self:
            bom.mo_count = self.env['mrp.production'].search_count([('bom_id', '=', bom.id)])

    @api.model_create_multi
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
        records = self.browse()
        for vals in vals_list:
            records |= self._create_single_MrpBom(vals)
        return records

    def _create_single_MrpBom(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('mrp.bom') or _('New')
            vals['create_product_variant_id'] = None
        return super(MrpBom, self).create(vals)

    def write(self, vals):
        if 'create_product_variant_id' in vals.keys():
            vals.pop('create_product_variant_id', None)
        return super(MrpBom, self).write(vals)

    def action_create_mo(self):
        for rec in self:
            product = rec._cpabooks_resolve_mo_product() if hasattr(
                rec, '_cpabooks_resolve_mo_product',
            ) else self.env['product.product'].sudo().search([
                ('product_tmpl_id', '=', rec.product_tmpl_id.id),
            ], limit=1)
            if not product:
                raise UserError(_('Cannot create manufacturing order: BOM has no product.'))
            mo_id = self.env['mrp.production'].create({
                'product_id': product.id,
                'product_qty': rec.product_qty or 1.0,
                'product_uom_id': product.uom_id.id,
                'bom_id': rec.id,
                'project_id': rec.project_id.id,
                'partner_id': rec.partner_id.id,
                'company_id': rec.company_id.id,
            })
            # Odoo 17+: raw moves, locations and work orders are computed fields.

    def explode(self, product, quantity, picking_type=False, never_attribute_values=False):
        """Odoo 19 explode; CPABooks reports also read 'product_qty' on the top BoM entry."""
        boms_done, lines_done = super().explode(
            product, quantity, picking_type=picking_type,
            never_attribute_values=never_attribute_values,
        )
        if boms_done:
            boms_done[0][1].setdefault('product_qty', quantity)
        return boms_done, lines_done
