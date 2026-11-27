# -*- coding: utf-8 -*-
{
    'name': 'CPABooks Account Compatibility',
    'summary': 'Odoo 14 account type, company and group fields for CPABooks accounting apps',
    'description': """
CPABooks Account Compatibility
==============================
Technical module shared by CPABooks accounting apps (Chart of Accounts
Management, Audited Financials) on Odoo 19:

* ``account.account.type``: the Odoo 14 account types, one per Odoo 19
  ``account_type`` (code = account_type).
* ``account.account``: ``user_type_id``, ``internal_type``, ``company_id``,
  ``deprecated`` and an editable stored ``group_id``.

It is installed automatically as a dependency.
    """,
    'version': '19.0.1.0.0',
    'category': 'Hidden',
    'author': 'CPA Books',
    'website': 'https://www.cpabooks.co',
    'support': 'info@cpabooks.org',
    'license': 'LGPL-3',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'data/account_type_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
