import base64
import logging
import openpyxl
import os
import datetime
import pandas as pd
import tempfile
from dateutil import parser

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class BelfiusImport(models.Model):
    _name = "belfius.import"

    name = fields.Char(required=True, )
    filename = fields.Char(required=True)
    file = fields.Binary(required=True)
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('progress', 'In progress'), ('awaiting', 'Awaiting Confirmation'),
                   ('done', 'Done'), ('error', 'Error')], default='draft')
    line_ids = fields.One2many(comodel_name="belfius.import.line", inverse_name="import_id")
    mastercard_wordline = fields.Boolean(default=False)

    @api.multi
    def create_from_files(self):
        self.ensure_one()
        self.write({'state':'progress'})
        error = False
        BelfiusImportLine = self.env['belfius.import.line']
        try:
            data_file = base64.decodestring(self.file)
            fobj = tempfile.NamedTemporaryFile(delete=False)
            fobj.write(data_file)
            if not self.mastercard_wordline:
                df = pd.read_csv(fobj.name, sep=';', header=12, encoding='iso-8859-1',
                                 names=["own_account", "account_date", "banking_receipt", "transaction_number",
                                        "partner_account", "partner_name", "partner_street", "partner_zip_city", "name",
                                        "value_date", "amount", "currency", "partner_bic", "partner_country",
                                        "description"],
                                 dtype={'own_account': 'str', 'account_date': 'str', 'banking_receipt': 'str',
                                         'transaction_number': 'str',
                                         'partner_account': 'str', 'partner_name': 'str', 'partner_street': 'str',
                                         'partner_zip_city': 'str',
                                         'value_date': 'str', 'amount': 'str', 'currency': 'str',
                                         'partner_bic': 'str',
                                         'partner_country': 'str', 'description': 'str', })
                df = df.fillna(False)
                for index, row in df.iterrows():
                    BelfiusImportLine.process_line_normal_receipt(row, self.id)
            else:
                wb = openpyxl.load_workbook(fobj)
                ws = wb.active
                for row in ws.iter_rows():
                    BelfiusImportLine.process_line_mastercard_receipt(row,self.id)
            fobj.close()
        except Exception as e:
            _logger.info(e)
            error = True
            self.write({'state':'error'})
        finally:
            os.unlink(fobj.name)
            if not error:
                self.write({'state':'awaiting'})

    def _create_invoice(self,partner,type,account_date):
        if type == 'purchase':
            invoice_type = 'in_invoice'
        else:
            invoice_type = 'out_invoice'
        invoice = self.env['account.invoice'].create({
            'type': invoice_type,
            'reference': False,
            'account_id': partner.property_account_receivable_id.id,
            'partner_id': partner.id,
            'currency_id': partner.company_id.currency_id.id,
            'fiscal_position_id': partner.property_account_position_id.id,
            'date_invoice':account_date,
        })
        return invoice

    @api.multi
    def confirm_lines(self):
        self.ensure_one()
        try:
            partner_ids = self.line_ids.mapped('partner_id')
            for partner_id in partner_ids:
                dates = sorted(list(set(self.line_ids.filtered(lambda l:l.partner_id.id == partner_id.id).mapped('account_date'))))
                for date in dates:
                    lines = self.line_ids.filtered(lambda l:l.partner_id.id == partner_id.id and l.account_date == date)
                    purchase_lines = lines.filtered(lambda l:l.type == 'purchase')
                    if purchase_lines:
                        purchase_invoice = self._create_invoice(partner_id,'purchase',date)
                        if purchase_invoice:
                            for purchase_line in purchase_lines:
                                purchase_line.create_invoice_line(purchase_invoice)
                    sale_lines = lines.filtered(lambda l:l.type == 'sale')
                    if sale_lines:
                        sale_invoice = self._create_invoice(partner_id,'sale',date)
                        if sale_invoice:
                            for asle_line in sale_lines:
                                asle_line.create_invoice_line(sale_invoice)
            self.write({'state':'done'})
        except Exception:
            self.write({'state':'error'})

class BelfiusImportLine(models.Model):
    _name = 'belfius.import.line'

    name = fields.Text()
    description = fields.Text()
    banking_receipt = fields.Char()
    transaction_number = fields.Char()
    partner_id = fields.Many2one(comodel_name='res.partner')
    product_id = fields.Many2one(comodel_name='product.product')
    account_date = fields.Date()
    amount = fields.Float(digits=dp.get_precision('Product Price'))
    type = fields.Selection(string="Type", selection=[('sale', 'Sale'), ('purchase', 'Purchase'), ], required=False, )
    import_id = fields.Many2one(comodel_name="belfius.import",ondelete='cascade')

    def create_partner(self, data):
        _logger.info('create_partner')
        res_partner = self.env['res.partner']
        res_country = self.env['res.country']
        bank_vals = {}
        partner_vals = {'name': data.get('partner_name', ''), 'street': data.get('partner_street', '')}
        if data.get('partner_zip_city', ''):
            zip = [int(s) for s in data.get('partner_zip_city').split() if s.isdigit()]
            city = [s for s in data.get('partner_zip_city').split() if not s.isdigit()]
            partner_vals['zip'] = zip[0]
            partner_vals['city'] = city[0]
        if data.get('partner_account', ''):
            bank_vals['acc_number'] = data.get('partner_account').encode(encoding='utf-8', errors='strict')
        if data.get('partner_country', ''):
            country = res_country.search([('code', '=', data.get('partner_country'))], limit=1)
            if country:
                partner_vals['country_id'] = country.id
        if bank_vals:
            partner_vals['bank_ids'] = [(0, 0, bank_vals)]
        if partner_vals:
            if 'name' in partner_vals and partner_vals['name']:
                return res_partner.create(partner_vals)
        return False

    def process_line_normal_receipt(self, data, import_id):
        _logger.info('process_line_normal')
        _logger.info(data)
        res_partner_bank = self.env['res.partner.bank']
        res_partner = self.env['res.partner']
        product_product = self.env['product.product']
        partner = product = False
        data_line = {'import_id': import_id,
                     'banking_receipt': data.get('banking_receipt', ''),
                     'transaction_number': data.get('transaction_number', ''), 'amount': data.get('amount', 0.0),
                     'description': data.get('description', ''), 'name': data.get('name', '')}

        if data.get('account_date', False):
            data_line['account_date'] = parser.parse(data.get('account_date'))
        if data.get('amount', False):
            if isinstance(data.get('amount'), str):
                data_line['amount'] = float(data.get('amount').replace(',', '.'))
            else:
                data_line['amount'] = data.get('amount')
        if data.get('partner_account', False):
            bank = res_partner_bank.search([('acc_number', '=ilike', data.get('partner_account'))], limit=1)
            if bank:
                partner = bank.partner_id
        if not partner and data.get('partner_name', False):
            partner_search = res_partner.search([('name', '=ilike', data.get('partner_name'))], limit=1)
            if partner_search:
                partner = partner_search
        if not partner:
            partner_create = self.create_partner(data)
            if partner_create:
                partner = partner_create
        if data.get('description', False):
            product_words = str(data.get('description')).split(" ")
            product = False
            for product_word in product_words:
                if product:
                    break
                product_search = product_product.search(
                    ['|', ('name', '=ilike', product_word), ('default_code', '=ilike', product_words)], limit=1)
                if product_search:
                    product = product_search
        if not partner:
            partner = self.env.ref('belfius_import.res_partner_unknown')
        if not product:
            product = self.env.ref('belfius_import.product_product_unknown')
        data_line['partner_id'] = partner.id
        data_line['product_id'] = product.id
        if data_line.get('amount',False):
            if data_line.get('amount') < 0.0:
                data_line['type'] = 'purchase'
            else:
                data_line['type'] = 'sale'
        return self.create(data_line)

    def process_line_mastercard_receipt(self, data, import_id):
        res_partner = self.env['res.partner']
        product_product = self.env['product.product']
        partner = product = False

        data_line = {'import_id': import_id,'name':data[2].value,'account_date':datetime.datetime.strptime(data[0].value, '%d/%m').replace(year=datetime.datetime.now().year)}
        amount = data[7].value.replace('EUR','')
        amount = amount.replace(',','.')

        if '-' in amount:
            amount = -float(amount.replace('-', '').strip())
            type = 'purchase'
        else:
            amount = float(amount.replace('+', '').strip())
            type = 'sale'

        data_line['amount'] = amount
        data_line['type'] = type

        partner_search = res_partner.search(['|',('name', '=ilike', data[2].value),('other_name','ilike',data[2].value)], limit=1)
        if partner_search:
            partner = partner_search

        if not partner:
            partner = res_partner.create({'name':data[2].value})

        product_search = product_product.search(['|',('name', '=ilike', data[2].value),('other_name','ilike',data[2].value)], limit=1)
        if product_search:
            product = product_search



        if not partner:
            partner = self.env.ref('belfius_import.res_partner_unknown')
        if not product:
            product = self.env.ref('belfius_import.product_product_unknown')
        data_line['partner_id'] = partner.id
        data_line['product_id'] = product.id
        return self.create(data_line)

    def create_invoice_line(self,invoice):
        self.ensure_one()
        if invoice.type == 'sale':
            account = invoice.journal_id.default_credit_account_id.id
        else:
            account = invoice.journal_id.default_debit_account_id.id
        return self.env['account.invoice.line'].create({'invoice_id': invoice.id, 'price_unit': self.amount, 'quantity': 1,
                'name':self.name,'description':self.description,'banking_receipt':self.banking_receipt,
                'transaction_number':self.transaction_number,'product_id':self.product_id.id,'account_id':account})
