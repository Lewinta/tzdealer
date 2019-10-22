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
		("Color", "Data", 70),
		("Customer", "Link/Customer", 130),
		("Date", "Date", 90),
		("Payment Type", "Data", 100),
		("Paid Amount", "Currency", 100),
		("Payment Entry", "Link/Payment Entry", 100),
		("Sales Inv.", "Link/Sales Invoice", 100),
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

def get_conditions(filters):
	"""
	Return sql conditions ready to use in query

	NOTE: Value is mandatory if condition_type == value
	"""
	company = frappe.get_value("User Permission", {
			"user":frappe.session.user,
			"allow":"Company",
		}, "for_value")


	conditions = []

	# if filters.get('from_date'):
	# 	conditions.append(
	# 		("Payment Entry", "posting_date", ">=", filters.get('from_date'))
	# 	)

	# if filters.get('to_date'):
	# 	conditions.append(
	# 		("Payment Entry", "posting_date", "<=", filters.get('to_date'))
	# 	)

	# if filters.get('vim_number'):
	# 	conditions.append(
	# 		("Item", "item_code", "=", filters.get('vim_number'))
	# 	)

	if filters.get('customer'):
		conditions.append(
			("Payment Entry", "party", "=", filters.get('customer'))
		)

	sql_conditions = []

	if not conditions:
		return sql_conditions
	
	for doctype, fieldname, compare, value in conditions:

		if not value:
			continue
		if value == "NULL":
			sql_condition = "`tab{doctype}`.`{fieldname}` {compare} {value}" \
				.format(doctype=doctype, fieldname=fieldname, compare=compare,
					value=value)
		else:
			sql_condition = "`tab{doctype}`.`{fieldname}` {compare} '{value}'" \
				.format(doctype=doctype, fieldname=fieldname, compare=compare,
					value=value)

		sql_conditions.append(sql_condition)

	# frappe.errprint(conditions)

	return " And ".join(sql_conditions)


def get_fields(filters):
	"""
	Return sql fields ready to be used on query
	"""
	fields = (
		("Sales Invoice Item", "item_code"),
		("Item", "model"),
		("Item", "year"),
		("Item", "exterior_color"),
		# ("Purchase Invoice Item", "amount", "pinv_price"), 	#"OC/Price"
		# ("(SELECT SUM(`tabPurchase Invoice Item`.amount) from `tabPurchase Invoice Item` WHERE `tabPurchase Invoice Item`.item_code = 'fee' and `tabPurchase Invoice Item`.parent = `tabPurchase Invoice`.name ) as fee"), 	#"OC/Fee"
		# ("(SELECT SUM(IF(`tabLanded Cost Taxes and Charges`.supplier_invoice_type = 'Transport',`tabLanded Cost Taxes and Charges`.amount,0)) as transport FROM  `tabLanded Cost Purchase Receipt` JOIN `tabLanded Cost Item` ON `tabLanded Cost Purchase Receipt`.parent = `tabLanded Cost Item`.parent JOIN `tabLanded Cost Taxes and Charges` ON `tabLanded Cost Item`.parent = `tabLanded Cost Taxes and Charges`.parent WHERE `tabLanded Cost Taxes and Charges`.docstatus =1 AND `tabLanded Cost Item`.item_code = `tabPurchase Invoice Item`.item_code) as transport"), 	#"Transport"
		# ("(SELECT SUM(IF(`tabLanded Cost Taxes and Charges`.supplier_invoice_type = 'Courrier/Delivery',`tabLanded Cost Taxes and Charges`.amount,0)) as courrier_delivery FROM  `tabLanded Cost Purchase Receipt` JOIN `tabLanded Cost Item` ON `tabLanded Cost Purchase Receipt`.parent = `tabLanded Cost Item`.parent JOIN `tabLanded Cost Taxes and Charges` ON `tabLanded Cost Item`.parent = `tabLanded Cost Taxes and Charges`.parent WHERE `tabLanded Cost Taxes and Charges`.docstatus =1 AND `tabLanded Cost Item`.item_code = `tabPurchase Invoice Item`.item_code) as delivery"), 	#"Courrier/Delivery"
		# ("(SELECT SUM(IF(`tabLanded Cost Taxes and Charges`.supplier_invoice_type = 'Parts',`tabLanded Cost Taxes and Charges`.amount,0)) as courrier_delivery FROM  `tabLanded Cost Purchase Receipt` JOIN `tabLanded Cost Item` ON `tabLanded Cost Purchase Receipt`.parent = `tabLanded Cost Item`.parent JOIN `tabLanded Cost Taxes and Charges` ON `tabLanded Cost Item`.parent = `tabLanded Cost Taxes and Charges`.parent WHERE `tabLanded Cost Taxes and Charges`.docstatus =1 AND `tabLanded Cost Item`.item_code = `tabPurchase Invoice Item`.item_code) as parts"), 	#"Parts"
		# ("(SELECT SUM(IF(`tabLanded Cost Taxes and Charges`.supplier_invoice_type = 'Labor/Repair',`tabLanded Cost Taxes and Charges`.amount,0)) as courrier_delivery FROM  `tabLanded Cost Purchase Receipt` JOIN `tabLanded Cost Item` ON `tabLanded Cost Purchase Receipt`.parent = `tabLanded Cost Item`.parent JOIN `tabLanded Cost Taxes and Charges` ON `tabLanded Cost Item`.parent = `tabLanded Cost Taxes and Charges`.parent WHERE `tabLanded Cost Taxes and Charges`.docstatus =1 AND `tabLanded Cost Item`.item_code = `tabPurchase Invoice Item`.item_code) as repair"), 	#"Labor/Repair"
		# ("(SELECT SUM(IF(`tabLanded Cost Taxes and Charges`.supplier_invoice_type not in ('Transport', 'Courrier/Delivery', 'Parts', 'Labor/Repair'),`tabLanded Cost Taxes and Charges`.amount,0)) as courrier_delivery FROM  `tabLanded Cost Purchase Receipt` JOIN `tabLanded Cost Item` ON `tabLanded Cost Purchase Receipt`.parent = `tabLanded Cost Item`.parent JOIN `tabLanded Cost Taxes and Charges` ON `tabLanded Cost Item`.parent = `tabLanded Cost Taxes and Charges`.parent WHERE `tabLanded Cost Taxes and Charges`.docstatus =1 AND `tabLanded Cost Item`.item_code = `tabPurchase Invoice Item`.item_code) as others"), 	#"Others"
		# ("Sales Invoice Item", "amount", "sinv_price"),
		# ("Sales Invoice", "posting_date", "sinv_date"),
		("Sales Invoice", "customer"),
		# ("Sales Invoice", "status"),
		("Sales Invoice", "name", "sinv_name"),
		# ("Purchase Invoice", "name", "pinv_name"),
		# ("Purchase Invoice", "posting_date", "pinv_date"),
		# ("Purchase Invoice", "supplier"),
		("Payment Entry Reference", "parent", "payment_entry"),
		("Payment Entry", "posting_date", "p_posting_date"),
		("Payment Entry", "mode_of_payment"),
		("Payment Entry Reference", "allocated_amount"),
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
	conditions = get_conditions(filters)
	results = []
	data =  frappe.db.sql("""
		Select
			{fields}
			
		From
			`tabSales Invoice Item`
		Inner Join 
				`tabItem`
			On
				`tabItem`.item_code = `tabSales Invoice Item`.item_code
		Inner Join
			`tabSales Invoice`
			On
			`tabSales Invoice`.name = `tabSales Invoice Item`.parent
			And 
				`tabSales Invoice`.docstatus = 1
		Inner Join
			`tabPayment Entry Reference`
			On
			`tabPayment Entry Reference`.reference_name = `tabSales Invoice`.name
		Inner Join
			`tabPayment Entry`
			On
			`tabPayment Entry Reference`.parent = `tabPayment Entry`.name
			And 
			`tabPayment Entry`.docstatus = 1
		Group By 
			`tabPayment Entry`.name

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
				row.exterior_color,
				row.customer,
				row.p_posting_date,
				row.mode_of_payment,
				row.allocated_amount,
				row.payment_entry,
				row.sinv_name,
			)
		)
	return results
