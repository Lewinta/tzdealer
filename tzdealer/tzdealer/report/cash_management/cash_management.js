// Copyright (c) 2016, TZCODE SRL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Cash Management"] = {
	"filters": [
		{
			"label": "Company",
			"options": "Company",
			"fieldname": "company",
			"fieldtype": "Link",
			"reqd": 1,
		}
	]
}
