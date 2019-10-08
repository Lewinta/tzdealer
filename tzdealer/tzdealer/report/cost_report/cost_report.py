	# Copyright (c) 2013, TZCODE SRL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cstr, flt

def execute(filters=None):
	return get_columns(), get_data(filters)

def get_columns():
	columns = (
		("Vim Number", "Link/Item", 150),
		("Model", "Data", 100),
		("Year", "Data", 60),
		("Gear", "Data", 100),
		("Color", "Data", 70),
		("Engine", "Data", 70),
		("Trim", "Data", 100),
		("Train", "Data",50),
		("OC/Price", "Currency", 100),
		("OC/Fee", "Currency", 100),
		("Transport", "Currency", 100),
		("Courrier/Delivery", "Currency", 115),
		("Parts", "Currency", 100),
		("Labor/Repair", "Currency", 100),
		("Others", "Currency", 100),
		("Total Cost", "Currency", 100),
		("Sales Price", "Currency", 100),
		("Sold Date", "Date", 90),
		("Customer", "Link/Customer", 130),
		("Billing Status", "Data", 90),
		("Sales Inv.", "Link/Sales Invoice", 100),
		("Purchase Inv.", "Link/Purchase Invoice", 100),
		("Purchase Date", "Date", 90),
		("Supplier ", "Link/Supplier", 130),
	)

	formatted_columns = []
	
	for label, fieldtype, width in columns:
		formatted_columns.append(
			get_formatted_column(label, fieldtype, width)
		)

	return formatted_columns

def get_formatted_column(label, fieldtype, width):
	# [label]:[fieldtype/Options]:width
	parts = (
		_(label),
		fieldtype,
		cstr(width)
	)
	return ":".join(parts)

def get_fields(filters):
	"""
	Return sql fields ready to be used on query
	"""
	fields = (
		("Item", "item_code"),
		("Item", "model"),
		("Item", "year"),
		("Item", "gear"),
		("Item", "exterior_color"),
		("Item", "engine"),
		("Item", "trim"),
		("Item", "drive_train"),
		("Purchase Invoice Item", "amount", "pinv_price"), 	#"OC/Price"
		("(SELECT SUM(`tabPurchase Invoice Item`.amount) from `tabPurchase Invoice Item` WHERE `tabPurchase Invoice Item`.item_code = 'fee' and `tabPurchase Invoice Item`.parent = `tabPurchase Invoice`.name ) as fee"), 	#"OC/Fee"
		("(SELECT SUM(IF(`tabLanded Cost Taxes and Charges`.supplier_invoice_type = 'Transport',`tabLanded Cost Taxes and Charges`.amount,0)) as transport FROM  `tabLanded Cost Purchase Receipt` JOIN `tabLanded Cost Item` ON `tabLanded Cost Purchase Receipt`.parent = `tabLanded Cost Item`.parent JOIN `tabLanded Cost Taxes and Charges` ON `tabLanded Cost Item`.parent = `tabLanded Cost Taxes and Charges`.parent WHERE `tabLanded Cost Taxes and Charges`.docstatus =1 AND `tabLanded Cost Item`.item_code = `tabPurchase Invoice Item`.item_code) as transport"), 	#"Transport"
		("(SELECT SUM(IF(`tabLanded Cost Taxes and Charges`.supplier_invoice_type = 'Courrier/Delivery',`tabLanded Cost Taxes and Charges`.amount,0)) as courrier_delivery FROM  `tabLanded Cost Purchase Receipt` JOIN `tabLanded Cost Item` ON `tabLanded Cost Purchase Receipt`.parent = `tabLanded Cost Item`.parent JOIN `tabLanded Cost Taxes and Charges` ON `tabLanded Cost Item`.parent = `tabLanded Cost Taxes and Charges`.parent WHERE `tabLanded Cost Taxes and Charges`.docstatus =1 AND `tabLanded Cost Item`.item_code = `tabPurchase Invoice Item`.item_code) as delivery"), 	#"Courrier/Delivery"
		("(SELECT SUM(IF(`tabLanded Cost Taxes and Charges`.supplier_invoice_type = 'Parts',`tabLanded Cost Taxes and Charges`.amount,0)) as courrier_delivery FROM  `tabLanded Cost Purchase Receipt` JOIN `tabLanded Cost Item` ON `tabLanded Cost Purchase Receipt`.parent = `tabLanded Cost Item`.parent JOIN `tabLanded Cost Taxes and Charges` ON `tabLanded Cost Item`.parent = `tabLanded Cost Taxes and Charges`.parent WHERE `tabLanded Cost Taxes and Charges`.docstatus =1 AND `tabLanded Cost Item`.item_code = `tabPurchase Invoice Item`.item_code) as parts"), 	#"Parts"
		("(SELECT SUM(IF(`tabLanded Cost Taxes and Charges`.supplier_invoice_type = 'Labor/Repair',`tabLanded Cost Taxes and Charges`.amount,0)) as courrier_delivery FROM  `tabLanded Cost Purchase Receipt` JOIN `tabLanded Cost Item` ON `tabLanded Cost Purchase Receipt`.parent = `tabLanded Cost Item`.parent JOIN `tabLanded Cost Taxes and Charges` ON `tabLanded Cost Item`.parent = `tabLanded Cost Taxes and Charges`.parent WHERE `tabLanded Cost Taxes and Charges`.docstatus =1 AND `tabLanded Cost Item`.item_code = `tabPurchase Invoice Item`.item_code) as repair"), 	#"Labor/Repair"
		("(SELECT SUM(IF(`tabLanded Cost Taxes and Charges`.supplier_invoice_type not in ('Transport', 'Courrier/Delivery', 'Parts', 'Labor/Repair'),`tabLanded Cost Taxes and Charges`.amount,0)) as courrier_delivery FROM  `tabLanded Cost Purchase Receipt` JOIN `tabLanded Cost Item` ON `tabLanded Cost Purchase Receipt`.parent = `tabLanded Cost Item`.parent JOIN `tabLanded Cost Taxes and Charges` ON `tabLanded Cost Item`.parent = `tabLanded Cost Taxes and Charges`.parent WHERE `tabLanded Cost Taxes and Charges`.docstatus =1 AND `tabLanded Cost Item`.item_code = `tabPurchase Invoice Item`.item_code) as others"), 	#"Others"
		("Sales Invoice Item", "amount", "sinv_price"),
		("Sales Invoice", "posting_date", "sinv_date"),
		("Sales Invoice", "customer"),
		("Sales Invoice", "status"),
		("Sales Invoice", "name", "sinv_name"),
		("Purchase Invoice", "name", "pinv_name"),
		("Purchase Invoice", "posting_date", "pinv_date"),
		("Purchase Invoice", "supplier"),
	)
		
	sql_fields = []

	for args in fields:
		sql_field = get_field(args)

		sql_fields.append(sql_field)

	return ", ".join(sql_fields)

def get_field(args):

	if len(args) == 2:
		doctype, fieldname = args
		alias = fieldname
	elif len(args) == 3:
		doctype, fieldname, alias = args
	else:
		return args if isinstance(args, basestring) \
			else " ".join(args)

	sql_field = "`tab{doctype}`.`{fieldname}` as {alias}" \
		.format(doctype=doctype, fieldname=fieldname, alias=alias)

	return sql_field

def get_data(filters):
	"""
	Return the data that needs to be rendered
	"""
	fields = get_fields(filters)
	conditions = ''
	results = []
	data =  frappe.db.sql("""
		Select
			{fields}
			
		From
			`tabPurchase Invoice Item`
		Inner Join 
			`tabItem`
			On
				`tabItem`.item_code = `tabPurchase Invoice Item`.item_code
			And 
				`tabItem`.item_type = 'Vehicles'
		Left Join
			`tabPurchase Invoice`
			On
				`tabPurchase Invoice`.name = `tabPurchase Invoice Item`.parent
			And
				`tabPurchase Invoice`.docstatus = 1	
		Left Join
			`tabSales Invoice Item`
			On
				`tabItem`.item_code = `tabSales Invoice Item`.item_code
		Left Join
			`tabSales Invoice`
			On
			`tabSales Invoice`.name = `tabSales Invoice Item`.parent
			And 
				`tabSales Invoice`.docstatus = 1
		
		Where
			{conditions}

		Group By 
			`tabPurchase Invoice Item`.item_code

		""".format(fields=fields, conditions=conditions or "1 = 1"),
	filters, as_dict=True, debug=False)

	for row in data:
		total_costs = flt(row.pinv_price) + flt(row.fee) + flt(row.transport) + \
			flt(row.delivery) + flt(row.parts) + flt(row.repair) + flt(row.others)
		results.append(
			(
				row.item_code,
				row.model,
				row.year,
				row.gear,
				row.exterior_color,
				row.engine,
				row.trim,
				row.drive_train,
				row.pinv_price,
				row.fee, 	#"OC/Fee"
				row.transport, 	#"Transport"
				row.delivery, 	#"Courrier/Delivery"
				row.parts, 	#"Parts"
				row.repair, 	#"Labor/Repair"
				row.others, 	#"Others"
				total_costs,
				row.sinv_price,
				row.sinv_date,
				row.customer,
				row.status,
				row.sinv_name,
				row.pinv_name,
				row.pinv_date,
				row.supplier,
			)
		)
	return results
