# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    oruschat_id = fields.Char()

