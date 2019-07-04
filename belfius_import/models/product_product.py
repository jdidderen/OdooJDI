import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = "product.product"

    other_name = fields.Text(string="Other(s) name(s)", required=False, )

