# -*- coding: utf-8 -*-

import sys

from odoo import api, fields, models
from odoo.addons.website.models import ir_http
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
    event_availability = fields.Selection([
        ('always', 'Show availability on website'),
        ('threshold', 'Show availability below a threshold'),
    ], string='Event Availability', help='Adds an event availability status on the web product page.')
    event_available_threshold = fields.Integer(string='Availability Threshold', default=5)
    event_ids = fields.Many2many('event.event', string='Events', help='Buying the product will automatically register '
                                                                      'the user to the events.',
                                 compute='_compute_event_ids', inverse='_set_event_ids', store=True)

    @api.constrains('event_set_ok', 'type')
    def _check_event_set_type(self):
        """Check if the type of an Event Set is a Service.

        """
        if self.event_set_ok and self.type != 'service':
            raise ValidationError("The type of an Event Set must be a Service")

    @api.constrains('event_set_ok', 'product_variant_ids')
    def _check_event_set_variants(self):
        """Check if the there is not any existing relationships between the product variants of an Event Set and Event
        records before modifying the field.

        """
        if not self.event_set_ok and self.product_variant_ids and self.product_variant_ids.event_ids:
            raise ValidationError("All existing relationships between the product variants of an Event Set and Event "
                                  "records have to be removed before modifying Event Set field")

    @api.onchange('event_set_ok')
    def _onchange_event_set_ok(self):
        if self.event_set_ok:
            self.type = 'service'

    @api.depends('product_variant_ids', 'product_variant_ids.event_ids')
    def _compute_event_ids(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            # replaces all existing records in the set
            template.event_ids = [(6, 0, [event.id for event in template.product_variant_ids.event_ids])]
        for template in (self - unique_variants):
            # removes all records from the set
            template.event_ids = [(5,)]

    @api.depends('product_variant_ids', 'product_variant_ids.event_ids')
    def _set_event_ids(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            # replaces all existing records in the set
            template.product_variant_ids.event_ids = [(6, 0, [event.id for event in template.event_ids])]
        for template in (self - unique_variants):
            # removes all records from the set
            template.event_ids = [(5,)]

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False,
                              parent_combination=False, only_template=False):
        """Override function in order to add information.

        """
        combination_info = super(ProductTemplate, self)._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty, pricelist=pricelist,
            parent_combination=parent_combination, only_template=only_template
        )

        if not self.env.context.get('website_sale_event_set_get_quantity'):
            return combination_info

        if combination_info['product_id']:
            product = self.env['product.product'].sudo().browse(combination_info['product_id'])
            combination_info.update({
                'event_seats_availability': product.event_seats_availability,
                'event_seats_available': product.event_seats_available,
                'event_set_ok': product.event_set_ok,
                'event_availability': product.event_availability,
                'event_available_threshold': product.event_available_threshold,
                'product_template': product.product_tmpl_id.id,
                'cart_qty': product.cart_qty,
                'uom_name': product.uom_id.name,
            })
        else:
            product_template = self.sudo()
            combination_info.update({
                # 'event_seats_availability': 'unlimited',
                # 'event_seats_available': 0,
                'event_set_ok': product_template.event_set_ok,
                'event_availability': product_template.event_availability,
                'event_available_threshold': product_template.event_available_threshold,
                'product_template': product_template.id,
                'cart_qty': 0
            })

        return combination_info


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
    cart_qty = fields.Integer(compute='_compute_cart_qty')

    @api.onchange('event_set_ok')
    def _onchange_event_set_ok(self):
        """Redirection, inheritance mechanism hides the method on the model.

        """
        if self.event_set_ok:
            self.type = 'service'

    @api.depends('event_ids', 'event_ids.date_tz', 'event_ids.date_begin')
    def _compute_event_is_expired(self):
        # print('\n_compute_event_is_expired')
        for record in self:
            record.event_is_expired = False
            for event in record.event_ids:
                event = event.with_context(tz=event.date_tz)
                begin_tz = fields.Datetime.context_timestamp(event, event.date_begin)
                current_tz = fields.Datetime.context_timestamp(event, fields.Datetime.now())
                if begin_tz < current_tz:
                    record.event_is_expired = True
                    break
            # print(record.name, record.event_is_expired)

    # maybe use seats_expected?
    @api.depends('event_ids', 'event_ids.seats_availability', 'event_ids.seats_available')
    def _compute_event_seats(self):
        # print('\n_compute_event_seats')
        for record in self:
            limited = False
            qty = sys.maxsize
            # print('record: ', record.id, record.name, [x.name for x in record.product_template_attribute_value_ids])
            for event in record.event_ids:
                # print('\tevent: :', event.id, event.name, event.seats_availability, event.seats_available)
                if event.seats_availability == 'limited' and event.seats_available < qty:
                    limited = True
                    qty = event.seats_available
            record.event_seats_availability = limited and 'limited' or 'unlimited'
            record.event_seats_available = limited and qty or 0
            # print('\t', record.event_seats_availability, record.event_seats_available)

    def _compute_cart_qty(self):
        website = ir_http.get_request_website()
        if not website:
            self.cart_qty = 0
            return
        cart = website.sale_get_order()
        for product in self:
            product.cart_qty = sum(cart.order_line.filtered(lambda p: p.product_id.id == product.id).mapped('product_uom_qty')) if cart else 0
