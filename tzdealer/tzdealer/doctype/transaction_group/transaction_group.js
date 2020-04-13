// Copyright (c) 2019, TZCODE SRL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Transaction Group', {
	refresh: function(frm) {
		frm.trigger("set_queries");
		
	},
	set_queries: frm => {
		frm.set_query("account", function () {
			return {
				"filters": {
					"company": frm.doc.company
				}
			}
		});
	},
	company: frm => {
		frm.set_value("account", "");
		frm.trigger("set_queries");
	}
});
