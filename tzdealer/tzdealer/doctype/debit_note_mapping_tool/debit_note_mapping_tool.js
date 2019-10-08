// Copyright (c) 2018, Yefri Tavarez and contributors
// For license information, please see license.txt

// STATUS LIST
// Draft
// Return
// Debit Note Issued
// Submitted
// Paid
// Unpaid
// Overdue
// Cancelled

frappe.ui.form.on('Debit Note Mapping Tool', {
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
			"set_supplier_query",
			"set_debit_note_query",
			"set_purchase_invoice_query"
		], event => frm.trigger(event));
	},
	"set_intro": (frm) => {
		frm.set_intro(`This form is used to map Debit notes to invoice
			so that the supplier balance can be reapplied`);
	},
	"set_supplier_query": (frm) => {
		// frm.set_query("supplier", function() {
		// 	return {
		// 		"query": "fairweather.queries.supplier_with_debit_query"
		// 	};
		// });
	},
	"set_debit_note_query": (frm) => {
		frm.set_query("debit_note", function() {
			return {
				"filters": {
					"status": "Debit Note Issued",
					"docstatus": "1",
					"supplier": frm.doc.supplier
				}
			};
		});
	},
	"set_purchase_invoice_query": (frm) => {
		frm.set_query("purchase_invoice", function() {
			return {
				"filters": {
					"status": ["in", "Overdue, Unpaid"],
					"docstatus": "1",
					"supplier": frm.doc.supplier
				}
			};
		});
	},
	"disable_save": (frm) => {
		frm.disable_save();
	},
	"validate_debit_note_against_invoice": (frm) => {
		if (frm.doc.debit_note == frm.doc.purchase_invoice) {
			frappe.throw("Purchase Invoice and Debit Note should be not be linked!");
		}
	},
	"validate_mandatory_fields": (frm) => {
		$.map(["supplier", "debit_note", "purchase_invoice"], fieldname => {
			const label = frm.fields_dict[fieldname].df.label,
				message = `Required: ${label} is a mandatory field!`;

			if (!frm.doc[fieldname]) {
				frappe.throw(message);
			}
		});
	},
	"guess_amount_to_apply": (frm) => {
		if (!frm.doc.unallocated_amount ||
			!frm.doc.invoice_outstanding_amount) { 

			return false; 
		}

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
				frappe.show_alert({ "message": "debit Applied", "indicator": "green" });
			}, exec => {
				frappe.show_alert({ "message": "debit not Applied", "indicator": "red" });
			});
	},
	"apply_debit": (frm) => {
		const ifyes = () => {
			frappe.run_serially([
				() => frm.trigger("validate_mandatory_fields"),
				() => frm.trigger("validate_debit_note_against_invoice"),
				() => frm.trigger("call_apply_outstanding_amount_to_invoice"),
				() => frm.trigger("clear_form")
			]);
		}, ifno = () => {
			// frm.trigger("clear_form");
		};

		frappe.confirm(`You are about to apply a debit from an Debit Note to an Invoice.
			This action cannot be undone... are you sure you want to continue?`, ifyes, ifno);
	},
	"supplier": (frm) => {
		const method = "erpnext.accounts.utils.get_balance_on",
			args = {
				"party_type": "Supplier",
				"party": frm.doc.supplier
			},
			callback = ({ message }) => {
				if (message) {
					frm.set_value("supplier_balance", message);
				}
			};

		frm.set_value("supplier_balance", "0.000");

		if (!frm.doc.supplier) { return ; }

		frappe.call({ "method": method, "args": args, "callback": callback });
	},
	"debit_note": (frm) => {
		const method = "frappe.client.get_value",
			args = {
				"doctype": "Purchase Invoice",
				"filters": {
					"name": frm.doc.debit_note
				},
				"fieldname": ["outstanding_amount"]
			},
			callback = ({ message }) => {
				const outstanding_amount = flt(message.outstanding_amount);

				if (outstanding_amount >= 0.000) {
					frappe.run_serially([
						() => frm.set_value("debit_note", undefined),
						() => frappe.throw("This Debit Note has no balance anymore!")
					]);
				}

				if (!frm.doc.amount_to_apply) {
					frm.trigger("guess_amount_to_apply");
				}

				frm.set_value("unallocated_amount", Math.abs(outstanding_amount));
			};

		frm.set_value("unallocated_amount", "0.000");

		if (!frm.doc.debit_note) { return ; }

		frappe.call({ "method": method, "args": args, "callback": callback });
	},
	"purchase_invoice": (frm) => {
		const method = "frappe.client.get_value",
			args = {
				"doctype": "Purchase Invoice",
				"filters": {
					"name": frm.doc.purchase_invoice
				},
				"fieldname": ["outstanding_amount", "grand_total"]
			},
			callback = ({ message }) => {
				const { outstanding_amount, grand_total } = message;

				if (flt(outstanding_amount) <= 0.000) {
					frappe.run_serially([
						() => frm.set_value("purchase_invoice", undefined),
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

		if (!frm.doc.purchase_invoice) { return ; }

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
