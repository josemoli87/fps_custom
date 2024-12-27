# -*- coding: utf-8 -*-
# from odoo import http


# class FacturaUnidad(http.Controller):
#     @http.route('/factura_unidad/factura_unidad', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/factura_unidad/factura_unidad/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('factura_unidad.listing', {
#             'root': '/factura_unidad/factura_unidad',
#             'objects': http.request.env['factura_unidad.factura_unidad'].search([]),
#         })

#     @http.route('/factura_unidad/factura_unidad/objects/<model("factura_unidad.factura_unidad"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('factura_unidad.object', {
#             'object': obj
#         })

