// Copyright (c) 2016, TZCODE SRL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer Age Summary"] = {
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
			// "reqd": 1,
		},
		{
			"label": __("To Date"),
			"fieldtype": "Date",
			"fieldname": "to_date",
			// "reqd": 1,
		},
		{
			"label": __("Customer"),
			"fieldtype": "Link",
			"fieldname": "customer",
			"options": "Customer",

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
		report.page.add_inner_button(__("Customer Age"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Customer Age', {
				company: filters.company,
				from_date: filters.from_date,
				to_date: filters.to_date,
				customer: filters.customer,
				unpaid: filters.unpaid,
				item_code: filters.item_code,
			});
		});
	},
	formatter: function (row, cell, value, columnDef, dataContext, default_formatter) {
		value = default_formatter(row, cell, value, columnDef, dataContext);

		if (cell == 18) {
			value = `<a class="grey" target="_blank" href="#List/Payment Entry/?reference_name=${dataContext["Sales Inv."]}&docstatus=1"><b>${value}</b></a>`;
			
		}

		return value;
	}
}
