// odoo.define('hello_world.main', function (require) {  const AbstractAction = require('web.AbstractAction');  console.log(AbstractAction);});

odoo.define('fittext.main', function (require) {
'use strict';

var Dialog = require('web.Dialog');
var publicWidget = require('web.public.widget');

publicWidget.registry.HelloWorldPopup = publicWidget.Widget.extend({
    selector: '#wrapwrap',

    start: function () {
        Dialog.alert(this, "Hello, world!");
        return this._super.apply(this, arguments);
    },
})
});
