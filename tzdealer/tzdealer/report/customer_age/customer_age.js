// Copyright (c) 2016, TZCODE SRL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer Age"] = {
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
			"reqd": 1,
		},
		{
			"label": __("To Date"),
			"fieldtype": "Date",
			"fieldname": "to_date",
			"reqd": 1,
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
	// formatter: function(row, cell, value, columnDef, dataContext) {
	// 	if (new Array(1, 2, 11, 12).includes(cell)) {
	// 		route = value.split(":")[0]
	// 		return `<a class="grey" href="#Form/${columnDef.df.options}/${route}" data-doctype="Item">${value}</a>`;
	// 	} 
		
	// 	if(new Array(5, 8, 9, 10).includes(cell)) {
	// 		value = frappe.format(value, {
	// 			fieldtype: "Currency",
	// 			precision: 2,
	// 		});
	// 		return this.left_align(row, cell, value, columnDef, dataContext);
	// 	}

	// 	return `<span style="padding-left: 10px;">${value}</span>`;	
	// },
	// left_align: function(row, cell, value, columnDef, dataContext) {
	// 	const stylesheet = [
	// 		"text-align: right !important;",
	// 		"display: block;",
	// 	].join(" ");

	// 	return `<span style="${stylesheet}">${value || ""}</span>`;
	// },
}
