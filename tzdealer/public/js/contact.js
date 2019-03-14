frappe.ui.form.on("Contact", {
	create_user: frm => {
		frappe.call({
			"method": "tzdealer.hook.contact.create_user",
			"args": {
				"doc": frm.doc
			},
			"callback": response => {
				frm.reload_doc();
			}
		})
	}
});
