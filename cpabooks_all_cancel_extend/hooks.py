# -*- coding: utf-8 -*-

def post_init_hook(cr, registry):
    from .install_notify import notify_app_install
    notify_app_install(cr, 'cpabooks_all_cancel_extend', 'All in One Cancel')
