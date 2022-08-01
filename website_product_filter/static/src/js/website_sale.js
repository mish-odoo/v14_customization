odoo.define('website_product_filter.cart', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var _t = core._t;

    publicWidget.registry.WebsiteSale.include({
        events: _.extend({}, publicWidget.registry.WebsiteSale.prototype.events, {
            'change input[name="size_id"]': '_change_product_size',
            'change input[name="color_id"]': '_change_product_color',
        }),

        /**
         * @override
         */
        start: function () {
            var def = this._super.apply(this, arguments);
            var $first_color = this.$('input[name="color_id"]').first()
            if ($first_color.length > 0){
                $first_color.attr('checked','checked')
                this._change_product_color()
            }
            return def;
        },

        /**
         * Extracted to a method to be extendable by other modules
         *
         * @param {$.Element} $parent
         */
        _getProductId: function ($parent) {
            return parseInt($parent.find('.product_id').val());
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {Event} ev
         */
        _onChangeCountry: function (ev) {
            this._super.apply(this, arguments);
            this._update_zip_code();
        },

        /**
         * @private
         */
        _update_zip_code: function(){
            this._rpc({
                route: "/shop/default_zip_infos/" + $("#country_id").val(),
            }).then(function (data) {
                $("input[name='zip']").val(data.default_zip_code)
            });
        },

        /**
         * @private
         * @param {Event} ev
         */
        _change_product_size: function(ev){
            this._change_identity_product_filter();
        },

        /**
         * @private
         */
        _change_product_color: function(ev){
            this._change_identity_product_filter();
        },
        /**
         * @see onChangeVariant
         *
         * @private
         * @override
         * @param {Event} ev
         * @returns {Deferred}
         */
        _getCombinationInfo: async function (ev) {
            var $parent = $(ev.target).closest('.js_product');
            if ($parent.find("input[name='identity_product']")) {
                let identity_product = $parent.find("input[name='identity_product']").val()
                if (identity_product) {
                    return await this._change_identity_product_filter();
                }
            }
            return this._super.apply(this, arguments);
        },
        _change_identity_product_filter: async function () {
            var self = this;
            var $size_id = this.$('input[name="size_id"]:checked');
            var sizeID = $size_id.val();
            var $color_id = this.$('input[name="color_id"]:checked');
            var colorID = $color_id.val();

            if (colorID > 0){
                var $parent = this.$('input[name="color_id"]').closest('.js_product');
                var qty = $parent.find('input[name="add_qty"]').val();
                var productTemplateId = parseInt($parent.find('.product_template_id').val());

                return await ajax.jsonRpc('/website_sale/get_product_identity_info', 'call', {
                    'product_template_id': productTemplateId,
                    'product_id': this._getProductId($parent),
                    'add_qty': parseInt(qty),
                    'pricelist_id': this.pricelistId || false,
                    'size_id': sizeID || 0,
                    'color_id': colorID || 0,
                }).then(function (combinationData) {
                    self._onChangeCombination(false, $parent, combinationData);
                    self._disable_product_size($parent, combinationData.remaining_sizes)
                });
            }
        },

        _disable_product_size: function($parent, remaining_sizes) {
            var self = this;
            $parent
            .find('input, label', '#size_li')
            .removeClass('css_not_available')
            .removeAttr('disabled');
            remaining_sizes.forEach(size => {
                var $input = $parent
                    .find('input.size_radio_input_' + size);
                    $input.addClass('css_not_available');
                    $input.closest('label').addClass('css_not_available');
                    $input.attr('disabled', 'disabled');
            });
        }

    })
});
