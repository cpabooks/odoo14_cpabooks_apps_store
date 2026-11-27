# -*- coding: utf-8 -*-
from odoo import api, fields, models

UNLOCK_PARAM = 'cpabooks_db_lock.unlocked'


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    db_manager_locked = fields.Boolean(
        string='Lock Database Manager',
        help='Hide the Manage Databases link and the database selector on the login page, '
             'and block the database manager URLs (create, duplicate, drop, backup, restore).',
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['db_manager_locked'] = not self.env['ir.config_parameter'].sudo().get_param(UNLOCK_PARAM)
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        # set_param(key, False) removes the parameter, which means "locked".
        self.env['ir.config_parameter'].sudo().set_param(
            UNLOCK_PARAM, False if self.db_manager_locked else 'True')
