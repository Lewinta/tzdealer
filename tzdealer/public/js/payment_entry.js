frappe.ui.form.on("Payment Entry", {
	refresh: frm => {

	},
	_reference_no: frm => {
		let {_reference_no} = frm.doc;

		new_ref = _reference_no ? _reference_no : "";
		frm.set_value("reference_no", _reference_no);
	},
	mode_of_payment: frm => {
		if (frm.doc.mode_of_payment == "Cash"){
			frm.set_value("reference_no", "Cash");
			return
		}
		frm.trigger("_reference_no");
	},
	date: frm => {
		const {date, posting_date} = frm.doc;
		
		if (!date){
			frm.set_value("posting_date", "");
			return
		}
		frm.set_value("posting_date", date);

	},
	payment_type: frm => {
		if (frm.doc.payment_type == "Pay")
			frm.set_value("party_type", "Supplier")

		if (frm.doc.payment_type == "Receive")
			frm.set_value("party_type", "Customer")
	}
})