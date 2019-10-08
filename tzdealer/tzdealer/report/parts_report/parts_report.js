// Copyright (c) 2016, TZCODE SRL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Parts Report"] = {
	"filters": [
			{
			"fieldname":"report_type",
			"label": __("Report Type"),
			"fieldtype": "Select",
			"default": "Stock Report",
			"options": "Stock Report\nSold Report",
			"reqd": 1,
			"width": "80",
		},
	]
}
