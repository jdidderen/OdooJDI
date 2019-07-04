import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    banking_receipt = fields.Char()
    transaction_number = fields.Char()
    description = fields.Text(string='Description')


