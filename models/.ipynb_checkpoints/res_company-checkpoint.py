# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    oruschat_key = fields.Char()

