// Copyright (c) 2018, Yefri Tavarez and contributors
// For license information, please see license.txt

// STATUS LIST
// Draft
// Return
// Credit Note Issued
// Submitted
// Paid
// Unpaid
// Overdue
// Cancelled

frappe.ui.form.on('Credit Note Mapping Tool', {
	"onload": (frm) => {
		frm.trigger("disable_save");
	},
	"refresh": (frm) => {
		$.map([
			"set_queries",
			"set_intro"
		], event => frm.trigger(event));
	},
	"set_queries": (frm) => {
		$.map([
			"set_customer_query",
			"set_credit_note_query",
			"set_sales_invoice_query"
		], event => frm.trigger(event));
	},
	"set_intro": (frm) => {
		frm.set_intro(`This form is used to map credit notes to invoice
			so that the customer balance can be reapplied`);
	},
	"set_customer_query": (frm) => {
		frm.set_query("customer", function() {
			return {
				"query": "fairweather.queries.customer_with_credit_query"
			};
		});
	},
	"set_credit_note_query": (frm) => {
		frm.set_query("credit_note", function() {
			return {
				"filters": {
					"status": "Credit Note Issued",
					"docstatus": "1",
					"customer": frm.doc.customer
				}
			};
		});
	},
	"set_sales_invoice_query": (frm) => {
		frm.set_query("sales_invoice", function() {
			return {
				"filters": {
					"status": ["in", "Overdue, Unpaid"],
					"docstatus": "1",
					"customer": frm.doc.customer
				}
			};
		});
	},
	"disable_save": (frm) => {
		frm.disable_save();
	},
	"validate_credit_note_against_invoice": (frm) => {
		if (frm.doc.credit_note == frm.doc.sales_invoice) {
			frappe.throw("Sales Invoice and Credit Note should be not be linked!");
		}
	},
	"validate_mandatory_fields": (frm) => {
		$.map(["customer", "credit_note", "sales_invoice"], fieldname => {
			const label = frm.fields_dict[fieldname].df.label,
				message = `Required: ${label} is a mandatory field!`;

			if (!frm.doc[fieldname]) {
				frappe.throw(message);
			}
		});
	},
	"guess_amount_to_apply": (frm) => {
		if (!frm.doc.unallocated_amount ||
			!frm.doc.invoice_outstanding_amount) { return ; }

		const guessed_amount = frm.doc.unallocated_amount > frm.doc.invoice_outstanding_amount?
			frm.doc.invoice_outstanding_amount:
			frm.doc.unallocated_amount;

		frm.set_value("amount_to_apply", guessed_amount);
	},
	"clear_form": (frm) => {
		$.each(frm.fields_dict, (fieldname, docfield) => {
			const excluded_list = ["Section Break", "Column Break", "Button", "HTML"],
				is_excluded = excluded_list.includes(docfield.df.fieldtype);

			if (!is_excluded) {
				frm.doc[fieldname] = undefined;
		    }
		});

		frm.refresh_fields();
	},
	"call_apply_outstanding_amount_to_invoice": (frm) => {
		frm.call("apply_outstanding_amount_to_invoice")
			.then(response => {
				frappe.show_alert({ "message": "Credit Applied", "indicator": "green" });
			}, exec => {
				frappe.show_alert({ "message": "Credit not Applied", "indicator": "red" });
			});
	},
	"apply_credit": (frm) => {
		const ifyes = () => {
			frappe.run_serially([
				() => frm.trigger("validate_mandatory_fields"),
				() => frm.trigger("validate_credit_note_against_invoice"),
				() => frm.trigger("call_apply_outstanding_amount_to_invoice"),
				() => frm.trigger("clear_form")
			]);
		}, ifno = () => {
			// frm.trigger("clear_form");
		};

		frappe.confirm(`You are about to apply a credit from an Credit Note to an Invoice.
			This action cannot be undone... are you sure you want to continue?`, ifyes, ifno);
	},
	"customer": (frm) => {
		const method = "erpnext.accounts.utils.get_balance_on",
			args = {
				"party_type": "Customer",
				"party": frm.doc.customer
			},
			callback = ({ message }) => {
				if (message) {
					frm.set_value("customer_balance", message);
				}
			};

		frm.set_value("customer_balance", "0.000");

		if (!frm.doc.customer) { return ; }

		frappe.call({ "method": method, "args": args, "callback": callback });
	},
	"credit_note": (frm) => {
		const method = "frappe.client.get_value",
			args = {
				"doctype": "Sales Invoice",
				"filters": {
					"name": frm.doc.credit_note
				},
				"fieldname": ["outstanding_amount"]
			},
			callback = ({ message }) => {
				const outstanding_amount = flt(message.outstanding_amount);

				if (outstanding_amount >= 0.000) {
					frappe.run_serially([
						() => frm.set_value("credit_note", undefined),
						() => frappe.throw("This Credit Note has no balance anymore!")
					]);
				}

				if (!frm.doc.amount_to_apply) {
					frm.trigger("guess_amount_to_apply");
				}

				frm.set_value("unallocated_amount", Math.abs(outstanding_amount));
			};

		frm.set_value("unallocated_amount", "0.000");

		if (!frm.doc.credit_note) { return ; }

		frappe.call({ "method": method, "args": args, "callback": callback });
	},
	"sales_invoice": (frm) => {
		const method = "frappe.client.get_value",
			args = {
				"doctype": "Sales Invoice",
				"filters": {
					"name": frm.doc.sales_invoice
				},
				"fieldname": ["outstanding_amount", "grand_total"]
			},
			callback = ({ message }) => {
				const { outstanding_amount, grand_total } = message;

				if (flt(outstanding_amount) <= 0.000) {
					frappe.run_serially([
						() => frm.set_value("sales_invoice", undefined),
						() => frappe.throw("This Invoice has not any Outstanding Amount!")
					]);
				}

				if (!frm.doc.amount_to_apply) {
					frm.trigger("guess_amount_to_apply");
				}

				$.each({
					"invoice_amount": grand_total,
					"invoice_outstanding_amount": outstanding_amount
				}, (fieldname, value) => frm.set_value(fieldname, value));
			};

		$.map([
			"invoice_amount",
			"invoice_outstanding_amount"
		], fieldname => frm.set_value(fieldname, "0.000"));

		if (!frm.doc.sales_invoice) { return ; }

		frappe.call({ "method": method, "args": args, "callback": callback });
	},
	"amount_to_apply": (frm) => {
		if (frm.doc.amount_to_apply > frm.doc.invoice_outstanding_amount) {
			frappe.run_serially([
				() => frm.trigger("guess_amount_to_apply"),
				() => frappe.throw("Amount to Apply cannot be greater than the Invoice Outstanding Amount")
			]);
		}

		if (frm.doc.amount_to_apply > frm.doc.unallocated_amount) {
			frappe.run_serially([
				() => frm.trigger("guess_amount_to_apply"),
				() => frappe.throw("Amount to Apply cannot be greater than the Unallocated Amount")
			]);
		}
	}
});
