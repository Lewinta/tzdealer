frappe.ui.form.on("Warehouse", {
	refresh: frm => {
		frm.trigger("add_custom_fields");
	},
	add_custom_fields: frm => {
		cur_frm.add_custom_button("Default to No Default", () => {
			frm.trigger("toggle_default");
		});
	},
	toggle_default: frm => {
		frm.set_value("default", !frm.doc.default);
		frm.save_or_update();
	}
});