# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    energy_mail_template_id = fields.Many2one(comodel_name="mail.template",config_parameter='energy_management.mail_reminder_template_id',)
    energy_mail_reminder = fields.Boolean(config_parameter='energy_management.mail_reminder',)
    energy_cron_id = fields.Many2one(comodel_name="ir.cron", string="Scheduled Action",config_parameter='energy_management.mail_reminder_cron_id',)
    energy_cron_nextcall = fields.Datetime(related='energy_cron_id.nextcall',readonly=False,)
    energy_cron_interval_number = fields.Integer(related='energy_cron_id.interval_number',readonly=False,)
    energy_cron_interval_type = fields.Selection([('minutes', 'Minutes'),
                                      ('hours', 'Hours'),
                                      ('days', 'Days'),
                                      ('weeks', 'Weeks'),
                                      ('months', 'Months')], related='energy_cron_id.interval_type',readonly=False,)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            energy_mail_reminder=self.env.ref('energy_management.ir_cron_energy_mail_reminder_action').active,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env.ref('energy_management.ir_cron_energy_mail_reminder_action').write({'active': self.energy_mail_reminder})
