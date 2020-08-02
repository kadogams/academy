# -*- coding: utf-8 -*-

from odoo.addons.website_sale_stock.controllers.main import WebsiteSaleStock

from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError


class WebsiteSaleEventSet(WebsiteSaleStock):
    @http.route()
    def payment_transaction(self, **kwargs):
        """Payment transaction override to double check cart quantities before placing the order. Inherits
        WebsiteSaleStock in order to avoid conflict if the Stock module is also downloaded.
        """
        order = request.website.sale_get_order()
        values = []
        for line in order.order_line:
            if line.product_id.event_set_ok and line.product_id.event_seats_availability == 'limited':
                cart_qty = int(sum(order.order_line.filtered(lambda p: p.product_id.id == line.product_id.id).mapped('product_uom_qty')))
                avl_qty = line.product_id.event_seats_available
                if cart_qty > avl_qty:
                    values.append(_('You ask for %s products but only %s is available') % (cart_qty, avl_qty if avl_qty > 0 else 0))
        if values:
            raise ValidationError('. '.join(values) + '.')
        return super(WebsiteSaleEventSet, self).payment_transaction(**kwargs)
