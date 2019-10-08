# Copyright (c) 2013, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import cstr

__all__ = ["execute"]

def execute(filters={}):
	return get_columns(filters), \
		get_data(filters)

def get_conditions(filters):
	"""
	Return sql conditions ready to use in query

	NOTE: Value is mandatory if condition_type == value
	"""
	conditions = (
		("Sales Invoice", "customer", "=", "%(customer)s"),
	)

	sql_conditions = []

	for doctype, fieldname, compare, value in conditions:

		if not filters.get(value):
			frappe.errprint(filters.get(value))
			continue

		sql_condition = "`tab{doctype}`.`{fieldname}` {compare} {value}" \
			.format(doctype=doctype, fieldname=fieldname, compare=compare,
				value=value)

		sql_conditions.append(sql_condition)

	return " And ".join(sql_conditions)

def get_formatted_field(label, width=100, fieldtype=None):
	"""
	Returns formatted string
		[Label]:[Field Type]/[Options]:[Width]
	"""
	from frappe import _

	parts = (
		_(label).title(),
		fieldtype if fieldtype else "Data",
		cstr(width),
	)
	return ":".join(parts)

def get_data(filters):
	"""
	Return the data that needs to be rendered
	"""
	fields = get_fields(filters)
	conditions = get_conditions(filters)

	return frappe.db.sql("""
		Select
			{fields}
		From
			`tabSales Invoice`
		Inner Join
			`tabSales Invoice Item`
			On
				`tabSales Invoice`.name = `tabSales Invoice Item`.parent
			And 
				`tabSales Invoice`.is_return = 0
			And 
				`tabSales Invoice`.docstatus = 1
		Inner Join
			`tabPurchase Invoice Item`
			On
				`tabPurchase Invoice Item`.item_code = `tabSales Invoice Item`.item_code
		Inner Join
			`tabPurchase Invoice`
			On
				`tabPurchase Invoice Item`.parent = `tabPurchase Invoice`.name
			And
				`tabPurchase Invoice`.docstatus = 1
		Inner Join
			`tabItem`
			On
				`tabSales Invoice Item`.item_code = `tabItem`.item_code

		Where
			{conditions}
		""".format(fields=fields, conditions=conditions or "1 = 1"),
	filters, debug=False)

def get_columns(filters):
	"""
	Return Frappe columns ready to be used on report
	"""
	columns = (
		("Status", "status", "data", 100),
		("Vim Number", "item_code", "Link/Item", 160),
		("Model", "model", "Link/Model", 100),
		("Year", "year", "Int", 50),
		("Gear", "gear", "Data", 90),
		("Color", "exterior_color", "Data", 65),
		("Engine", "engine_size", "Data", 55),
		("Trim", "trim", "Data", 60),
		("Drive Train", "drive_train", "Data", 80),
		("Sales Price", "sales_price", "Currency", 100),
		("Sold Date", "posting_date", "Date", 100),
		("Customer", "customer", "Link/Customer", 200),
		# ("Sales Order", "sales_order", "Link/Sales Order", 100),
		("Billing Status", "billing_status", "Data", 100),
		("Sales Inv.", "sales_name", "Link/Sales Invoice", 100),
		("Purchase Inv.", "purchase_name", "Link/Purchase Invoice", 100),
		("Purchase Date", "purchase_date", "Date", 100),
		("Supplier", "supplier", "Link/Supplier", 100),
		("Title", "title_status", "data", 100),
	)

	formatted_columns = []

	for label, fieldname, fieldtype, width in columns:
		formatted_column = get_formatted_field(label=label,
			fieldtype=fieldtype, width=width)

		formatted_columns.append(formatted_column)

	return formatted_columns

def get_fields(filters):
	"""
	Return sql fields ready to be used on query
	"""

	fields = (
		("Item", "status"),
		("Item", "item_code"),
		("Item", "model"),
		("Item", "year"),
		("Item", "gear"),
		("Item", "exterior_color"),
		("Item", "engine_size"),
		("Item", "trim"),
		("Item", "drive_train"),
		("Sales Invoice Item", "amount"),
		("Sales Invoice", "posting_date"),
		("Sales Invoice", "customer"),
		("Sales Invoice Item", "sales_order"),
		# ("Sales Order", "billing_status"),
		("Sales Invoice", "name"),
		("Purchase Invoice", "name"),
		("Purchase Invoice", "posting_date"),
		("Purchase Invoice", "supplier"),
		("Item", "title_status"),
	)

	sql_fields = []

	for args in fields:
		sql_field = get_field(args)

		sql_fields.append(sql_field)

	return ", ".join(sql_fields)

def get_field(args):

	if len(args) == 2:
		doctype, fieldname = args
	else:
		return args if isinstance(args, basestring) \
			else " ".join(args)

	sql_field = "`tab{doctype}`.`{fieldname}`" \
		.format(doctype=doctype, fieldname=fieldname)

	return sql_field
