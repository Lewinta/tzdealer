// Copyright (c) 2016, TZCODE SRL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Container Report"] = {
	"filters": [{
			"fieldname":"report_type",
			"label": __("Report Type"),
			"fieldtype": "Select",
			"default": "Stock Report",
			"options": "Stock Report\nSold Report",
			"reqd": 1,
			"width": "80",
		},
	],
	// formatter: function(row, cell, value, columnDef, dataContext) {
	// 	let type = $('select[data-fieldname="report_type"]').val();
		
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


