# Copyright (c) 2013, TZCODE SRL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _

def execute(filters=None):
	return get_columns(), get_data(filters)

def get_columns():
	return [
		_("Company") 		+ ":Company:120",
		_("Location") 		+ ":Company:230",
		_("Status") 		+ ":Data:100",
		_("Title") 			+ ":Data:100",
		_("Item Group") 	+ ":Data:90",
		_("Date")	 		+ ":Date:90",
		_("Stock No.") 		+ ":Link/Item:150",
		_("Vin Number") 	+ ":Data:150",
		_("Vehicle Details") 		+ ":Data:220",
		_("Container Details") 		+ ":Data:220",
		_("Purchase") 		+ ":Currency/currency:120",
		_("Sold") 			+ ":Currency/currency:100",
		_("Last Updated") 	+ ":Date:140",
	]

def get_data(filters=None):
	return frappe.db.sql("""
		SELECT
			`tabItem`.company,
			CONCAT(`tabItem`._default_supplier, ' - ', `tabAddress`.city, ', ', `tabAddress`.state) as location,
			`tabItem`.status,
			`tabItem`.title_status,
			`tabItem`.item_group,
			`tabItem`.purchase_date,
			`tabItem`.name,
			`tabItem`.vim_number,
			CONCAT(
				`tabItem`.make, " ",
				`tabItem`.model, " ",
				`tabItem`.exterior_color, " ",
				`tabItem`.year
			) as veh_details,
			CONCAT(
				`tabItem`.booking_no, " ",
				`tabItem`.container_no, " "
			) as cont_details,
			`tabPurchase Invoice Item`.base_amount,
			`tabSales Invoice Item`.base_amount,
			`tabItem`.modified
		FROM 
			`tabItem`
		LEFT JOIN
			`tabPurchase Invoice Item`
		ON
			`tabItem`.item_code = `tabPurchase Invoice Item`.item_code
		AND
			`tabPurchase Invoice Item`.docstatus = 1 
		LEFT JOIN
			`tabSales Invoice Item`
		ON
			`tabItem`.item_code = `tabSales Invoice Item`.item_code
		AND
			`tabSales Invoice Item`.docstatus = 1 	
		LEFT JOIN
			`tabAddress`
		ON
			`tabItem`.location = `tabAddress`.name
		WHERE	
			`tabItem`.item_type = 'Vehicles'
		
		UNION

		SELECT
			`tabItem`.company,
			CONCAT(`tabItem`._default_supplier, ' - ', `tabAddress`.city, ', ', `tabAddress`.state) as location,
			`tabItem`.status,
			`tabItem`.title_status,
			`tabItem`.item_group,
			`tabItem`.purchase_date,
			`tabItem`.name,
			`tabItem Description`.vim_number,
			CONCAT(
				`tabItem Description`.make, " ",
				`tabItem Description`.model, " ",
				`tabItem Description`.exterior_color, " ",
				`tabItem Description`.year
			) as veh_details,
			CONCAT(
				`tabItem`.booking_no, " ",
				`tabItem`.container_no, " "
			) as cont_details,
			`tabPurchase Invoice Item`.base_rate ,
			`tabSales Invoice Item`.base_rate,
			`tabItem`.modified
		FROM 
			`tabItem`
		JOIN
			`tabItem Description`
		ON
			`tabItem`.item_code = `tabItem Description`.parent
		LEFT JOIN
			`tabPurchase Invoice Item`
		ON
			`tabItem Description`.parent = `tabPurchase Invoice Item`.item_code
		AND
			`tabPurchase Invoice Item`.docstatus = 1
		LEFT JOIN
			`tabSales Invoice Item`
		ON
			`tabItem Description`.parent = `tabSales Invoice Item`.item_code
		AND
			`tabItem Description`.vim_number = SUBSTRING_INDEX(`tabSales Invoice Item`.vim_number, '-', 1) 
		AND
			`tabSales Invoice Item`.docstatus = 1
		LEFT JOIN
			`tabAddress`
		ON
			`tabItem`.location = `tabAddress`.name
		WHERE	
			`tabItem`.item_type = 'Containers'

		
	""")