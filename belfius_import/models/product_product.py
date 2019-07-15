import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = "product.product"

    other_name_ids = fields.Many2many(relation="other.name",)

