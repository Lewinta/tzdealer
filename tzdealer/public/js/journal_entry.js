frappe.ui.form.on("Journal Entry", {
	refresh: frm => {
		let cond = frm.doc.docstatus < 2;
		if (cond)
			frm.toggle_reqd("transaction_type", cond);
	},
	validate: frm => {
		let {voucher_type, cheque_date, cheque_no, posting_date} = frm.doc;

		if (!cheque_no)
			frm.set_value("cheque_no", `${voucher_type} on ${posting_date}`);
		
		if (!cheque_date)
			frm.set_value("cheque_date", posting_date);
	},
	voucher_type: frm => {
		// Waseem requested to remove the reqd option for thi field
		if (!frm.doc.voucher_type)
			return
		setTimeout(function() {
			frm.set_df_property("cheque_no", "reqd", 0);
			frm.set_df_property("cheque_date", "reqd", 0);
		}, 500);
	}

});