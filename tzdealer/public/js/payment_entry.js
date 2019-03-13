frappe.ui.form.on("Payment Entry", {
	refresh: frm => {

	},
	payment_type: frm => {
		if (frm.doc.payment_type == "Pay")
			frm.set_value("party_type", "Supplier")

		if (frm.doc.payment_type == "Receive")
			frm.set_value("party_type", "Customer")
	}
})