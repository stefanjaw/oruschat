# -*- coding: utf-8 -*-
from odoo import http
import requests
import json

import logging
_logging = _logger = logging.getLogger(__name__)

class Oruschat(http.Controller): 

    
    
    @http.route('/oruschat/lead', auth='public', csrf=False, methods=['POST'], type='json')
    def oruschat_post(self, **kw):
        _logging.info(f"DEF15 oruschat_post================")
        
        data = (json.loads((http.request.httprequest.data).decode('utf-8'))).get('data')
        header = http.request.httprequest.headers
        args = http.request.httprequest.args

        status_response = True
        
        lead_name = data.get('lead_name')
        category_name = data.get('category_name')
        product_name = data.get('product_name')
        oruschat_id = data.get('contact_id')
        user_email = data.get('agent_email')
        partner_name = data.get('contact_name')
        partner_email = data.get('email')
        partner_phone = data.get('phone')
        campaign_name = data.get('campaign')
        
        medium = data.get('medium')
        source = data.get('source')
        active = data.get('active')
        
        aux_null = [False, None, ""]
        
        lead_data = {}
        lead_data['type'] = 'lead'
        
        user_id = self.get_user_id_by_email(user_email)
        if len(user_id) == 1: lead_data['user_id'] = user_id.id
        _logging.info(f"DEF43 user_id: {user_id.name}")
        
        partner_params = {}
        if oruschat_id: partner_params['oruschat_id'] = oruschat_id
        if partner_name: partner_params['name'] = partner_name
        if partner_email: partner_params['email'] = partner_email
        if partner_phone: partner_params['phone'] = partner_phone
        
        partner_id = self.get_update_partner_id(partner_params)
        if len(partner_id) == 0:
            partner_id = self.create_partner(partner_params)
            partner_id.write({'user_id': user_id.id})
        elif len(partner_id) > 1:
            _logging.info(f"DEF45 Condicion No debe Suceder ==============partner_id: {partner_id}\n\n")
            partner_id = partner_id[0]
        else:
            pass
        
        lead_data['partner_id'] = partner_id.id
        
        
        
        category_id = self.get_record_by_name( 'crm.tag', category_name )
        if len(category_id) == 1: lead_data['tag_ids'] = category_name_id.id

        product_id = self.get_record_by_name('product.product', product_name)
        if len(product_id) == 1: lead_data['product_id'] = product_id.id
        
        source_id = self.get_record_by_name('utm.source', source)
        if len(source_id) == 1: lead_data['source_id'] = source_id.id
        
        medium_id = self.get_record_by_name('utm.medium', medium)
        if len(medium_id) == 1: lead_data['medium_id'] = medium_id.id
        
        campaign_id = self.get_record_by_name('utm.campaign', campaign_name)
        if len(campaign_id) == 1: lead_data['campaign_id'] = campaign_id.id
        
        if lead_name not in aux_null: 
            lead_data['name'] = lead_name
            
        if partner_name: 
            lead_data['contact_name'] = partner_name
            
        if partner_email: 
            lead_data['email_from'] = partner_email
            
        if partner_phone: 
            lead_data['phone'] = partner_phone
            
        if active: 
            lead_data['active'] = active
        
        
        lead_id = (http.request.env['crm.lead'].sudo().with_context(create_lead = True).create(lead_data))
       
        data= {
            'status' : True
        }
        
        return json.dumps(data)


 
        
        
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

        params = {}
        if oruschat_id : params['oruschat_id'] = oruschat_id
        if email : params['email'] = email  
        if phone : params['phone'] = phone    
        
        
        
        partner_id = self.get_partner_id(params)
        
        if len(partner_id) == 1 and oruschat_id:
            partner_id.write({'oruschat_id' : oruschat_id})
            
        _logging.info(f"DEF157 partner_id oruschat_id: {partner_id}\n")
        

        
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
    
     
        
           
    
    
    
    def get_update_partner_id(self, params):
        partner_id = http.request.env['res.partner']
        for key in params:
            partner_id = http.request.env['res.partner'].sudo().search([
                (key, '=', params[key])
            ])
            if len(partner_id) == 1:
                break
        
        if len(partner_id) == 1:
            partner_id.write(params)
        
        return partner_id
        
        
    
    def create_partner(self, params):
        partner_id = http.request.env['res.partner'].sudo().create(params)
        return partner_id
    
    def get_user_id_by_email(self, email):
        if email:
            record_id = http.request.env['res.users'].sudo().search([
                ('partner_id.email', '=', email )
            ])
        else:
            record_id = http.request.env['res.users']
        return record_id
    
    def get_record_by_name( self, model, name ):
        if name:
            record_id = http.request.env[model].sudo().search([
                ('name', 'ilike', name )
            ])
        else:
            record_id = http.request.env[model]
        return record_id
    
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

    
