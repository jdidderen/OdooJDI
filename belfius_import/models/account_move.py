import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    banking_receipt = fields.Char()
    transaction_number = fields.Char()

