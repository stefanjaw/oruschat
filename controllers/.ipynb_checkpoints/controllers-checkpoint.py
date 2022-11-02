# -*- coding: utf-8 -*-
from odoo import http

import json

import logging
_logging = _logger = logging.getLogger(__name__)

class Oruschat(http.Controller):

     @http.route('/oruschat/oruschat/', auth='public', csrf=False)
     def index(self, **kw):
        
        _logging.info(f"DEF11  dir: {dir(self)}\n self: {self}\n kw:{kw}\n")
        
        data = http.request.httprequest.data
        header = http.request.httprequest.headers
        args = http.request.httprequest.args
        
        msg = f"DEF18 data: {data}\n header: {header}\n args: {args}\n"

        _logging.info( msg )
        
        key = header.get('key')
        phone = header.get('phone')
        email = header.get('email')
        oruschat_id = header.get('contact-id')
        company_int = header.get('company-id') or 1
        
        _logging.info(f"DEF28 phone: {phone}")
        partner_data = http.request.env['res.partner'].sudo().search([
            ('phone', '=', phone),
            #('id', '=', 41)
        ],limit=1)
        # Utilizar search_read
        _logging.info(f"DEF34 phone: {partner_data}")

        msg = f"DEF36: partner_data: {partner_data.ids} other: {partner_data}"
        
        if len(partner_data) == 0:
            return http.Response("", status=404)
        elif len(partner_data) > 1:
            data = { "Error": "Many Users Found" }
            return http.Response( json.dumps(data), status=404)
        else:
            pass

        
        data = { data: {
                    'name': partner_data.name ,
                    'contact_id': 'PENDIENTE',
                    'agent_email': partner_data.user_id.partner_id.name,
                }
        }
        
        data = json.dumps(data)
        _logging.info(f"DEF55 data: {data}")
        
        return http.Response( , status=200)
        
        

'''
     @http.route('/oruschat/oruschat/objects/', auth='public')
     def list(self, **kw):
         return http.request.render('oruschat.listing', {
             'root': '/oruschat/oruschat',
             'objects': http.request.env['oruschat.oruschat'].search([]),
         })

     @http.route('/oruschat/oruschat/objects/<model("oruschat.oruschat"):obj>/', auth='public')
     def object(self, obj, **kw):
         return http.request.render('oruschat.object', {
             'object': obj
         })
'''