# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ProductColor(models.Model):
    _name = 'product.color'
    _description = 'Product Colors'

    name = fields.Char("Name")
    color = fields.Char(string='Color Index', help='Color to visulaize on Website')
    is_image = fields.Boolean(string="Image (?)")
    image = fields.Image(string="Image", help='Image to visulaize on Website')


class ProductSize(models.Model):
    _name = 'product.size'
    _description = 'Product Sizes'

    name = fields.Char("Name")
    sequence = fields.Integer("Sequence", help="Sequence in which the size will be displayed in website product view.")


class ProductIdentityGroup(models.Model):
    _name = 'ecommerce.identity.group'
    _description = 'Product Identity Group'

    name= fields.Char("Identity Name")
    image_count = fields.Integer(compute='_compute_image_count', string='Number of Images')
    product_image_ids = fields.One2many('product.image', 'ecommerce_identity_group_id', string='Product Images')

    @api.depends('product_image_ids')
    def _compute_image_count(self):
        for record in self:
            record.image_count = len(record.product_image_ids)

    def action_image_view(self):
        action = self.env["ir.actions.actions"]._for_xml_id('website_product_filter.action_product_upload_image_list')
        product_image = self.env['product.image'].search([('ecommerce_identity_group_id', '=', self.id)])
        action.update({
            'domain': [('ecommerce_identity_group_id', '=', self.id)],
            'context': {
                'default_ecommerce_identity_group_id': self.id,
            }
        })
        return action


class ProductSizeGuide(models.Model):
    _name = 'product.size.guide'
    _description = 'Product Size Guide'
    _rec_name = 'foot_length'

    foot_length = fields.Float(string='Foot Length')
    eu_size = fields.Float(string='EU Size')
    us_size = fields.Float(string='US Size')
    uk_size = fields.Float(string='UK Size')
