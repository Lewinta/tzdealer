frappe.ui.form.on("Landed Cost Voucher", {
	refresh: frm => {
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
