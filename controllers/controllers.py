# -*- coding: utf-8 -*-
from odoo import http
import requests
import json

import logging
_logging = _logger = logging.getLogger(__name__)

class Oruschat(http.Controller): 

    
    
    @http.route('/oruschat/lead', auth='public', csrf=False, methods=['POST'], type='json')
    def oruschat_post(self, **kw):
    
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
        params = {}
        
        if oruschat_id not in aux_null : params['oruschat_id'] = oruschat_id
        if email not in aux_null : params['email'] = email  
        if phone not in aux_null : params['phone'] = phone  
        
        partner_id = self.get_partner_id(params)
        if partner_id not in aux_null and len(partner_id) == 1:
            partner_id.write(params)
        if len(partner_id) < 1:
            params['name'] = contact_name
            partner_id = self.create_partner(params)
             
                
        if agent_email not in aux_null:
            user_id = (http.request.env['res.users'].sudo().search([
            ('name', '=', agent_email )
            ]))
            if user_id not in aux_null and len(user_id) > 0:
                lead_data['user_id'] = user_id.id 
                
         
        
        if  category_name not in aux_null:
            category_name_id = (http.request.env['crm.tag'].sudo().search([
            ('name', 'ilike', category_name )
            ]))
            if category_name_id not in aux_null or len(category_name_id) == 0:
                lead_data['tag_ids'] = category_name_id.id 

        if  product_name not in aux_null:
            product_id = (http.request.env['product.product'].sudo().search([
            ('name', 'ilike', product_name )
            ]))
            if product_id not in aux_null and len(product_id) > 0:
                lead_data['product_id'] = product_id.id 
        
        if  source not in aux_null:
            source_id = (http.request.env['utm.source'].sudo().search([
            ('name', 'ilike', source )
            ]))
            if source_id not in aux_null and len(source_id) > 0:
                lead_data['source_id'] = source_id.id 
        
        if  medium not in aux_null:
            medium_id = (http.request.env['utm.medium'].sudo().search([
            ('name', 'ilike', medium )
            ]))
            if medium_id not in aux_null and len(medium_id) > 0:
                lead_data['medium_id'] = medium_id.id
        
        
        
        if  lead_name not in aux_null: 
            lead_data['name'] = lead_name
            
        if  contact_name not in aux_null: 
            lead_data['contact_name'] = contact_name
            
        if  email not in aux_null: 
            lead_data['email_from'] = email
            
        if  phone not in aux_null: 
            lead_data['phone'] = phone
            
        if  active not in aux_null: 
            lead_data['active'] = active
     
         
        lead_id = (http.request.env['crm.lead'].sudo().create(lead_data))
       
         
        campaigns_leads = http.request.env['crm.lead'].sudo().search([
            ('campaign_id.id', '=', lead_id.campaign_id.id)
        ])
                     
           
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
    
     
        
           
    
    
    
    def get_partner_id(self, params):
        partner_id = {}
        for key in params:
            partner_id = http.request.env['res.partner'].sudo().search([
                (key, '=', params[key])
            ])
            if(len(partner_id) == 1):
                break
        
        return partner_id
        
        
    
    def create_partner(self, params):

        partner_id = http.request.env['res.partner'].sudo().create(params)
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

    
