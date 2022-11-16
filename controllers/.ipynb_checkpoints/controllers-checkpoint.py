# -*- coding: utf-8 -*-
from odoo import http
import requests
import json

import logging
_logging = _logger = logging.getLogger(__name__)

class Oruschat(http.Controller):

    @http.route('/oruschat/lead', auth='public', csrf=False, methods=['POST'], type='json')
    def oruschat_post(self, **kw):
        
        #Falta la validacion dek key

        
        # data = (json.loads((http.request.httprequest.data).decode('utf-8'))).get('data')
        data = (json.loads((http.request.httprequest.data).decode('utf-8'))).get('data')
        header = http.request.httprequest.headers
        
        args = http.request.httprequest.args
        
        _logging.info(f"DEF15 data: {data}\n")

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
        
        #Se utiliza para realizar las validaciones y que el codigo este mas limpio
        aux_null = [False, None, ""]
        
        
        if  category_name in aux_null:
            category_name_id = ""
        else:
            category_name_id = (http.request.env['crm.tag'].sudo().search([
            ('name', 'ilike', category_name )
            ])).id
        
        _logging.info(f"DEF49 ========")
        
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
        
        _logging.info(f"DEF67=======")
        if product_name in aux_null:
            product_id = ""
        else:
            product_id = (http.request.env['product.product'].sudo().search([
            ('name', 'ilike', product_name)
            ]))
        
        
        if agent_email in aux_null:
            user_id = ""
        else:
            user_id = (http.request.env['res.users'].sudo().search([
            ('partner_id.email', '=', agent_email)
            ]))
            
        _logging.info(f"DEF83======")
        if source in aux_null:
            source_id = ""
        else:
            source_id = (http.request.env['utm.source'].sudo().search([
            ('name', 'ilike', source)
            ]))
        
        _logging.info(f"DEF91======")
        if medium in aux_null:
            medium_id = ""
        else:
            medium_id = (http.request.env['utm.medium'].sudo().search([
            ('name', 'ilike', medium)
            ]))
            
        
        _logging.info(f"DEF100====== partner_ids: {partner_ids}")
        #for partner_id in partner_ids:
        #    _logging.info(f"DEF102======")
        lead_id = http.request.env['crm.lead'].sudo().create({
                'name' : lead_name,
                #'tag_ids' : category_name_id.id,
                'product_id' : product_id.id,
                'contact_name' : contact_name,
                #'partner_id' : partner_id.id,
                'user_id' : user_id.id,
                'email_from' : email,
                'phone' : phone,

                'medium_id' : medium_id.id,
                'source_id' : source_id.id,
                'active' : active,
        })
        _logging.info(f"DEF117====== lead_id: {lead_id}")
        _logging.info(f"DEF118====== ")
        
        data = {
            'status' : True
        }
        
        headers = {
            'content-type' : 'application/json'
        }
        
        status=200
        response = "ALGO"  # json.dumps(data)
        
        return http.Response( response,status,headers, )
        
        
        
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
        oruschat_id = header.get('contact-id')
        company_int = header.get('company-id') or 1
        
        if oruschat_id in [False, None]:
            data = {'error': 'No Oruschat id sent'}
            
            headers = {
                'content-type' : 'application/json'
            }

            return http.Response( json.dumps(data), status=404, headers=headers,)   

        
        data = self.get_partner( [ ('oruschat_id', '=', oruschat_id) ] )
        _logging.info(f"DEF166 phone: {data}\n")
        if data.get('error') != {}:
            data = self.get_partner([ ('phone', '=', phone), ('phone', 'not in', [False, None])  ])
        _logging.info(f"DEF169 phone: {data}\n")
        if data.get('error') != {}:
            data = self.get_partner([ ('email', '=', email), ('email', 'not in', [False, None])  ])
        _logging.info(f"DEF172 phone: {data}\n")
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
    