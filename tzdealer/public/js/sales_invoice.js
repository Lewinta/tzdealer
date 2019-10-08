frappe.ui.form.on("Sales Invoice", {
	refresh: frm => {
		// if(frm.is_new()){
		// 	frm.trigger("set_defaults");
		// }
		frm.trigger("set_queries");

	},
	date: frm => {
		const {date, posting_date} = frm.doc;
		
		if (!date){
			frm.set_value("posting_date", "");
			return
		}
		frm.set_value("posting_date", date);

	},
	set_queries: frm => {

		frm.set_query("item_code", "items", () => {
			return{
				filters:{
					"company": frm.doc.company
				}
			}
		});

		frm.set_query("transaction_group",  event => {
			return{
				filters:{
					"transaction_type": "Sales"
				}
			}
		});
	},
	transaction_group: frm => {

		const {transaction_group, items} = frm.doc;
		console.log("Fetching account");
		frappe.db.get_value(
			"Transaction Group",
			transaction_group,
			"account", ({account}) => {
				if(!account)
					frappe.throw(_("Please set an account for Transaction Group "+ transaction_group));
				
				console.log("Found "+ account);
				frm.set_value("account", account);
				
				if (!items )
					return

				$.map(items, item => {
					item.income_account = account;
				});

				frm.trigger("set_default_currency");
				
			}
		)

	},
	validate: frm => {
		const {account, items} = frm.doc;
		frappe.run_serially([
			frm.trigger("invoice_type"),
			frm.trigger("transaction_group"),
			// () => setTimeout( event => {
			// 	$.map(items, item => {
			// 		if(!account)
			// 			return
			// 		if(item.income_account != account){
			// 			frappe.msgprint("Please refresh Transaction Group " + item.idx);
			// 			validated = fale;
			// 		}
			// 	})
			// },400)
		]);

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
	},
	set_defaults: frm => {
		const defaults = {
			"Vehicles": "Sales Vehicle Export",
			"Containers": "Sales CAD Shipping Services",
			"Parts": "Sales PARTS CAD-LOCAL",
			"Services": "Sales CAD Services"
		}
		
		let {invoice_type, transaction_group} = frm.doc;

		setTimeout(event => {
			frm.set_value("account"	, "4150 - Sale Vehicle Export - EZ");
			frm.set_value("transaction_group", defaults[invoice_type]);
		}, 500)
	},
	set_default_currency: frm => {
		const {transaction_group} = frm.doc;
		if (!transaction_group)
			return
		frm.set_value(
			"currency",
			transaction_group.includes("USD") ? "USD" : "CAD"
		);
	},
	customer: frm => {
		frm.set_value("title", frm.doc.customer);
	},
	currency: frm => {
		const {currency} = frm.doc;

		frm.fields_dict.total_g.df.label = "Total G (" + currency + ")";
		refresh_field("total_g");
	},
	refresh_gprice: frm => {
		let total_g = 0.00;

		$.map(frm.doc.items, item => {
			total_g += flt(item.gprice);
		});

		frm.set_value("total_g", total_g);
	},
	total_g: frm =>{
		frm.trigger("calcualte_grand_g_total");
		frm.trigger("calculate_g_taxes_item");
	},
	calcualte_grand_g_total: frm => {
		const {total_g, total_g_taxes_and_charges} = frm.doc;
		const total = flt(total_g, 4) + flt(total_g_taxes_and_charges, 4);

		frm.set_value("grand_g_total", total);
	},
	taxes_and_charges: frm => {
		frm.trigger("calculate_g_taxes_item");
	},
	total_g_taxes_and_charges: frm => {
		frm.trigger("calcualte_grand_g_total");
	},
	refresh_g_taxes: frm => {
		if (!frm.doc.taxes)
			return
		let total_g_tax = 0.00;
		$.map(frm.doc.taxes, row => {
			total_g_tax += flt(row.g_tax, 4);
		})
		frm.set_value("total_g_taxes_and_charges", flt(total_g_tax, 4));
	},
	calculate_g_taxes_item: frm => {
		setTimeout(event => {
			$.map(frm.doc.taxes, ({doctype, name, charge_type, rate, tax_amount}) => {
				let tax = 0.00;
				let g_amount = 0.00;

				if (charge_type == "On Net Total"){
					tax = flt(frm.doc.total_g * rate / 100.00, 4);
					g_amount = flt(frm.doc.total_g * (1 + rate / 100.0), 4);
				}

				if (charge_type == "Actual"){
					tax = tax_amount;
					g_amount = frm.doc.total_g + tax_amount;
				}

				frappe.model.set_value(doctype, name, "g_amount", g_amount);
				frappe.model.set_value(doctype, name, "g_tax", tax);
			});
			frm.trigger("refresh_g_taxes");
		}, 500);
	}
});

frappe.ui.form.on("Sales Invoice Item",  {
	item_add: (frm, cdt, cdn) => {
		let {account} = frm.doc;

		if (!account)
			return

		setTimeout(event =>{
			frappe.model.set_value(cdt, cdn, "income_account", account);
		}, 500);
	},
	item_code: (frm, cdt, cdn) => {
		let {account} = frm.doc;
		let row = frappe.model.get_doc(cdt,cdn);
		let df = frm.get_field("items").grid.docfields[2];
		setTimeout( event => {
			if(row.item_group == "Containers"){
				console.log("is a container")
				frappe.call(
					"tzdealer.api.get_container_vims", 
					{
						"item_code": row.item_code,
						"company": frm.doc.company,
					},
					({message})=> {
						df.options = message;
						df.reqd = 1;
						frm.refresh_field("items");
					}
				);
			}
			else{
				console.log(row.item_group+ " is not a container for item "+ row.item_code)
				row.vim_number = '';
				df.reqd = 0;
				frm.refresh_field("items");

			}
			
			if (!account)
				return
			setTimeout(event =>{
				frappe.model.set_value(cdt, cdn, "income_account", account);
			}, 500);

			frm.refresh_field("items");
		}, 600);
	},
	gprice: (frm, cdt, cdn) => {
		frm.trigger("refresh_gprice");
	},
});

frappe.ui.form.on("Sales Taxes and Charges",  {
	taxes_add: (frm, cdt, cdn) => {
		frm.trigger("calculate_g_taxes_item");
	},
	rate: (frm, cdt, cdn)  => {
		frm.trigger("calculate_g_taxes_item");
	},
	tax_amount: (frm, cdt, cdn) => {
		frm.trigger("calculate_g_taxes_item");
	}

});