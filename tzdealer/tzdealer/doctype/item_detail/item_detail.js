// Copyright (c) 2019, TZCODE SRL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item Detail', {
	refresh: frm => {
		const triggers = ["set_query"];

		$.map(triggers, event => {
			frm.trigger(event);
		});
	},
	set_query: frm => {
		frm.set_query("item", event => {
			return {
				filters:{
					"item_type": ["in", "Vehicles, Vehicle Parts"]
				}
			}
		});
	}
});
