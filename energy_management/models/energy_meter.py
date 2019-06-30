import json
import logging

from datetime import datetime
from dateutil.relativedelta import relativedelta
from calendar import monthrange
from babel.dates import format_date

from odoo import models, fields, api
from odoo.tools import safe_eval
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class EnergyMeter(models.Model):
    _name = 'energy.meter'
    _inherit = ['mail.thread']

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
    kanban_dashboard_graph = fields.Text(compute='_compute_kanban_dashboard_graph')
    kanban_dashboard_graph_type = fields.Selection(string="", selection=[('line', 'Line'), ('bar', 'Bar'), ], default='line',)
    show_on_dashboard = fields.Boolean(default=True,)
    color = fields.Integer('Color Index',default=0)

    @api.multi
    def _compute_kanban_dashboard_graph(self):
        for meter in self:
            meter.kanban_dashboard_graph = json.dumps(meter.get_graph_datas())

    def _graph_title_and_key(self):
        return ['','Number']

    @api.multi
    def get_graph_datas(self):
        self.ensure_one()
        data = []
        ReadingLine = self.env['energy.meter.reading.line']
        today = datetime.today()
        first_date = today + relativedelta(months=-6)
        first_date = first_date.replace(day=monthrange(first_date.year,first_date.month)[0])
        last_date = today.replace(day=monthrange(today.year,today.month)[1])
        locale = self._context.get('lang') or 'en_US'
        reading_lines = ReadingLine.read_group(
            domain=[('meter_id','=',self.id),('reading_date','>=',first_date),('reading_date','<=',last_date)],
            fields=['reading_date', 'number'],
            groupby='reading_date:month')
        _logger.info(reading_lines)
        [graph_title, graph_key] = self._graph_title_and_key()
        if self.kanban_dashboard_graph_type in ['line',]:
            for reading_line in reading_lines:
                data.append({
                    'x': reading_line['reading_date:month'],
                    'name': reading_line['reading_date:month'],
                    'y': reading_line['number'],
                })
            _logger.info(data)
            return [{'values': data, 'title': graph_title, 'key': graph_key, 'area': True}]
        elif self.kanban_dashboard_graph_type in ['bar',]:
            for reading_line in reading_lines:
                data.append({
                    'label': reading_line['reading_date:month'],
                    'value': reading_line['number'],
                    'type':'past',
                })
            return [{'values': data, 'title': graph_title, 'key': graph_key}]
        else:
            raise ValidationError("This type of graph doesn't exit ! Verify the settings of your meter.")


    @api.multi
    def open_action(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "energy.meter",
            "views": [[False, "form"]],
            "res_id": self.id,
            "target": "current",
        }

    @api.multi
    def open_action_reading_lines(self):
        self.ensure_one()
        return{
                "name": "Meter Reading Lines",
                "type": "ir.actions.act_window",
                "res_model": "energy.meter.reading.line",
                "views": [[False, "tree"], [False, "form"]],
                "domain": [["meter_id", "=", self.id]],
        }

    @api.multi
    def open_transfer_money(self):
        return self.open_payments_action('transfer')

    @api.multi
    def open_create_reading_action(self):
        [action] = self.env.ref("energy_management.energy_meter_reading_view_action").read()
        action['context'] = dict(safe_eval(action.get('context')))
        action['views'] = [[False, 'form']]
        return action

    @api.model
    def send_mail_reminder(self):
        meters = self.search([('mail_reminder', '=', True)])
        template = self.env['mail.template'].browse(int(self.env["ir.config_parameter"].sudo().get_param("energy_management.mail_reminder_template_id")))
        _logger.info(template)
        if template:
            for meter in meters:
                if meter.partner_id and meter.partner_id.lang:
                    template = template.with_context(lang=meter.partner_id.lang)
                else:
                    template = template.with_context('en_US')
                template.send_mail(meter.id,force_send=True)


