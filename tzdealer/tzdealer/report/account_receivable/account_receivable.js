// Copyright (c) 2016, TZCODE SRL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Account Receivable"] = {
	"filters": [

		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			// "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			// "default": frappe.datetime.get_today()
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname":"unpaid",
			"label": __("Show Unpaid Only?"),
			"fieldtype": "Check",
			"default": 1
		}
	]
}
