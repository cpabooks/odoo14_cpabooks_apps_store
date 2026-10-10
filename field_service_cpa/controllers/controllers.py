# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksFieldServieceExtend(http.Controller):
#     @http.route('/field_service_cpa/field_service_cpa/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/field_service_cpa/field_service_cpa/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('field_service_cpa.listing', {
#             'root': '/field_service_cpa/field_service_cpa',
#             'objects': http.request.env['field_service_cpa.field_service_cpa'].search([]),
#         })

#     @http.route('/field_service_cpa/field_service_cpa/objects/<model("field_service_cpa.field_service_cpa"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('field_service_cpa.object', {
#             'object': obj
#         })
