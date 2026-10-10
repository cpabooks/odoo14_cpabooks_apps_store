# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        DELETE FROM ir_ui_view
         WHERE id IN (
            SELECT res_id
              FROM ir_model_data
             WHERE module = 'cafm_cpa'
               AND name = 'view_cafm_cpa_contract_order_form_sale'
         )
        """
    )
    cr.execute(
        """
        DELETE FROM ir_model_data
         WHERE module = 'cafm_cpa'
           AND name = 'view_cafm_cpa_contract_order_form_sale'
        """
    )
