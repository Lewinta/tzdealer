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

frappe.ui.form.on("Sales Order Item",  {
	item_code: (frm, cdt, cdn) => {
		let {company} = frm.doc;
		let  filters = {
			"company": company,
			"default": 1
		}
		row  = frappe.model.get_doc(cdt, cdn);

		if (!row.item_code)
			return 

		if (!company){
			frappe.throw("Please set a valid company in order to choose an Item ");
			frappe.model.set_value(cdt, cdn, "item_code", "");
		}

		setTimeout(() => {
			frappe.db.get_value("Warehouse", filters, "name",({name}) => {
				if(!name)
					return
				frappe.model.set_value(cdt, cdn, "warehouse", name);
			});
		},500);
	}
});