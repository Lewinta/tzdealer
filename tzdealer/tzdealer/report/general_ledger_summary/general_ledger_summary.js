// Copyright (c) 2016, TZCODE SRL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["General Ledger Summary"] = {
	"filters": [
		{
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"fieldname": "company",
			"reqd": 1,
		},
		{
			"label": __("From Date"),
			"fieldtype": "Date",
			"fieldname": "from_date",
			"default": frappe.datetime.year_start(),
		},
		{
			"label": __("To Date"),
			"fieldtype": "Date",
			"fieldname": "to_date",
			"default": frappe.datetime.year_end(),
		},
		{
			"label": __("Account"),
			"fieldtype": "Link",
			"options": "Account",
			"fieldname": "account",
		},

	]
}
