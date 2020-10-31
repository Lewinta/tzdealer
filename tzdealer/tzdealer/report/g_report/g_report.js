// Copyright (c) 2016, TZCODE SRL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["G Report"] = {
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
			"label": __("Payment Status"),
			"fieldtype": "Select",
			"fieldname": "payment_status",
			"options": "All\nUnpaid Only\nPaid Only",
			"default": "Unpaid Only",
			"reqd": 1,
		},
		
	],
	formatter: function (row, cell, value, columnDef, dataContext, default_formatter) {
		value = default_formatter(row, cell, value, columnDef, dataContext);

		if (cell == 2 && value) {
			_name = value.split('-')[0]
			value = `<a class="grey" target="_blank" href="#Form/Supplier/${_name}"">${value}</a>`;
		}

		if (cell == 16) {
			value = `<a class="grey" target="_blank" href="#List/Payment Entry/?reference_name=${dataContext["Sales Inv."]}&docstatus=1"><b>${value}</b></a>`;
			
		}
		
		if (cell == 19) {
			value = `<a class="grey" target="_blank" href="#Form/Vehicle Release/${dataContext['Stock No.']}""><b>${value}</b></a>`;
			
		}

		return value;
	}
}
