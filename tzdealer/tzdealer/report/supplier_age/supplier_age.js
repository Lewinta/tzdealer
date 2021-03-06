// Copyright (c) 2016, TZCODE SRL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Supplier Age"] = {
	"filters": [
		{
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"fieldname": "company",
		},
		{
			"label": __("From Date"),
			"fieldtype": "Date",
			"fieldname": "from_date",
		},
		{
			"label": __("To Date"),
			"fieldtype": "Date",
			"fieldname": "to_date",
		},
		{
			"label": __("Supplier"),
			"fieldtype": "Link",
			"fieldname": "supplier",
			"options": "Supplier",
		},
		{
			"label": __("Item Code"),
			"fieldtype": "Link",
			"fieldname": "item_code",
			"options": "Item",
		},
		{
			"label": __("Show Unpaid Only?"),
			"fieldtype": "Check",
			"fieldname": "unpaid",
			"default": 1,
		},
	],
	onload: function(report) {
		report.page.add_inner_button(__("Supplier Age Summary"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Supplier Age Summary', {
				company: filters.company,
				from_date: filters.from_date,
				to_date: filters.to_date,
				supplier: filters.supplier,
				unpaid: filters.unpaid,
				item_code: filters.item_code,
			});
		});
	},
}
