// Copyright (c) 2020, TZCODE SRL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vehicle Release', {
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
	// load_checklist: frm => {
	// 	frappe.db.get_list("Checklist Item").then(
	// 		items => {
	// 			$.map(items, item => {
	// 				frm.add_child("checklist", {"description": item.name})
	// 			});
	// 			frm.refresh_field("checklist");
	// 		}
	// 	);
	// }
});

frappe.ui.form.on("Vehicle Checklist Item", {
	done: (frm, cdt, cdn) => {
		row = locals[cdt][cdn];
		if (row.done == 1)
			frappe.model.set_value(cdt, cdn, "notes", "DONE");
		else
			frappe.model.set_value(cdt, cdn, "notes", "");
	}
});