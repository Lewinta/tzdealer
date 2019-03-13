frappe.ui.form.on("Sales Invoice", {
	refresh: frm => {
		if(frm.is_new())
			frm.trigger("invoice_type");

		frm.set_query("transaction_group",  event => {
			return{
				filters:{
					"transaction_type": "Sales"
				}
			}
		});
	},
	transaction_group: frm => {
		let = {account, items} = frm.doc;

		if (!account || !items )
			return

		$.map(items, item => {
			item.income_account = account;
		});
	},
	validate: frm => {
		frm.trigger("invoice_type");
		let {account, items} = frm.doc;
		
		if (!account)
			return

		$.map(items, item => {
			if (item.income_account != account){
				frappe.msgprint("Invalid Transaction Group on row " + item.idx);
				validated = false;
			}
		});
	},
	invoice_type: frm => {
		let check = frm.doc.invoice_type != "Services" ? true : false;
		frm.set_value("update_stock", check);
	}
});


frappe.ui.form.on("Sales Invoice Item",  {
	item_code: (frm, cdt, cdn) => {
		let {account} = frm.doc;

		if (!account)
			return

		setTimeout(event =>{
			frappe.model.set_value(cdt, cdn, "income_account", account);
		}, 500);
	}
});