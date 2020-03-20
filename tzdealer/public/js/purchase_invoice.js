frappe.ui.form.on("Purchase Invoice", {
	refresh: frm => {
		if (frappe.user.has_role("Sales User") && !frappe.user.has_role("System Manager"))
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
	onload_post_render: frm => {
		if(frm.is_new)
			setTimeout( event => {
				frm.set_value("posting_date", '')
			}, 1000);
	},
	date: frm => {
		const {date, posting_date} = frm.doc;
		
		if (!date){
			frm.set_value("posting_date", "");
			return
		}
		frm.set_value("posting_date", date);

	},
	company: frm => {
		if (!frm.doc.company)
			return
		
		let filters = {"company": frm.doc.company, "default": 1}
		frappe.db.get_value("Warehouse", filters, "name", (response) => {
			frm.doc.default_warehouse = "";
			if (!response || !response.name)
				return
			frm.doc.default_warehouse = response.name;
			
			// if there are items let's update the warehouse
			if (frm.doc.items)
				frm.trigger("update_warehouse_items");
		})
	},
	update_warehouse_items: frm => {
		$.map(frm.doc.items, item => {
			frappe.model.set_value(
				item.doctype, item.name, 
				"warehouse", 
				frm.doc.default_warehouse
			)
			
			frappe.model.set_value(
				item.doctype,
				item.name,
				"rejected_warehouse",
				frm.doc.default_warehouse
			)
		})
	},
	transaction_group: frm => {
		const {account, items, transaction_group} = frm.doc;

		if(!transaction_group)
			return

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
		let {account, items, date} = frm.doc;

		frm.set_value("posting_date", date);
		
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
		let check = frm.doc.invoice_type != "Services" && !frm.doc.is_return ? true : false;
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
			frappe.model.set_value(cdt, cdn, "warehouse", frm.doc.default_warehouse);
			frappe.model.set_value(cdt, cdn, "rejected_warehouse", frm.doc.default_warehouse);

		}, 500);
	}
});