from odoo import api, fields, models

class Partner(models.Model):
    _inherit = 'res.partner'

    energy_meter_count = fields.Integer(compute="_compute_meter", copy=False, default=0, store=True,)
    energy_meter_ids = fields.One2many(comodel_name="energy.meter", inverse_name="partner_id", string="Meters",)

    @api.depends('energy_meter_ids')
    def _compute_meter(self):
        for partner in self:
            partner.energy_meter_count = len(partner.energy_meter_ids)

    @api.multi
    def action_view_meter(self):
        meters = self.mapped('energy_meter_ids')
        action = self.env.ref('energy_management.energy_meter_view_action').read()[0]
        if len(meters) > 1:
            action['domain'] = [('id', 'in', meters.ids)]
        elif len(meters) == 1:
            action['views'] = [(self.env.ref('energy_management.energy_meter_view_form').id, 'form')]
            action['res_id'] = meters.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action