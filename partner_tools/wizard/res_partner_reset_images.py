# -*- coding: utf-8 -*-

from odoo import models, tools

class ResPartnerResetImage(models.TransientModel):
    _name = 'res.partner.reset.image'

    def set_images(self):
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            partners = self.env['res.partner'].browse(active_ids)
            for partner in partners:
                vals = {'image':self.env['res.partner']._get_default_image(partner['type'], partner['is_company'], partner['parent_id'])}
                tools.image_resize_images(vals, sizes={'image': (1024, None)})
                partner.write(vals)