# -*- coding: utf-8 -*-
from odoo import http
import requests
import json

import logging
_logging = _logger = logging.getLogger(__name__)

class Oruschat(http.Controller):

    @http.route('/oruschat/lead', auth='public', csrf=False, methods=['POST'], type='json')
    def oruschat_post(self, **kw):

        
        # data = (json.loads((http.request.httprequest.data).decode('utf-8'))).get('data')
        data = (json.loads((http.request.httprequest.data).decode('utf-8'))).get('data')
        header = http.request.httprequest.headers
        
        args = http.request.httprequest.args
        

        status_response = True
        
        lead_name = data.get('lead_name')
        category_name = data.get('category_name')
        product_name = data.get('product_name')
        contact_name = data.get('contact_name')
        oruschat_id = data.get('contact_id')
        agent_email = data.get('agent_email')
        email = data.get('email')
        phone = data.get('phone')
        
        medium = data.get('medium')
        source = data.get('source')
        active = data.get('active')
        
        aux_null = [False, None, ""]
        lead_data = {}
        
        if oruschat_id in aux_null:
            data = {
                'status' : False,
                'error': 'No Oruschat id sent'
            }
            headers = {
                'content-type' : 'application/json'
            }
            _logging.info(f"DEF61 ===========")
            return http.Response( json.dumps(data), status=404, headers=headers,)
        else:
            partner_ids = (http.request.env['res.partner'].sudo().search([
            ('oruschat_id', '=', oruschat_id)
            ]))
        
        
        
        if  category_name not in aux_null:
            category_name_id = (http.request.env['crm.tag'].sudo().search([
            ('name', 'ilike', category_name )
            ]))
            if category_name_id not in aux_null:
                lead_data['tag_ids'] = category_name_id.id 

        if  product_name not in aux_null:
            product_id = (http.request.env['product.product'].sudo().search([
            ('name', 'ilike', product_name )
            ]))
            if product_id not in aux_null:
                lead_data['product_id'] = product_id.id 
        
        if  agent_email not in aux_null:
            user_id = (http.request.env['res.users'].sudo().search([
            ('name', '=', agent_email )
            ]))
            if user_id not in aux_null:
                lead_data['user_id'] = user_id.id 
        
        if  source not in aux_null:
            source_id = (http.request.env['utm.source'].sudo().search([
            ('name', 'ilike', source )
            ]))
            if user_id not in aux_null:
                lead_data['source_id'] = source_id.id 
        
        if  medium not in aux_null:
            medium_id = (http.request.env['utm.medium'].sudo().search([
            ('name', 'ilike', medium )
            ]))
            if user_id not in aux_null:
                lead_data['medium_id'] = medium_id.id
        
        
        
        if  lead_name not in aux_null:
            lead_data['lead_name'] = lead_name
        
        if  contact_name not in aux_null:
            lead_data['contact_name'] = contact_name
            
        if  email not in aux_null:
            lead_data['email_from'] = email
        
        if  phone not in aux_null:
            lead_data['phone'] = phone
            
        if  active not in aux_null:
            lead_data['active'] = active
        
        
        for partner_id in partner_ids:
            lead_id = http.request.env['crm.lead'].sudo().create(lead_data)
        
        data = {
            'status' : True
        }
        
        http.Response.status = "400 algo"
        return json.dumps(data) #http.Response( response,status,headers, )


        
        
        
    #/////////////////////////////////////////////////////////////////////////////////////////////    
        
        
        
    @http.route('/oruschat/contact', auth='public', csrf=False, methods=['GET'])
    def oruschat_get(self, **kw):
        
        data = http.request.httprequest.data
        header = http.request.httprequest.headers
        args = http.request.httprequest.args
        
        key = header.get('key')
        _logging.info(f"DEF145 key: {key}\n")
        phone = header.get('phone')

        if phone not in [False, None] and str(phone)[0] == "+":
            phone = phone[1:]
        _logging.info(f"DEF150 phone: {phone}\n")
        email = header.get('email')
        _logging.info(f"DEF143 email: {email}\n")
        oruschat_id = header.get('contact-id')
        company_int = header.get('company-id') or 1
        
        if oruschat_id in [False, None]:
            data = {'error': 'No Oruschat id sent'}
            
            headers = {
                'content-type' : 'application/json'
            }

            return http.Response( json.dumps(data), status=404, headers=headers,)   

        
        partner_id = self.get_partner_id( [ ('oruschat_id', '=', oruschat_id) ] )
        _logging.info(f"DEF157 partner_id oruschat_id: {partner_id}\n")
        
        if len(partner_id) == 0 and phone not in [False, None]:
            partner_id = self.get_partner_id([ ('phone', '=', phone), ])
        _logging.info(f"DEF162 partner_id phone: {partner_id}\n")
        
        if len(partner_id) == 0 and email not in [False, None]:
            partner_id = self.get_partner_id([ ('email', '=', email), ('email', 'not in', [False, None])  ])
        _logging.info(f"DEF166 partner_id email: {partner_id}\n")
        
        
        try:
            if partner_id.oruschat_id != oruschat_id:
                partner_id.write({
                    'oruschat_id': oruschat_id,
                })
        except:
            pass
        
        error = {}
        if len(partner_id) == 1:
            status = 200
            data =  {   'name': partner_id.name ,
                        'contact_id': partner_id.oruschat_id,
                    }
            if len( partner_id.user_id ) > 0:
                data[ 'agent_email' ] = partner_id.user_id.partner_id.email
            elif len( partner_id.user_id ) == 0:
                data[ 'agent_email' ] = False
                
        elif len(partner_id) == 0:
            status = 404
            data = {  }
            error = "Not Found"
        elif len(partner_id) > 1:
            status = 404
            data = {  }
            error = "Many Users Found"
            
        headers = {
            'content-type' : 'application/json'
        }
        
        output = {'data': data, 'error': error}
        _logging.info(f"DEF202 output: {output}\n")
        return http.Response( json.dumps(output), status, headers, )
    
    def get_partner_id(self, filter1):
        partner_id = http.request.env['res.partner'].sudo().search(
            filter1,
            limit=1
        )
        
        return partner_id
        
#         status = 200
#         error = {}
#         data = {}
#         if len(partner_id) == 0:
# #             status = 404
# #             error = { "error": "Not Found" }
#         elif len(partner_id) > 1:
#             status = 404
#             error = { "error": "Many Users Found" }
#         else:
#             pass
#             data = {'name': partner_id.name ,
#                     'contact_id': partner_id.oruschat_id,
#                     'agent_email': partner_id.user_id.partner_id.email,
#                    }
        
        
#         return {'data': data, 'status': status, 'error': error, 'partner_id': partner_id}

    