import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    other_name_ids = fields.Many2many(comodel_name="other.name",)


