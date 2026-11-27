# -*- coding: utf-8 -*-
"""Odoo 18+ company-dependent account values (jsonb) helpers (replaces ir.property SQL)."""


def company_dependent_account_columns(env):
    """(table, column) of every stored company-dependent many2one to account.account.

    Odoo 18 removed ir.property: such values now live in a jsonb column
    {company_id: account_id} on the model's own table.
    """
    columns = []
    for model_name in env.registry:
        model = env[model_name]
        if model._abstract or not model._auto:
            continue
        for field in model._fields.values():
            if (
                field.type == 'many2one'
                and field.comodel_name == 'account.account'
                and field.company_dependent
                and field.store
            ):
                columns.append((model._table, field.name))
    return columns


def reassign_company_dependent_accounts(env, source_ids, target_id=None):
    """Point company-dependent account values from source_ids to target_id.

    With target_id=None the values are removed (dangling references cleanup).
    """
    source_ids = [int(i) for i in source_ids or []]
    if not source_ids:
        return
    sources_txt = [str(i) for i in source_ids]
    cr = env.cr
    for table, column in company_dependent_account_columns(env):
        if target_id:
            new_value = "to_jsonb(%s::int)" % int(target_id)
            cr.execute(
                f'''
                UPDATE "{table}" t
                   SET "{column}" = (
                        SELECT jsonb_object_agg(e.key, CASE WHEN e.value #>> '{{}}' = ANY(%s) THEN {new_value} ELSE e.value END)
                          FROM jsonb_each(t."{column}") e
                   )
                 WHERE t."{column}" IS NOT NULL
                   AND EXISTS (SELECT 1 FROM jsonb_each(t."{column}") e WHERE e.value #>> '{{}}' = ANY(%s))
                ''',
                [sources_txt, sources_txt],
            )
        else:
            cr.execute(
                f'''
                UPDATE "{table}" t
                   SET "{column}" = NULLIF((
                        SELECT COALESCE(jsonb_object_agg(e.key, e.value), '{{}}'::jsonb)
                          FROM jsonb_each(t."{column}") e
                         WHERE NOT (e.value #>> '{{}}' = ANY(%s))
                   ), '{{}}'::jsonb)
                 WHERE t."{column}" IS NOT NULL
                   AND EXISTS (SELECT 1 FROM jsonb_each(t."{column}") e WHERE e.value #>> '{{}}' = ANY(%s))
                ''',
                [sources_txt, sources_txt],
            )
    env.invalidate_all()
