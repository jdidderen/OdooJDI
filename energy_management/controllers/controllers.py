# -*- coding: utf-8 -*-
from odoo import http

# class EnergyManagement(http.Controller):
#     @http.route('/energy_management/energy_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/energy_management/energy_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('energy_management.listing', {
#             'root': '/energy_management/energy_management',
#             'objects': http.request.env['energy_management.energy_management'].search([]),
#         })

#     @http.route('/energy_management/energy_management/objects/<model("energy_management.energy_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('energy_management.object', {
#             'object': obj
#         })