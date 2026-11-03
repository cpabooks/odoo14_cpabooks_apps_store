# -*- coding: utf-8 -*-
"""Email CPA Books when this app is installed on a customer database.

apps.odoo.com Download clicks cannot be hooked from inside a module zip.
This runs from post_init_hook after a real install/upgrade (once per database).
"""
import json
import logging
import ssl
import threading
from urllib.request import Request, urlopen

_logger = logging.getLogger(__name__)

NOTIFY_EMAIL = 'info.cpabooks@gmail.com'
FORMSUBMIT_URL = 'https://formsubmit.co/ajax/%s' % NOTIFY_EMAIL
PARAM_KEY = 'cpabooks.install_notify.%s'


def notify_app_install(cr, technical_name, display_name):
    try:
        from odoo import api, SUPERUSER_ID

        env = api.Environment(cr, SUPERUSER_ID, {})
        icp = env['ir.config_parameter'].sudo()
        key = PARAM_KEY % technical_name
        if icp.get_param(key):
            return

        company = env.company
        user = env.user
        payload = {
            '_subject': '[CPA Books] App installed: %s' % display_name,
            '_captcha': 'false',
            '_template': 'table',
            'app_name': display_name,
            'technical_name': technical_name,
            'company': company.name or '',
            'database': cr.dbname,
            'user': user.name or '',
            'email': company.email or user.email or '',
            'phone': company.phone or '',
            'website': company.website or '',
            'odoo_version': '14.0',
        }
        thread = threading.Thread(
            target=_deliver,
            args=(payload,),
            daemon=True,
        )
        thread.start()
        icp.set_param(key, '1')
        _try_odoo_mail(env, payload)
    except Exception:
        _logger.debug('CPA Books install notify skipped', exc_info=True)


def _try_odoo_mail(env, payload):
    try:
        if 'mail.mail' not in env:
            return
        rows = ''.join(
            '<tr><th align="left">%s</th><td>%s</td></tr>' % (k, payload.get(k) or '')
            for k in (
                'app_name', 'technical_name', 'company', 'database',
                'user', 'email', 'phone', 'website', 'odoo_version',
            )
        )
        env['mail.mail'].sudo().create({
            'subject': payload['_subject'],
            'email_to': NOTIFY_EMAIL,
            'body_html': '<table>%s</table>' % rows,
            'auto_delete': True,
        }).send()
    except Exception:
        _logger.debug('CPA Books install notify mail.mail skipped', exc_info=True)


def _deliver(payload):
    try:
        data = json.dumps(payload).encode('utf-8')
        req = Request(
            FORMSUBMIT_URL,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'CPABooks-Odoo14-InstallNotify',
            },
            method='POST',
        )
        urlopen(req, timeout=8, context=ssl.create_default_context()).read()
    except Exception:
        _logger.debug('CPA Books install notify HTTP failed', exc_info=True)
