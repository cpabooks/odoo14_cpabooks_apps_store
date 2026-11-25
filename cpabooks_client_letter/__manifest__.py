{
    "name": "Client Letter Generator",
    "summary": "Client letters, emails and WhatsApp messages from CRM, quotations, invoices and projects",
    "version": "19.0.1.1.2",
    "category": "Sales/CRM",
    "author": "CPA Books",
    "website": "https://www.cpabooks.co",
    "support": "info@cpabooks.org",
    "license": "LGPL-3",
    "price": 10.00,
    "currency": "USD",
    "images": ["static/description/banner.jpg"],
    "live_test_url": "https://cpabooks.org/contactus?debug=1",
    "description": """
Client Letter Generator
=======================
Create client letters, emails and WhatsApp messages from CRM leads,
quotations, customer invoices and projects. Letter types are templates
with placeholders such as {{client_name}} and {{project_name}}.
Print the letter as PDF, send it by email or keep it in the chatter.

If an estimation app that provides the model job.estimate is installed,
estimations are supported too. It is not required.
""",
    "depends": [
        "crm",
        "sale_management",
        "account",
        "project",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/client_letter_sequence.xml",
        "data/client_letter_template_data.xml",
        "views/client_letter_document_views.xml",
        "views/client_letter_template_views.xml",
        "wizard/client_letter_wizard_views.xml",
        "views/action_buttons_views.xml",
        "report/client_letter_report.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
    "post_init_hook": "post_init_hook",
}
