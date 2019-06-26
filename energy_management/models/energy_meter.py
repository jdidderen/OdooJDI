from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EnergyMeter(models.Model):
    _name = 'energy.meter'

    name = fields.Char(required=True,)
    identifier = fields.Char(required=True,)
    partner_id = fields.Many2one(comodel_name="res.partner", string="Adress/Contact", required=True, )
    type_id = fields.Many2one(comodel_name="energy.type", required=True, )
    reading_line_ids = fields.One2many(comodel_name="energy.meter.reading.line", inverse_name="meter_id")
    description = fields.Text()
    automation = fields.Boolean()
    cron_id = fields.Many2one(comodel_name="ir.cron", string="CRON")
    interval_number = fields.Integer(help="Repeat every x.")
    interval_type = fields.Selection([('minutes', 'Minutes'),
                                      ('hours', 'Hours'),
                                      ('days', 'Days'),
                                      ('weeks', 'Weeks'),
                                      ('months', 'Months')], string='Interval Unit')
    nextcall = fields.Datetime(related='cron_id.nextcall')

    @api.constrains("automation", "interval_number", "interval_type")
    def _check_automation(self):
        """Ensure values are setup for automation."""
        for record in self:
            if record.automation:
                if not (record.interval_number or record.interval_type):
                    raise ValidationError(_('If you want to activate the automation, you have to set the interval.'))

    @api.multi
    def _create_cron(self):
        pass

    @api.model
    def create(self, values):
        meter = super(EnergyMeter, self).create(values)
        if meter.automation:
            pass
        return meter

    @api.multi
    def write(self, values):
        # Add code here
        return super(EnergyMeter, self).write(values)