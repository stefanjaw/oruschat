# -*- coding: utf-8 -*-
from odoo import http
import requests
import json

import logging
_logging = _logger = logging.getLogger(__name__)

class Oruschat(http.Controller):

    @http.route('/oruschat/contact', auth='public', csrf=False, methods=['GET'])
    def index(self, **kw):
        
        data = http.request.httprequest.data
        header = http.request.httprequest.headers
        args = http.request.httprequest.args
        
        key = header.get('key')
        phone = header.get('phone')
        email = header.get('email')
        oruschat_id = header.get('contact-id')
        company_int = header.get('company-id') or 1
        
        if oruschat_id in [False, None]:
            data = {'error': 'No Oruschat id sent'}
            return http.Response( json.dumps(data), status=404)
        
        data = self.get_partner( [ ('oruschat_id', '=', oruschat_id) ] )

        if data.get('error') != {}:
            data = self.get_partner([ ('phone', '=', phone) ])
        
        if data.get('error') != {}:
            data = self.get_partner([ ('email', '=', email) ])
        
        try:
            partner_id = data.get('partner_id')
            if partner_id.oruschat_id != oruschat_id:
                partner_id.write({
                    'oruschat_id': oruschat_id,
                })
        except:
            pass

        data.pop('partner_id')
        status = data.get('status')
        data.pop('status')

        return http.Response( json.dumps(data), status )
    


    def get_partner(self, filter1):
        partner_id = http.request.env['res.partner'].sudo().search(
            filter1,
            limit=1
        )
        
        status = 200
        error = {}
        data = {}
        if len(partner_id) == 0:
            status = 404
            error = { "error": "Not Found" }
        elif len(partner_id) > 1:
            status = 404
            error = { "error": "Many Users Found" }
        else:
            data = {'name': partner_id.name ,
                    'contact_id': partner_id.oruschat_id,
                    'agent_email': partner_id.user_id.partner_id.email,
                   }

        return {'data': data, 'status': status, 'error': error, 'partner_id': partner_id}
    

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