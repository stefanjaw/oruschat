# -*- coding: utf-8 -*-
# from odoo import http


# class Oruschat(http.Controller):
#     @http.route('/oruschat/oruschat/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/oruschat/oruschat/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('oruschat.listing', {
#             'root': '/oruschat/oruschat',
#             'objects': http.request.env['oruschat.oruschat'].search([]),
#         })

#     @http.route('/oruschat/oruschat/objects/<model("oruschat.oruschat"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('oruschat.object', {
#             'object': obj
#         })
