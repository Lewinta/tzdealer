// Copyright (c) 2016, TZCODE SRL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Vehicle Status"] = {
	"filters": [

		{
			"fieldname":"report_type",
			"label": __("Report Type"),
			"fieldtype": "Select",
			"default": "Stock Report",
			"options": "All\nStock Report\nSold Report\nSales Order To Be Billed",
			"reqd": 1,
			"width": "80",
		},
		{
			"label": __("Vehicle Status"),
			"fieldname":"status",
			"fieldtype": "Select",
			"options": "\nComing Soon\nReceived\nSale Order\nSales Invoice\nDelivered",
			"width": "80",
		},
		{
			"label": __("Title Status"),
			"fieldname":"title_status",
			"fieldtype": "Select",
			"options": "\nComing Soon\nReceived\nDelivered",
			"width": "80",
		},
	],
	formatter: function (row, cell, value, columnDef, dataContext, default_formatter) {
		value = default_formatter(row, cell, value, columnDef, dataContext);

		if (cell == 3 && value) {
			_name = value.split('-')[0]
			value = `<a class="grey" target="_blank" href="#Form/Supplier/${_name}"">${value}</a>`;
		}
		
		if (cell == 7 && value) {
			_name = value.split('-')[0]
			value = `<a class="grey" target="_blank" href="#Form/Vehicle Release/${dataContext['Stock No.']}"">${value}</a>`;
		}
		return value;
	}
}
