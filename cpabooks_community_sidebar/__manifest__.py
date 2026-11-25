# -*- coding: utf-8 -*-
{
    'name': 'Community App Sidebar',
    'summary': 'Left sidebar with all installed apps for Odoo 19 Community',
    'description': """
Community App Sidebar
=====================
Adds a left sidebar that lists every installed app, with search, to the
Odoo 19 Community web client. One click opens an app. A "Default menu"
button switches back to the standard top menu bar.

Built for Community only. It does not depend on or copy web_enterprise.
    """,
    'version': '19.0.1.0.17',
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
    'assets': {
        'web.assets_backend': [
            'cpabooks_community_sidebar/static/src/scss/sidebar.scss',
            'cpabooks_community_sidebar/static/src/js/sidebar.js',
            'cpabooks_community_sidebar/static/src/xml/sidebar.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
