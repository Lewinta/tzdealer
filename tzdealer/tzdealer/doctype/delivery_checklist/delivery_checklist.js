// Copyright (c) 2020, TZCODE SRL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Delivery Checklist', {
	setup: frm => {
		frm.set_query("vehicle", event => {
			return {
				"filters": {
					"item_type": "Vehicles"
				}
			}
		});
		if(frm.is_new())
			frm.trigger("load_checklist");
	},
	type: frm => {
		frm.call("get_items").then(() => refresh_field("checklist"));
	}
});

frappe.ui.form.on("Delivery Checklist Item", {
	done: (frm, cdt, cdn) => {
		row = locals[cdt][cdn];
		if (row.done == 1)
			frappe.model.set_value(cdt, cdn, "notes", "DONE");
		else
			frappe.model.set_value(cdt, cdn, "notes", "");
	}
});