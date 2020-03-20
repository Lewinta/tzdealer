// Copyright (c) 2020, TZCODE SRL and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bulk Debit Note Tool', {
	refresh: frm => {

	},
	supplier: frm => {
		frm.call("retrieve_invoices");
	}
});
