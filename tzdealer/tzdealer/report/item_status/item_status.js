// Copyright (c) 2016, TZCODE SRL and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Status"] = {
	"filters": [

	],
	formatter: function (row, cell, value, columnDef, dataContext, default_formatter) {
		value = default_formatter(row, cell, value, columnDef, dataContext);

		if (cell == 2 && value) {
			_name = value.split('-')[0]
			value = `<a class="grey" target="_blank" href="#Form/Supplier/${_name}"">${value}</a>`;
		}

		return value;
	}
}
