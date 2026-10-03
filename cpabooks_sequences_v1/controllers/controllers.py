# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksSequences(http.Controller):
#     @http.route('/cpabooks_sequences_v1/cpabooks_sequences_v1/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_sequences_v1/cpabooks_sequences_v1/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_sequences_v1.listing', {
#             'root': '/cpabooks_sequences_v1/cpabooks_sequences_v1',
#             'objects': http.request.env['cpabooks_sequences_v1.cpabooks_sequences_v1'].search([]),
#         })

#     @http.route('/cpabooks_sequences_v1/cpabooks_sequences_v1/objects/<model("cpabooks_sequences_v1.cpabooks_sequences_v1"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_sequences_v1.object', {
#             'object': obj
#         })
