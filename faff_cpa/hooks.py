# -*- coding: utf-8 -*-

def post_init_hook(env):
    cr = env.cr
    registry = env.registry
    from .install_notify import notify_app_install
    notify_app_install(env, 'faff_cpa', 'Fire Alarm and Fire Fighting')
