import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)

class OtherName(models.Model):
    _name = "other.name"

    name = fields.Char(required=True,)

