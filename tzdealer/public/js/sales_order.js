frappe.ui.form.on("Sales Order", {
	customer: frm => {
		frm.set_value("title", frm.doc.customer);
	},
	date: frm => {
		const {date, transaction_date} = frm.doc;
		
		if (!date){
			frm.set_value("transaction_date", "");
			return
		}
		frm.set_value("transaction_date", date);

	}
});