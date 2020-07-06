odoo.define('academy.fittext', function (require) {
    console.log('AbstractAction');
    $("#products_grid .description-hoverable").fitText();
});

// odoo.define('academy.main', function (require) {
// 'use strict';
//
// var Dialog = require('web.Dialog');
// var publicWidget = require('web.public.widget');
//
// publicWidget.registry.HelloWorldPopup = publicWidget.Widget.extend({
//     selector: '#wrapwrap',
//
//     start: function () {
//         Dialog.alert(this, "Hello, world!");
//         return this._super.apply(this, arguments);
//     },
// })
// });
