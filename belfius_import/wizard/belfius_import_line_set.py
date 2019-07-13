# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError

class BelfiusImportLineSet(models.TransientModel):
    _name = 'belfius.import.line.set'

    partner_id = fields.Many2one(comodel_name='res.partner')
    product_id = fields.Many2one(comodel_name='product.product')
    type = fields.Selection(string="Type", selection=[('sale', 'Sale'), ('purchase', 'Purchase'), ], required=False, )

    def set_lines(self):
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            vals = {}
            if self.partner_id:
                vals['partner_id'] = self.partner_id.id
            if self.product_id:
                vals['product_id'] = self.product_id.id
            if self.type:
                vals['type'] = self.type
            if vals:
                lines = self.env['belfius.import.line'].browse(active_ids)
                if lines.filtered(lambda l:l.state != 'awaiting'):
                    raise UserError("You can not change a line with a state different from 'Awaiting Confirmation'")
                else:
                    lines.write(vals)
