frappe.ui.form.on("Purchase Invoice", {
	refresh: frm => {
		if (frappe.user.has_role("Sales User") && !frappe.user.has_role("System Manager"))
			frappe.show_not_permitted();

		frm.trigger("reqd_transaction_group");
		frm.trigger("set_queries");

		
	},
	onload_post_render: frm => {
		if(frm.is_new)
			setTimeout( event => {
				frm.set_value("posting_date", '')
			}, 1000);
	},
	set_queries: frm => {
		frm.set_query("transaction_group",  event => {
			return{
				filters:{
					"transaction_type": "Purchases",
					"company": frm.doc.company,
				}
			}
		});

		if (frm.doc.company)
			frm.set_query("item_code", "items", () => {
				return{
					filters:{
						"company": frm.doc.company,
						"is_purchase_item": 1
					}
				}
			});

		frm.set_query("taxes_and_charges",  event => {
			return{
				filters:{
					"company": frm.doc.company,
				}
			}
		});
		frm.set_query("transaction_group",  event => {
			return{
				filters:{
					"transaction_type": "Purchases",
					"company": frm.doc.company,
				}
			}
		});

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
			if(item.idx == 1)
				item.expense_account = account;
		});

	},
	validate: frm => {
		
		frm.trigger("invoice_type");
		frm.trigger("update_expense_account_items");
		let {account, items, date} = frm.doc;

		frm.set_value("posting_date", date);
		
	},
	is_opening: frm => {
		frm.trigger("reqd_transaction_group");
	},
	reqd_transaction_group: frm => {
		frm.toggle_reqd("transaction_group", frm.doc.is_opening == "No");
	},
	invoice_type: frm => {
		if(frm.doc.is_return)
			return
		let check = frm.doc.invoice_type != "Services" && !frm.doc.is_return ? true : false;
		frm.set_value("update_stock", check);
	}

});

frappe.ui.form.on("Purchase Invoice Item",  {
	item_code: (frm, cdt, cdn) => {
		let {account} = frm.doc;
		let row = locals[cdt][cdn];
		if (!account)
			return

		setTimeout(event =>{
			if (row.idx == 1)
				frappe.model.set_value(cdt, cdn, "expense_account", account);
			
			frappe.model.set_value(cdt, cdn, "warehouse", frm.doc.default_warehouse);
			frappe.model.set_value(cdt, cdn, "rejected_warehouse", frm.doc.default_warehouse);

		}, 500);
	}
});