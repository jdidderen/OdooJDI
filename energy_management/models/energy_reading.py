from odoo import models, fields, api

class EnergyMeterReading(models.Model):
    _name = 'energy.meter.reading'
    _rec_name = 'reading_date'
    _order = 'reading_date desc'

    reading_date = fields.Datetime(required=True,default=fields.Datetime.now, )
    reading_line_ids = fields.One2many(comodel_name="energy.meter.reading.line", inverse_name="reading_id", string="Reading Lines")
    comment = fields.Html()

class EnergyMeterReadingLine(models.Model):
    _name = 'energy.meter.reading.line'
    _order = 'reading_id desc'

    reading_id = fields.Many2one(comodel_name="energy.meter.reading", string="Meter Reading", required=True,)
    reading_date = fields.Datetime(related='reading_id.reading_date',readonly=True,store=True,)
    meter_id = fields.Many2one(comodel_name="energy.meter", string="", required=True, )
    number = fields.Float(string="Number",  required=True, )

    @api.multi
    def name_get(self):
        return [(record.id, '%s - %s' % (record.meter_id.name,record.reading_date)) for record in self]
