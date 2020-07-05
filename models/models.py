# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    """Add a description tooltip attribute to the product template. The description will be displayed as a
    Bootstrap tooltip when hovering over the product on the shop page.
    """
    _inherit = "product.template"

    description_tooltip = fields.Text(
        'Tooltip Description', translate=True,
        help="An additional description of the Product that you want to communicate to your customers. "
             "This description will be displayed when hovering over the product on the shop page."
    )

    def _get_description_tooltip(self):
        """Return its `description_tooltip` attribute value.
        """
        return self.description_tooltip


class ProductAttributeValue(models.Model):
    """Add a limit date attribute to the product variants.
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
