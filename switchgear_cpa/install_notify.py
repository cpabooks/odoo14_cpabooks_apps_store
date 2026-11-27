# -*- coding: utf-8 -*-
"""Notify CPA Books when this app is installed on a customer database.

Customer PCs do not need SMTP. post_init_hook POSTs to cpabooks.org, which
emails info.cpabooks@gmail.com. Apps Store Download clicks cannot be hooked.
"""
import json
import logging
import ssl
from urllib.parse import urlencode
from urllib.request import HTTPSHandler, ProxyHandler, Request, build_opener

_logger = logging.getLogger(__name__)

NOTIFY_EMAIL = 'info.cpabooks@gmail.com'
NOTIFY_TOKEN = 'cpa14-app-install-9f3e2a'
PARAM_KEY = 'cpabooks.install_notify.%s'
WEBHOOK_URLS = (
    'https://cpabooks.org/cpabooks/app_install_notify',
    'https://www.cpabooks.org/cpabooks/app_install_notify',
)
FORMSUBMIT_URL = 'https://formsubmit.co/ajax/%s' % NOTIFY_EMAIL


def notify_app_install(env, technical_name, display_name):
    try:
        from odoo import SUPERUSER_ID, api

        cr = env.cr
        env = api.Environment(cr, SUPERUSER_ID, {})
        icp = env['ir.config_parameter'].sudo()
        key = PARAM_KEY % technical_name
        if icp.get_param(key):
            _logger.info('CPA Books install notify already sent for %s', technical_name)
            return

        company = env.company
        user = env.user
        payload = {
            'token': NOTIFY_TOKEN,
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
            'odoo_version': '19.0',
        }
        icp.set_param(key, '1')
        if _deliver_webhook(payload) or _deliver_formsubmit(payload):
            return
        _try_odoo_mail(env, payload)
    except Exception:
        _logger.exception('CPA Books install notify skipped')


def _try_odoo_mail(env, payload):
    try:
        if 'mail.mail' not in env:
            return
        if 'ir.mail_server' in env and not env['ir.mail_server'].sudo().search([], limit=1):
            from odoo.tools import config
            if not config.get('smtp_user'):
                return
        rows = ''.join(
            '<tr><th align="left">%s</th><td>%s</td></tr>' % (k, payload.get(k) or '')
            for k in (
                'app_name', 'technical_name', 'company', 'database',
                'user', 'email', 'phone', 'website', 'odoo_version',
            )
        )
        mail = env['mail.mail'].sudo().create({
            'subject': payload['_subject'],
            'email_to': NOTIFY_EMAIL,
            'email_from': payload.get('email') or NOTIFY_EMAIL,
            'body_html': '<table>%s</table>' % rows,
            'auto_delete': True,
        })
        mail.send()
        _logger.info('CPA Books install notify local mail.mail state=%s', mail.state)
    except Exception:
        _logger.debug('CPA Books install notify local mail skipped', exc_info=True)


def _opener():
    return build_opener(
        ProxyHandler({}),
        HTTPSHandler(context=ssl.create_default_context()),
    )


def _deliver_webhook(payload):
    body = json.dumps(payload).encode('utf-8')
    for url in WEBHOOK_URLS:
        try:
            req = Request(
                url,
                data=body,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'User-Agent': 'CPABooks-Odoo19-InstallNotify',
                },
                method='POST',
            )
            resp = _opener().open(req, timeout=10)
            raw = resp.read()[:400]
            _logger.info('CPA Books install notify webhook %s %s', resp.getcode(), raw)
            if resp.getcode() and 200 <= resp.getcode() < 300:
                return True
        except Exception as err:
            _logger.warning('CPA Books install notify webhook failed %s: %s', url, err)
    return False


def _deliver_formsubmit(payload):
    try:
        form = {k: v for k, v in payload.items() if k != 'token'}
        req = Request(
            FORMSUBMIT_URL,
            data=urlencode(form).encode('utf-8'),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (compatible; CPABooksInstallNotify/1.0)',
            },
            method='POST',
        )
        resp = _opener().open(req, timeout=8)
        _logger.info('CPA Books install notify formsubmit %s', resp.getcode())
        return True
    except Exception as err:
        _logger.warning('CPA Books install notify formsubmit failed: %s', err)
        return False
