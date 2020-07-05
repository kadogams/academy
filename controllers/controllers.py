# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging


_logger = logging.getLogger(__name__)


class UpdateBillingFields(WebsiteSale):
    """Override the mandatory fields during the billing process.
    """
    def _get_mandatory_billing_fields(self):
        return ["name", "email", "phone"]


class Academy(http.Controller):
    @http.route('/inscription/', auth='public', website=True)
    def index(self, **kw):
        tmp = http.request.env['product.attribute']
        print('aaa:')
        for x in tmp:
            print(tmp.name)

        products = http.request.env['product.template']
        # for p in products.search([]):
        #     print(p.name)
        #     for ptal in p.attribute_line_ids.value_ids:
        #         print(ptal.name)
        #         for v in ptal.ptav_product_variant_ids:
        #             v.ptav_product_variant_ids
        #     print('\n')
        return http.request.render('academy.inscription')


#     @http.route('/academy/academy/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('academy.listing', {
#             'root': '/academy/academy',
#             'objects': http.request.env['academy.academy'].search([]),
#         })

#     @http.route('/academy/academy/objects/<model("academy.academy"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('academy.object', {
#             'object': obj
#         })
