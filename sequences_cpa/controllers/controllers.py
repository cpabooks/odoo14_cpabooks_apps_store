# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksSequences(http.Controller):
#     @http.route('/sequences_cpa/sequences_cpa/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sequences_cpa/sequences_cpa/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sequences_cpa.listing', {
#             'root': '/sequences_cpa/sequences_cpa',
#             'objects': http.request.env['sequences_cpa.sequences_cpa'].search([]),
#         })

#     @http.route('/sequences_cpa/sequences_cpa/objects/<model("sequences_cpa.sequences_cpa"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sequences_cpa.object', {
#             'object': obj
#         })
