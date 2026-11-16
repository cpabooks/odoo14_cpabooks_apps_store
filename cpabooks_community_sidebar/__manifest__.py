# -*- coding: utf-8 -*-
{
    'name': 'Community App Sidebar',
    'summary': 'Left sidebar with all installed apps for Odoo 14 Community',
    'description': """
Community App Sidebar
=====================
Adds a left sidebar that lists every installed app, with search, to the
Odoo 14 Community web client. One click opens an app. A "Default menu"
button switches back to the standard top menu bar.

Built for Community only. It does not depend on or copy web_enterprise.
    """,
    'version': '14.0.1.0.17',
    'category': 'Productivity',
    'author': 'CPA Books',
    'website': 'https://www.cpabooks.co',
    'support': 'info@cpabooks.org',
    'license': 'LGPL-3',
    'price': 35.00,
    'currency': 'USD',
    'images': ['static/description/banner.jpg'],
    'live_test_url': 'https://cpabooks.org/contactus?debug=1',
    'depends': ['web'],
    'data': [
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/sidebar.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
