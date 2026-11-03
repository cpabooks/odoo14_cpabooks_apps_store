# -*- coding: utf-8 -*-

def post_init_hook(cr, registry):
    from .install_notify import notify_app_install
    notify_app_install(cr, 'sequences_cpa', 'Invoice Sequence Numbering')
