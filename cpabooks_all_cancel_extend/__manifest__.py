# -*- coding: utf-8 -*-
{
    'name': 'All in One Cancel: Invoice, Payment, Sale, Purchase, Picking',
    'summary': 'Cancel, reset to draft or delete posted invoices, payments, '
               'sale orders, purchase orders, done pickings and expense reports',
    'description': """
All in One Cancel
=================
One module to undo posted documents in Odoo 19 Community and Enterprise:

* Invoices, bills, credit notes and journal entries: cancel, reset to draft or delete.
* Payments: cancel, reset to draft or delete (linked payments are handled too).
* Sale orders and purchase orders: cancel together with their invoices,
  payments and done deliveries / receipts.
* Done pickings: cancel and put the stock back, then reset to draft.
* Expense reports (when Expenses is installed): cancel, reset or delete
  posted reports.
* Mass confirm quotations and RFQs from the list view.

Only users in the group "Cancel Posted Documents" can use these actions.
    """,
    'author': 'CPA Books',
    'website': 'https://www.cpabooks.co',
    'support': 'info@cpabooks.org',
    'category': 'Accounting/Accounting',
    'version': '19.0.2.0.0',
    'license': 'LGPL-3',
    'price': 15.00,
    'currency': 'USD',
    'images': ['static/description/banner.jpg'],
    'live_test_url': 'https://cpabooks.org/contactus?debug=1',

    # Official Odoo addons only. stock_account and hr_expense are optional:
    # they are used when installed, without being required.
    'depends': [
        'account',
        'sale_management',
        'sale_stock',
        'purchase',
        'purchase_stock',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/cpa_cancel_wizard_views.xml',
        'views/res_config_settings_views.xml',
        'views/account_views.xml',
        'views/stock_picking_views.xml',
        'data/server_actions.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
