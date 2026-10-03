# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_ui_view
           SET mode = 'primary'
         WHERE id IN (
            SELECT res_id
              FROM ir_model_data
             WHERE module = 'cpabooks_cafm_v1'
               AND name = 'view_cpabooks_cafm_v1_amc_invoice_tree'
               AND model = 'ir.ui.view'
         )
        """
    )
    cr.execute(
        """
        DELETE FROM ir_attachment
         WHERE name LIKE 'web.assets_backend%%'
            OR url LIKE '/web/content/%%assets_backend%%'
        """
    )
