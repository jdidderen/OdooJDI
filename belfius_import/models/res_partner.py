import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    other_name = fields.Text(string="Other(s) name(s)", required=False, )


