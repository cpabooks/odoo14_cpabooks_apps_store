# -*- coding: utf-8 -*-
import logging

from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.database import Database

_logger = logging.getLogger(__name__)

UNLOCK_PARAM = 'cpabooks_db_lock.unlocked'


def db_manager_locked():
    """True unless an administrator unlocked the database manager in Settings.

    Without a database (server-wide load, several databases, no session)
    there is no setting to read, so the manager stays locked.
    """
    if not request.db:
        return True
    try:
        return not request.env['ir.config_parameter'].sudo().get_param(UNLOCK_PARAM)
    except Exception:
        _logger.exception('Database Manager Lock: could not read the setting, keeping the lock')
        return True


def _blocked():
    _logger.warning('Database Manager Lock: blocked %s from %s',
                    request.httprequest.path, request.httprequest.remote_addr)
    raise NotFound()


class DatabaseLock(Database):

    @http.route()
    def selector(self, **kw):
        if db_manager_locked():
            return _blocked()
        return super(DatabaseLock, self).selector(**kw)

    @http.route()
    def manager(self, **kw):
        if db_manager_locked():
            return _blocked()
        return super(DatabaseLock, self).manager(**kw)

    @http.route()
    def create(self, *args, **kw):
        if db_manager_locked():
            return _blocked()
        return super(DatabaseLock, self).create(*args, **kw)

    @http.route()
    def duplicate(self, *args, **kw):
        if db_manager_locked():
            return _blocked()
        return super(DatabaseLock, self).duplicate(*args, **kw)

    @http.route()
    def drop(self, *args, **kw):
        if db_manager_locked():
            return _blocked()
        return super(DatabaseLock, self).drop(*args, **kw)

    @http.route()
    def backup(self, *args, **kw):
        if db_manager_locked():
            return _blocked()
        return super(DatabaseLock, self).backup(*args, **kw)

    @http.route()
    def restore(self, *args, **kw):
        if db_manager_locked():
            return _blocked()
        return super(DatabaseLock, self).restore(*args, **kw)

    @http.route()
    def change_password(self, *args, **kw):
        if db_manager_locked():
            return _blocked()
        return super(DatabaseLock, self).change_password(*args, **kw)

    @http.route()
    def list(self):
        # Odoo mobile app uses this: give it the current database only.
        if db_manager_locked():
            return [request.db] if request.db else []
        return super(DatabaseLock, self).list()
