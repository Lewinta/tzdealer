// Copyright (c) 2020, TZCODE SRL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cross Invoice Payment Tool', {
	refresh: frm => {
		frm.trigger("set_queries");
		frm.add_custom_button("Clear Form", () => {
			frm.trigger("clear_form");
		})
	},
	set_queries: frm => {
		let field_map = {
			"customer_invoices": "customer",
			"supplier_invoices": "supplier",
		}

		$.map(["customer", "supplier"], field => {
			frm.set_query(field, function() { return { "disabled": 0 } });
		})
				
		$.map(["supplier_invoices", "customer_invoices"], field => {
			frm.set_query("invoice", field, () => {
				return {
					"filters": {
						"supplier": frm.doc[field_map[field]],
						"company": frm.doc.company,
						"posting_date": ["<=", frm.doc.posting_date],
						"outstanding_amount": [">", 0],
					}
				}
			});
		});
	},
	company: frm => {
		frm.trigger("reset_form");
	},
	posting_date: frm => {
		frm.trigger("set_queries");
	},
	customer: frm => {
		frm.clear_table("customer_invoices");
		frm.refresh_field("customer_invoices");
		frm.trigger("set_queries");
	},
	supplier: frm => {
		frm.clear_table("supplier_invoices");
		frm.refresh_field("supplier_invoices");
		frm.trigger("set_queries");
	},
	calculate_totals: frm => {
		let field_map = {
			"customer_invoices": "total_sales",
			"supplier_invoices": "total_purchases",
		}
		
		$.map(["customer_invoices", "supplier_invoices"], field => {
			let total = 0;
			frappe.run_serially([
				() => $.map(frm.doc[field], invoice => {total += flt(invoice.amount)}),
				() => frm.set_value(field_map[field], total),
			])
		});
	},
	clear_form: frm => {
		frm.set_value("company", "");
		frm.set_value("posting_date", "");
		frm.trigger("reset_form");
		frm.save_or_update();
	},
	reset_form: frm => {
		frm.set_value("customer", "");
		frm.set_value("supplier", "");
		frm.clear_table("customer_invoices");
		frm.clear_table("supplier_invoices");
		frm.set_value("total_sales", "");
		frm.set_value("total_purchases", "");
	},
	apply_payment: frm => {
		frm.call("apply_payment").then(() => {
			frappe.msgprint("Payment applied successfully");
			frm.trigger("clear_form");
			frm.save_or_update();
		});
	}

});

frappe.ui.form.on("Cross Invoice Detail", {
	customer_invoices_add: (frm, cdt, cdn) => {
		frappe.model.set_value(cdt, cdn, "invoice_type", "Sales Invoice");
		frm.set_query("invoice", "customer_invoices", () => {
			return {
				"filters": {
					"customer": frm.doc.customer,
					"company": frm.doc.company,
					"outstanding_amount": [">", 0],
				}
			}
		});
	},
	supplier_invoices_add: (frm, cdt, cdn) => {
		frappe.model.set_value(cdt, cdn, "invoice_type", "Purchase Invoice");
		frm.set_query("invoice", "supplier_invoices", () => {
			return {
				"filters": {
					"supplier": frm.doc.supplier,
					"company": frm.doc.company,
					"outstanding_amount": [">", 0],
				}
			}
		});
	},
	supplier_invoices_remove: (frm, cdt, cdn) => {
		frm.trigger("calculate_totals");
	},
	customer_invoices_remove: (frm, cdt, cdn) => {
		frm.trigger("calculate_totals");
	},
	invoice: (frm, cdt, cdn) => {
		row = frappe.model.get_doc(cdt, cdn);
		if (!row.invoice)
			return
		
		// Let's check for duplicates
		$.map(["customer_invoices", "supplier_invoices"], field => {
			frm.doc[field].filter(r => {
				if (r.invoice == row.invoice && r.idx != row.idx ){
					frappe.show_alert(`${row.invoice} already exists on row ${r.idx}`, 5);
					frm.get_field(field).grid.grid_rows[
						cur_frm.doc[field].length-1
					].remove();
					return
				}
			});
		});
		// Let's fetch the outstanding amount
		let fields_map = {
			"Sales Invoice": ["outstanding_amount", "debit_to", "customer"],
			"Purchase Invoice": ["outstanding_amount", "credit_to", "supplier"]
		}
		frappe.db.get_value(
			row.invoice_type,
			row.invoice,
			fields_map[row.invoice_type],
			({outstanding_amount, debit_to, credit_to, customer, supplier}) => {
				if(outstanding_amount)
					frappe.model.set_value(cdt, cdn, "amount", outstanding_amount);
				if(debit_to)
					frappe.model.set_value(cdt, cdn, "account", debit_to);
				if(credit_to)
					frappe.model.set_value(cdt, cdn, "account", credit_to);
				if(supplier)
					frappe.model.set_value(cdt, cdn, "party", supplier);
				if(customer)
					frappe.model.set_value(cdt, cdn, "party", customer);
			}
		).then( () => frm.trigger("calculate_totals"));
	}
});
