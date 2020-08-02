# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo import http


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    event_set_ok = fields.Boolean(related='product_id.event_set_ok', readonly=True)

    def _update_registrations(self, confirm=True, cancel_to_draft=False, registration_data=None):
        """
        """
        if confirm:
            print('\nSaleOrderLine._update_registrations')
            Registration = self.env['event.registration'].sudo()

            # obj = http.request.env['sale.order.line']
            # for so_line in obj.search([]):
            #     registration = {}
            #     print('so_line: ', so_line.id)
            #     registration['sale_order_line_id'] = so_line
            #     registration = Registration._prepare_attendee_values(registration)
            #     print(so_line.id, registration)

            # registration = {}
            # for so_line in self:
            #     registration['sale_order_line_id'] = so_line
            #     print('aaa', Registration._prepare_attendee_values(registration))

            registrations = Registration
            for so_line in self.filtered('event_set_ok'):
                print('event_set_ok')
                att_data = {'sale_order_line_id': so_line}
                att_data = Registration._prepare_attendee_values(att_data)
                for event in so_line.product_id.event_ids:
                    print('\n', so_line.id, att_data)
                    att_data.update({'event_id': event.id})
                    for count in range(int(so_line.product_uom_qty)):
                        registrations += Registration.create(att_data.copy())#.confirm_registration()

        return super(SaleOrderLine, self)._update_registrations(confirm, cancel_to_draft, registration_data)
