// Copyright (c) 2016, TZCODE SRL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Supplier Age"] = {
	"filters": [
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
			"label": __("Limit"),
			"fieldtype": "Int",
			"fieldname": "limit",
			"default": 50,
		},
		{
			"label": __("Show Unpaid Only?"),
			"fieldtype": "Check",
			"fieldname": "unpaid",
			"default": 1,
		},
	],
}
