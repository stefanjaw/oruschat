# -*- coding: utf-8 -*-
from odoo import http
import requests
import json

import logging
_logging = _logger = logging.getLogger(__name__)

class Oruschat(http.Controller): 
    
    @http.route('/oruschat/lead', auth='public', csrf=False, methods=['POST'], type='json')
    def oruschat_post(self, **kw):
        partner_params = {}
        
        _logging.info(f"POST lead")
        data = (json.loads((http.request.httprequest.data).decode('utf-8'))).get('data')
        
        header = http.request.httprequest.headers
        args = http.request.httprequest.args
        description = f"data: {data}\n\nargs:{args}"
        status_response = True
        
        company_int = 1
        
        key = header.get('key')
        
        lead_name = data.get('lead_name')
        
        category_name = data.get('category_name')
        product_name = data.get('product_name')
        product_code = data.get('product_code')
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
        lead_data['description'] = description
        
        company_id = http.request.env['res.company'].sudo().search([
                ('id', '=', company_int)
        ])
        
        if company_id.oruschat_key != key:
            data = {
            'status' : False,
            'error' : 'INVALID KEY'
            }
            return data
        else:
            pass
        
        user_id = self.get_user_id_by_email(user_email)
        if len(user_id) == 1:
            lead_data['user_id'] = user_id.id
            partner_params['user_id'] = user_id.id
        
        if oruschat_id: partner_params['oruschat_id'] = oruschat_id
        if partner_name: partner_params['name'] = partner_name
        if partner_email: partner_params['email'] = partner_email
        if partner_phone: partner_params['phone'] = partner_phone
        
        partner_id = self.get_update_partner_id(partner_params)
        if len(partner_id) == 0 and len(partner_params) > 0:
            partner_id = self.create_partner(partner_params)
        elif len(partner_id) > 1:
            partner_id = partner_id[0]
        else:
            pass
        lead_data['partner_id'] = partner_id.id
        lead_data['user_id'] = partner_id.user_id.id
        
        category_id = self.get_record_by_name( 'crm.tag', category_name )
        if len(category_id) > 0: lead_data['tag_ids'] = [category_id[0].id]
        
        product_id = self.get_record_by_default_code('product.product', product_code)
        if len(product_id) > 0: lead_data['product_id'] = product_id[0].id
        
        if len(product_id) == 0:
            product_id = self.get_record_by_name('product.product', product_name)
            if len(product_id) > 0: lead_data['product_id'] = product_id[0].id
        
        source_id = self.get_record_by_name('utm.source', source)
        if len(source_id) > 0: lead_data['source_id'] = source_id[0].id
        
        medium_id = self.get_record_by_name('utm.medium', medium)
        if len(medium_id) > 0: lead_data['medium_id'] = medium_id[0].id
        
        campaign_id = self.get_record_by_name('utm.campaign', campaign_name)
        if len(campaign_id) > 0: lead_data['campaign_id'] = campaign_id[0].id
        
        if lead_name not in aux_null: 
            lead_data['name'] = lead_name
        
        if lead_data.get('name') in aux_null: 
            lead_data['name'] = partner_name
            
        if lead_data.get('name') in aux_null: 
            lead_data['name'] = partner_phone
        
        if partner_name:
            lead_data['contact_name'] = partner_name
            
        if partner_email: 
            lead_data['email_from'] = partner_email
            
        if partner_phone: 
            lead_data['phone'] = partner_phone
            
        if active: 
            lead_data['active'] = active
        
        is_salesperson_secuential = True
        if lead_data.get('user_id'):
            is_salesperson_secuential = False
        
        lead_id = self.lead_existing(lead_data)
        
        if len(lead_id) > 0:
            _logger.info(f"      Updating CRM: {lead_id}")
            is_salesperson_secuential = False
            
            lead_id.with_context(
                salesperson_secuential = is_salesperson_secuential).write(lead_data)
        else:
            lead_id = (http.request.env['crm.lead'].sudo().with_context(
                salesperson_secuential = is_salesperson_secuential).create(lead_data)
            )
            _logging.info(f"  Created: {lead_id} for {partner_id}")
        
        data= {
            'status' : True
        }
        
        return data

        
    @http.route('/oruschat/contact', auth='public', csrf=False, methods=['GET'])
    def oruschat_get(self, **kw):
        _logging.info(f"GET contact")
        data = http.request.httprequest.data
        header = http.request.httprequest.headers
        args = http.request.httprequest.args
        
        key = header.get('key')

        phone = header.get('phone')

        if phone not in [False, None] and str(phone)[0] == "+":
            phone = phone[1:]

        email = header.get('email')
        oruschat_id = header.get('contact-id')
        company_int = header.get('company-id') or 1
        
        company_id = http.request.env['res.company'].sudo().search([
                ('id', '=', company_int)
        ])
        
        if company_id.oruschat_key != key:
            data = {
            'status' : False,
            'error' : 'INVALID KEY'
            }
            return json.dumps( {'data': data} )
        else:
            pass

        if oruschat_id in [False, None]:
            
            data = {'error': 'contact-id not sent'}
            
            headers = {
                'content-type' : 'application/json'
            }
            
            return http.Response( json.dumps(data), status=404, headers=headers,)   
        
        params = {}
        if oruschat_id : params['oruschat_id'] = oruschat_id
        if email : params['email'] = email  
        if phone : params['phone'] = phone    
        
        
        
        partner_id = self.get_update_partner_id(params)
        
        
        
        if len(partner_id) == 1 and oruschat_id:
            partner_id.write({'oruschat_id' : oruschat_id})
            

        

        
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
        
        return http.Response( json.dumps(output), status, headers, )
    
     
        
           
    
    
    
    def get_update_partner_id(self, params):
        
        partner_id = http.request.env['res.partner']
        for key in params:
            
            if key not in ["oruschat_id", "phone"]:
                continue
                
            partner_id = http.request.env['res.partner'].sudo().search([
                (key, '=', params[key])
            ], limit=1)
            
            if len(partner_id) == 0 and key == "phone":
                phone = params[key]
                
                partner_id =    http.request.env['res.partner'].sudo().search([
                                    ('phone', '=like', f'%{phone[-4:]}'),
                                    ('phone', '=like', f'%{phone[-8:-4]}%'),
                                ], limit=1)
            
            if len(partner_id) == 0 and key == "phone":
                phone = params[key]
                
                partner_id =    http.request.env['res.partner'].sudo().search([
                                    ('mobile', '=like', f'%{phone[-4:]}'),
                                    ('mobile', '=like', f'%{phone[-8:-4]}%')
                                ], limit=1)
            
            if len(partner_id) == 1:
                break
        
        if len(partner_id) == 1:
            phone = params.get('phone')
            rem_phone = False
            if str(phone[-4:]) in str(partner_id.phone) and str(phone[-8:-4]) in str(partner_id.phone):
                rem_phone = True
            if str(phone[-4:]) in str(partner_id.mobile) and str(phone[-8:-4]) in str(partner_id.mobile):
                rem_phone = True
            if rem_phone == True:
                params.pop('phone')
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
    
    def get_record_by_default_code( self, model, default_code ):
        if default_code:
            record_id = http.request.env[model].sudo().search([
                ('default_code', 'ilike', default_code )
            ])
        else:
            record_id = http.request.env[model]
        return record_id

    
    def lead_existing(self, lead_data):
        lead_ids = http.request.env['crm.lead'].sudo().search([
                        ('name',       '=', lead_data.get('name')  ),
                        ('email_from', '=', lead_data.get('email_from') ),
                        ('partner_id', '=', lead_data.get('partner_id') ),
                        ('medium_id', '=', lead_data.get('medium_id') ),
                        ('source_id', '=', lead_data.get('source_id') ),
                        ('user_id', '=', lead_data.get('user_id') ),
                    ],
                        limit=1
                    )
        return lead_ids