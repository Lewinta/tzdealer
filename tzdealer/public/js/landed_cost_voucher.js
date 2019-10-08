frappe.ui.form.on("Landed Cost Voucher", {
	refresh: frm => {
		const events = ["add_custom_buttons" , "set_queries"]
		
		$.map(events, event => {
			frm.trigger(event);
		});
	},
	set_queries: frm => {
		frm.set_query("transaction_group", "taxes", event => {
			return {
				"filters":{
					"transaction_type": "Purchases"
				}
			}
		});
	},
	add_custom_buttons: frm => {
		if(frm.doc.docstatus == 1)
			frm.trigger("purchase_inv_btn");
	},
	purchase_inv_btn: frm => {
		let method = "tzdealer.hook.landed_cost_voucher.create_purchase_invoice";
		frm.add_custom_button("Create Purchase Invoice", event => {
			$.map(frm.doc.taxes, row => {

				frappe.call(method, {"args":{},"row":row} , ({message}) => {
						if (message){
							frappe.show_alert(message, 10);

						}
					}
				);
			});
		});
	}
});

frappe.ui.form.on("Landed Cost Taxes and Charges", {
	total: (frm, cdt, cdn) => {
		frm.script_manager.trigger("calculate_tax_amount", cdt, cdn);
	},
	tax: (frm, cdt, cdn) => {
		frm.script_manager.trigger("calculate_tax_amount", cdt, cdn);
	},
	calculate_tax_amount: (frm, cdt, cdn) => {
		const {tax, total, tax_rate} = frappe.get_doc(cdt, cdn);

		if (!tax || !total)
			return

		const amount = total * (1 + flt(tax_rate) / 100);
		frappe.model.set_value(cdt, cdn, "amount", amount);
	}
});
