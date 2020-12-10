frappe.ui.form.on("Sales Invoice", {
	refresh: frm => {
		$.map(["set_queries", "has_commission_invoice"], event => frm.trigger(event));

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
		frm.set_value("customer_group", "");
		frm.trigger("set_queries");
	},
	set_queries: frm => {

			frm.set_query("item_code", "items", () => {
				return{
					filters:{
						"company": frm.doc.company,
						"is_sales_item": 1,
					}
				}
			});

		frm.set_query("transaction_group",  event => {
			return{
				filters:{
					"transaction_type": "Sales",
					"company": frm.doc.company,
				}
			}
		});
		frm.set_query("commission_tax",  event => {
			return{
				filters:{
					"company": frm.doc.company,
				}
			}
		});
	},
	transaction_group: frm => {
		const {transaction_group, items} = frm.doc;
		frappe.db.get_value(
			"Transaction Group",
			transaction_group,
			"account", ({account}) => {
				if(!account)
					frappe.throw(_("Please set an account for Transaction Group "+ transaction_group));
				
				frm.set_value("account", account);
				
				if (!items )
					return

				$.map(items, item => {
					if(item.idx == 1)
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
	has_commission_invoice: frm => {
		let _callback = function (response) {
			let cond = response && response.message;
			$.map(
				["sales_partner", "commission_tax", "commission_rate", "total_commission"],
				field => frm.set_df_property(field, "read_only", !!cond)
			)
		}
		let opts = {
			"method": "tzdealer.hook.sales_invoice.has_commission_invoice",
			"args": {"sinv_name":cur_frm.doc.name},
			"callback": _callback,
		}
		frappe.call(opts)
	},
	is_opening: frm => {
		frm.trigger("reqd_transaction_group");
	},
	reqd_transaction_group: frm => {
		frm.toggle_reqd("transaction_group", frm.doc.is_opening == "No");
	},
	invoice_type: frm => {
		if (frm.doc.is_return)
			return
		let check = frm.doc.invoice_type != "Services" ? true : false;
		frm.set_value("update_stock", check);

		frm.toggle_reqd("sale_type", frm.doc.invoice_type == "Vehicles");
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
		//This will allow users to bill the customer on different currency
		return
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
	item_code: (frm, cdt, cdn) => {
		let {account, company} = frm.doc;
		let row = frappe.model.get_doc(cdt,cdn);
		let df  = frm.get_field("items").grid.docfields[2];
		let  filters = {
			"company": company,
			"default": 1
		}
		if (!row.item_code)
			return 
		if (!company){
			frappe.throw("Please set a valid company in order to choose an Item ");
			frappe.model.set_value(cdt, cdn, "item_code", "");
		}

		setTimeout( event => {
			if(row.item_group == "Containers"){
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
				row.vim_number = '';
				df.reqd = 0;
				frm.refresh_field("items");

			}
			
			frappe.db.get_value("Warehouse", filters, "name",({name}) => {
				if(!name)
					return
				frappe.model.set_value(cdt, cdn, "warehouse", name);
			});

			if(row.idx == 1)
				frappe.model.set_value(cdt, cdn, "income_account", account);
			
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