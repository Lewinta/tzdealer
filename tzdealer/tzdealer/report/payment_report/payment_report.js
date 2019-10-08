// Copyright (c) 2016, TZCODE SRL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Payment Report"] = {
	"filters": [
		// {
		// 	"label": __("From Date"),
		// 	"fieldtype": "Date",
		// 	"fieldname": "from_date",
		// 	"default": frappe.datetime.month_start(),
		// 	"reqd": 1
		// },
		// {
		// 	"label": __("To Date"),
		// 	"fieldtype": "Date",
		// 	"fieldname": "from_date",
		// 	"default": frappe.datetime.month_end(),
		// 	"reqd": 1
		// },
		{
			"label": __("Customer"),
			"fieldtype": "Link",
			"fieldname": "customer",
			"options": "Customer",
		},
		// {
		// 	"label": __("Vim Number"),
		// 	"fieldtype": "Link",
		// 	"fieldname": "vim_number",
		// 	"options": "Item",
		// },
		// {
		// 	"label": __("Company"),
		// 	"fieldtype": "Link",
		// 	"fieldname": "company",
		// 	"options": "Company",
		// 	"hidden": 1
		// 	"default": "EAZYAUTOTRADE"
		// }
	]	
}
