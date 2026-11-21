# -*- coding: utf-8 -*-
{
    "name": "Database Manager Lock",
    "summary": "Hide and block the Odoo database manager: no Manage Databases link, no database selector, no create / drop / backup / restore URLs",
    "version": "14.0.1.0.0",
    "category": "Tools",
    "author": "CPA Books",
    "website": "https://www.cpabooks.co",
    "support": "info@cpabooks.org",
    "license": "LGPL-3",
    "price": 10.00,
    "currency": "USD",
    "images": ["static/description/banner.png"],
    "live_test_url": "https://cpabooks.org/contactus?debug=1",
    "description": """
Database Manager Lock
=====================
* Removes the "Manage Databases" link and the database "Select" button from the login page.
* Blocks the database manager URLs on the server (selector, manager, create,
  duplicate, drop, backup, restore, change master password). They answer 404.
* /web/database/list only returns the current database.
* Settings > General Settings > Lock Database Manager: unlock for a moment
  when you need a backup, then lock again.

Full lock on a server with several databases: also load the module server-wide
(``--load=base,web,cpabooks_db_lock`` or ``server_wide_modules`` in odoo.conf).
""",
    "depends": [
        "web",
        "base_setup",
    ],
    "data": [
        "views/login_templates.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "post_init_hook": "post_init_hook",
}
