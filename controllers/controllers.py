# -*- coding: utf-8 -*-
from odoo import http
import requests
import json

import logging
_logging = _logger = logging.getLogger(__name__)

class Oruschat(http.Controller):

    @http.route('/oruschat/contact', auth='public', csrf=False, methods=['POST'], type='json')
    def oruschat_post(self, **kw):
        data = (json.loads((http.request.httprequest.data).decode('utf-8'))).get('data')

        header = http.request.httprequest.headers
        args = http.request.httprequest.args
        
        status_response = True
        name = data.get('name')
        agent_email = data.get('agent_email')
        email = data.get('email')
        mobile = data.get('mobile')
        product_name = data.get('product_name')
        source = data.get('source')
        oruschat_id = data.get('contact_id')
         
        
        if (oruschat_id in [False, None, ""]):
            status_response = False
            response = {'error' : 'Invalid contact_id'}
            return http.Response({'response':response}, 404)
        else:
            pass
        
        partner_ids = http.request.env['res.partner'].sudo().search([
            ('oruschat_id', '=', oruschat_id)
        ])
        
        user_id = http.request.env['res.users'].sudo().search([
            ('partner_id.email', '=', agent_email)
        ])
        
        source_id = http.request.env['utm.source'].sudo().search([
            ('name', 'ilike', source)
        ])
        
        for partner_id in partner_ids:
            lead_id = http.request.env['crm.lead'].sudo().create({
                    'name' : name,
                    'email_from' : email,
                    'user_id' : user_id.id,
                    'phone' : mobile,
                    'source_id' : source_id.id,
                    'partner_id' : partner_id.id,
                    'type' : 'lead'
            })

        return http.Response(data, 200)
        
    @http.route('/oruschat/contact', auth='public', csrf=False, methods=['GET'])
    def oruschat_get(self, **kw):
        
        data = http.request.httprequest.data
        header = http.request.httprequest.headers
        args = http.request.httprequest.args
        
        key = header.get('key')
        phone = header.get('phone')
        if phone is not [False, None] and str(phone)[0] == "+":
            phone = phone[1:]

        email = header.get('email')
        oruschat_id = header.get('contact-id')
        company_int = header.get('company-id') or 1
        
        if oruschat_id in [False, None]:
            data = {'error': 'No Oruschat id sent'}
            
            headers = {
                'content-type' : 'application/json'
            }

            return http.Response( json.dumps(data), status=404, headers=headers,)   

        
        data = self.get_partner( [ ('oruschat_id', '=', oruschat_id) ] )

        if data.get('error') != {}:
            data = self.get_partner([ ('phone', '=', phone), ('phone', 'not in', [False, None])  ])
        
        if data.get('error') != {}:
            data = self.get_partner([ ('email', '=', email), ('email', 'not in', [False, None])  ])
        
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
        
        headers = {
            'content-type' : 'application/json'
        }
        
        return http.Response( json.dumps(data),status,headers, )
    
    def get_partner(self, filter1):
        #revisar el limite
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
    