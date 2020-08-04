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


# class EventSetController(http.Controller):
#
#     # @http.route(['/event/<model("event.event"):event>/registration/new'], type='json', auth="public", methods=['POST'], website=True)
#     def registration_new(self, event, **post):
#         tickets = self._process_tickets_details(post)
#         availability_check = True
#         if event.seats_availability == 'limited':
#             ordered_seats = 0
#             for ticket in tickets:
#                 ordered_seats += ticket['quantity']
#             if event.seats_available < ordered_seats:
#                 availability_check = False
#         if not tickets:
#             return False
#         return request.env['ir.ui.view'].render_template("website_event.registration_attendee_details", {'tickets': tickets, 'event': event, 'availability_check': availability_check})
