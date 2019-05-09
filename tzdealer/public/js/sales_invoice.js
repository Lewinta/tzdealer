frappe.ui.form.on("Sales Invoice", {
	refresh: frm => {
		if(frm.is_new()){
			frm.trigger("set_defaults");
		}
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

		frm.trigger("set_default_currency");
	},
	validate: frm => {
		frm.trigger("invoice_type");
		let {account, items} = frm.doc;
		
		if (!account)
			return

		$.map(items, item => {
			if (item.income_account != account){
				frappe.msgprint("Please refresh Transaction Group " + item.idx);
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
	},
	set_defaults: frm => {
		const defaults = {
			"Vehicles": "Sales Vehicle CAD-Export",
			"Containers": "Sales CAD Shipping Services",
			"Parts": "Sales PARTS CAD-LOCAL",
			"Services": "Sales CAD Services"
		}
		
		let {invoice_type, transaction_group} = frm.doc;

		setTimeout(event => {
			frm.set_value("account"	, "4150 - SALE Vehicle CAD-Export - EZ");
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
		const total = flt(total_g) + flt(total_g_taxes_and_charges);

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
			total_g_tax += flt(row.g_tax);
		})
		frm.set_value("total_g_taxes_and_charges", flt(total_g_tax, 2));
	},
	calculate_g_taxes_item: frm => {
		setTimeout(event => {
			$.map(frm.doc.taxes, ({doctype, name, charge_type, rate, tax_amount}) => {
				let tax = 0.00;
				let g_amount = 0.00;

				if (charge_type == "On Net Total "){
					tax = frm.doc.total_g * flt(rate / 100, 2);
					g_amount = frm.doc.total_g * flt(1 + rate / 100, 2);
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

		if (!account)
			return

		setTimeout(event =>{
			frappe.model.set_value(cdt, cdn, "income_account", account);
		}, 500);
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