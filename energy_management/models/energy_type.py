from odoo import models, fields, api

class EnergyType(models.Model):
    _name = 'energy.type'

    name = fields.Char(required=True, )