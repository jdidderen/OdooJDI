# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResPartnerMassSet(models.TransientModel):
    _name = 'res.partner.mass.set'

    is_company = fields.Boolean(string='Is a Company',)
    customer = fields.Boolean(string='Is a Customer',)
    supplier = fields.Boolean(string='Is a Vendor',)

    def set_partners(self):
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            vals = {'customer':self.customer,'supplier':self.supplier,'is_company':self.is_company}
            partners = self.env['res.partner'].browse(active_ids).write(vals)