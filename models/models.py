# -*- coding: utf-8 -*-

import sys

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    """Add a description tooltip attribute to the product template. The description will be displayed as a
    Bootstrap tooltip when hovering over the product on the shop page.
    """
    _inherit = "product.template"

    """Description tooltip"""
    description_tooltip = fields.Text(
        'Tooltip Description', translate=True,
        help="An additional description of the Product that you want to communicate to your customers. "
             "This description will be displayed when hovering over the product on the shop page."
    )

    def _get_description_tooltip(self):
        """Return its `description_tooltip` attribute value.
        """
        return self.description_tooltip

    """Event set"""
    event_set_ok = fields.Boolean(string='Is an Event Set',
                                  help="If checked this product automatically creates an event registration at the "
                                       "sales order confirmation.")

    @api.onchange('event_set_ok')
    def _onchange_event_set_ok(self):
        if self.event_set_ok:
            self.type = 'service'

    @api.constrains('event_set_ok', 'type')
    def _check_description(self):
        if self.event_set_ok and self.type != 'service':
            raise ValidationError("The type of an Event Set must be a Service")


class ProductProduct(models.Model):
    _inherit = "product.product"

    event_ids = fields.Many2many('event.event', string='Events',
                                 help='Buying the product will automatically register the user to the events.')
    event_seats_availability = fields.Selection([('limited', 'Limited'), ('unlimited', 'Unlimited')],
                                                string='Available Seat', store=True, readonly=True,
                                                compute='_compute_event_seats')
    event_seats_available = fields.Integer('Available Seats', store=True, readonly=True,
                                           compute='_compute_event_seats')
    event_is_expired = fields.Boolean('Event Expired', readonly=True, compute='_compute_event_is_expired',
                                      help='Check if one or more events are expired')

    @api.onchange('event_set_ok')
    def _onchange_event_set_ok(self):
        """Redirection, inheritance mechanism hides the method on the model."""
        if self.event_set_ok:
            self.type = 'service'
            # Remove all records from event_ids
            self.event_ids = [(5, 0, 0)]
        print('\nonchange: ', self.event_seats_availability, self.event_seats_available)

    # maybe use seats_expected?
    @api.depends('event_set_ok', 'event_ids.seats_availability', 'event_ids.seats_available')
    def _compute_event_seats(self):
        print('\n_compute_event_seats')
        for record in self:
            limited = False
            qty = sys.maxsize
            print('record: ', record.id, record.name)
            for event in record.event_ids:
                print('\tevent: :', event.id, event.name, event.seats_availability, event.seats_available)
                if event.seats_availability == 'limited' and event.seats_available < qty:
                    limited = True
                    qty = event.seats_available
            record.event_seats_availability = limited and 'limited' or 'unlimited'
            record.event_seats_available = limited and qty or 0
            print('\t', record.event_seats_availability, record.event_seats_available)

    @api.depends('event_ids.date_tz', 'event_ids.date_begin')
    def _compute_event_is_expired(self):
        print('\n_compute_event_is_expired')
        for record in self:
            record.event_is_expired = False
            for event in record.event_ids:
                event = event.with_context(tz=event.date_tz)
                begin_tz = fields.Datetime.context_timestamp(event, event.date_begin)
                current_tz = fields.Datetime.context_timestamp(event, fields.Datetime.now())
                if begin_tz < current_tz:
                    record.event_is_expired = True
                    break
            print(record.name, record.event_is_expired)


class ProductAttributeValue(models.Model):
    """Add a limit date attribute to the product attributes.
    """
    _inherit = "product.attribute.value"

    limit_date = fields.Datetime('Limit date', translate=True, help='Maximum availability date of the variant.')


class ProductTemplateAttributeValue(models.Model):
    """Take into account the `limit_date` to define if the attribute is active or not.
    """
    _inherit = "product.template.attribute.value"

    def _only_active(self):
        """Return false if `ptav_active` is set to False or if `limit_date` is set and is expired.
        """
        return self.filtered(lambda ptav: ptav.ptav_active
                                          and (not ptav.product_attribute_value_id.limit_date
                                               or ptav.product_attribute_value_id.limit_date > fields.Datetime.now()))

# class academy(models.Model):
#     _name = 'academy.academy'
#     _description = 'academy.academy'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
