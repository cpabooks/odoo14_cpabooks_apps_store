# -*- coding: utf-8 -*-

def post_init_hook(cr, registry):
    from .install_notify import notify_app_install
    notify_app_install(cr, 'recipe_book_cpa', 'Recipe and Food Costing')
