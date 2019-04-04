frappe.ui.form.on("Purchase Invoice", {
	refresh: frm => {
		if(frm.is_new())
			frm.trigger("invoice_type");

		if (frappe.user.has_role("Sales User"))
			frappe.show_not_permitted();
		
		frm.trigger("reqd_transaction_group");

		frm.set_query("transaction_group",  event => {
			return{
				filters:{
					"transaction_type": "Purchases"
				}
			}
		});
	},
	transaction_group: frm => {
		let = {account, items} = frm.doc;

		frappe.db.get_value(
			"Account", 
			account, 
			"account_currency", ({account_currency}) => {
				if (account_currency)
					frm.set_value("currency", account_currency)
			}
		)

		if (!account || !items )
			return


		$.map(items, item => {
			item.expense_account = account;
		});

	},
	validate: frm => {
		frm.trigger("invoice_type");
		let {account, items} = frm.doc;
		
		if (!account)
			return

		$.map(items, item => {
			if (item.expense_account != account){
				frappe.msgprint("Invalid Transaction Group on row " + item.idx);
				validated = false;
			}
		});
		

	},
	is_opening: frm => {
		frm.trigger("reqd_transaction_group");
	},
	reqd_transaction_group: frm => {
		frm.toggle_reqd("transaction_group", frm.doc.is_opening == "No");
	},
	invoice_type: frm => {
		let check = frm.doc.invoice_type != "Services" ? true : false;
		frm.set_value("update_stock", check);
	}

});

frappe.ui.form.on("Purchase Invoice Item",  {
	item_code: (frm, cdt, cdn) => {
		let {account} = frm.doc;

		if (!account)
			return

		setTimeout(event =>{
			frappe.model.set_value(cdt, cdn, "expense_account", account);
		}, 500);
	}
});