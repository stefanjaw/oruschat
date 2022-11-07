# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CrmLeadInherit(models.Model):
    _inherit = 'crm.lead'

    product_name = fields.Char()
