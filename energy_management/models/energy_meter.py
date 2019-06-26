from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EnergyMeter(models.Model):
    _name = 'energy.meter'

    @api.model
    def _get_company(self):
        return self.env.user.company_id

    name = fields.Char(required=True,)
    identifier = fields.Char(required=True,)
    partner_id = fields.Many2one(comodel_name="res.partner", string="Adress/Contact", required=True, )
    type_id = fields.Many2one(comodel_name="energy.type", required=True, )
    reading_line_ids = fields.One2many(comodel_name="energy.meter.reading.line", inverse_name="meter_id")
    description = fields.Text()
    mail_reminder = fields.Boolean()
    company_id = fields.Many2one('res.company', string='Company', required=True, default=_get_company)