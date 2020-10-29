// Copyright (c) 2016, TZCODE SRL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Supplier Age Summary"] = {
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
			"label": __("Payment Status"),
			"fieldtype": "Select",
			"fieldname": "payment_status",
			"options": "All\nUnpaid Only\nPaid Only",
			"default": "Unpaid Only",
			"reqd": 1,
		},
		// {
		// 	"label": __("Show Unpaid Only?"),
		// 	"fieldtype": "Check",
		// 	"fieldname": "unpaid",
		// 	"default": 1,
		// },
	],
	onload: function(report) {
		report.page.add_inner_button(__("Supplier Age"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Supplier Age', {
				company: filters.company,
				from_date: filters.from_date,
				to_date: filters.to_date,
				supplier: filters.supplier,
				unpaid: filters.unpaid,
				item_code: filters.item_code,
			});
		});
	},
	formatter: function (row, cell, value, columnDef, dataContext, default_formatter) {
		value = default_formatter(row, cell, value, columnDef, dataContext);

		// if (cell == 2 && value) {
		// 	_name = value.split('-')[0]
		// 	value = `<a class="grey" target="_blank" href="#Form/Supplier/${_name}"">${value}</a>`;
		// }

		if (cell == 21) {
			value = `<a class="grey" target="_blank" href="#List/Payment Entry/?reference_name=${dataContext["Invoice"]}&docstatus=1"><b>${value}</b></a>`;
			
		}

		return value;
	}
}
