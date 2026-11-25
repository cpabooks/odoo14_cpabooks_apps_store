# -*- coding: utf-8 -*-
{
    "name": "Construction & Labour Supply Invoice",
    "summary": "Progress billing for contractors: Work Done %, Previous % and a Contracting Invoice PDF",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "author": "CPA Books",
    "website": "https://www.cpabooks.co",
    "support": "info@cpabooks.org",
    "license": "LGPL-3",
    "price": 120.00,
    "currency": "USD",
    "images": ["static/description/banner.png"],
    "live_test_url": "https://cpabooks.org/contactus?debug=1",
    "description": """
Construction & Labour Supply Invoice
====================================
Progress billing for contracting companies on standard Odoo customer invoices.

* Labour Supply Invoice / Construction Invoice switch on the invoice form.
* Construction lines carry Previous %, Work Done %, Contract Amount and a
  Guarantee flag. Only the Work Done % of each line is invoiced, so the
  journal entry, taxes, amount due and payments all follow the claimed value.
* Contracting Invoice PDF with Amount Excl. Tax, Previous %, Work Done %,
  Work Done Amount and Amount Incl. Tax.
* Next Progress Claim button: copies the invoice and moves the claimed
  percentage into Previous %.
* Company setting to open new customer invoices as Construction invoices.

Depends only on Odoo Accounting (Invoicing).
""",
    "depends": [
        "account",
    ],
    "data": [
        "views/account_move_views.xml",
        "views/res_config_settings_views.xml",
        "report/contracting_invoice_report.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "cpabooks_contracting_invoice/static/src/css/invoice_kind_toggle.css",
            "cpabooks_contracting_invoice/static/src/js/invoice_kind_toggle.js",
            "cpabooks_contracting_invoice/static/src/xml/invoice_kind_toggle.xml",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
    "post_init_hook": "post_init_hook",
}
