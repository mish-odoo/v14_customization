# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class CustomWebsiteSale(WebsiteSale):

    def _prepare_product_values(self, product, category, search, **kwargs):
        res = super(CustomWebsiteSale, self)._prepare_product_values(product, category, search, **kwargs)
        if product._has_identity_products():
            res['color'] = res['product'].color_id
            res['size'] = res['product'].size_id
            main_identity_product = request.env['product.template'].search([
                ('ecommerce_identity_group_id','=',res['product'].ecommerce_identity_group_id.id),
                ('color_id','=',False),
                ('size_id','=',False)
            ], limit=1)
            res['product'] = main_identity_product
            res['main_object'] = main_identity_product
        return res

    def _get_pricelist(self, pricelist_id, pricelist_fallback=False):
        return request.env['product.pricelist'].browse(int(pricelist_id or 0))

    @http.route(['/website_sale/get_product_identity_info'], type='json', auth="user", methods=['POST'])
    def get_product_identity_info(self, product_template_id, product_id, add_qty, pricelist_id, size_id, color_id, **kw):
        combination = request.env['product.template.attribute.value']
        pricelist = self._get_pricelist(pricelist_id)
        ProductTemplate = request.env['product.template']
        if 'context' in kw:
            ProductTemplate = request.env['product.template'].with_context(**kw.get('context'))
        product_template = ProductTemplate.browse(int(product_template_id))
        if size_id or color_id:
            product = request.env['product.product'].search([
                ('ecommerce_identity_group_id','=',product_template.ecommerce_identity_group_id.id),
                ('color_id','=',int(color_id or 0)),
            ], limit=1)
            all_sizes = product_template._get_identity_group_sizes()
            product_for_sizes = request.env['product.product'].search([
                ('ecommerce_identity_group_id','=',product_template.ecommerce_identity_group_id.id),
                ('color_id','=',int(color_id or 0)),
            ])
            available_sizes = product_for_sizes.mapped('size_id')
            remaining_sizes = all_sizes - available_sizes
            res = product_template._get_combination_info(combination, int(product.id or 0), int(add_qty or 1), pricelist)
            if not product:
                res['is_combination_possible'] = False
            product_image_ids = request.env['product.image'].search([('ecommerce_identity_group_id','=',product_template.ecommerce_identity_group_id.id),
                ('color_id','=',int(color_id or 0))])
            if product:
                carousel_view = request.env['ir.ui.view']._render_template('website_product_filter.product_image_grid',
                    values={
                        'product_image_ids': product_image_ids,
                    })
                res['carousel'] = carousel_view
            res['remaining_sizes'] = remaining_sizes.ids
        return res

    def checkout_form_validate(self, mode, all_form_values, data):
        error, error_message = super(CustomWebsiteSale, self).checkout_form_validate(mode, all_form_values, data)
        country_code = request.env['res.country'].browse(data.get('country_id')).code
        mobile_number = data.get('phone')
        if country_code == 'IL' or country_code == 'PS':
            if not mobile_number.isdigit():
                error["phone"] = 'error'
                error_message.append(_("Please Enter only digits as a Mobile Number"))
            if not mobile_number.startswith('97'):
                error["phone"] = 'error'
                error_message.append(_("Kindly check your Mobile Number, It should start with '97' "))
            if len(mobile_number) != 12:
                error["phone"] = 'error'
                error_message.append(_("Your Mobile Number should be 12 digits"))

        return error, error_message

    @http.route(['/shop/default_zip_infos/<model("res.country"):country>'], type='json', auth="public", methods=['POST'], website=True)
    def default_zip(self, country, **kw):
        return dict(
            default_zip_code=country.default_zip_code,
        )
