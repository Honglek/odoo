from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    province_name = fields.Text(string='Province', max=100)
    district_name = fields.Char(string='District', max=100)
