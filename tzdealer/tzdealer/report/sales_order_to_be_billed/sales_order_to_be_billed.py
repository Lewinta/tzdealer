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
		("Item", "item_code", "=", "%(item_code)s"),
		("Sales Order", "transaction_date", "=", "%(purchase_date)s"),
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
			`tabSales Order`
		Inner Join
			`tabSales Order Item`
			On
				`tabSales Order`.name = `tabSales Order Item`.parent
			And
				`tabSales Order`.docstatus = 1
			And
				`tabSales Order`.status in ('Not Billed', 'Partly Billed', 'To Deliver and Bill')
		Inner Join
				`tabPurchase Invoice Item`
			On
				`tabPurchase Invoice Item`.item_code = 	`tabSales Order Item`.item_code
		Inner Join
				`tabPurchase Invoice`
			On
				`tabPurchase Invoice Item`.parent = `tabPurchase Invoice`.name
			And
				`tabPurchase Invoice`.docstatus = 1
		Inner Join
			`tabItem`
			On
				`tabSales Order Item`.item_code = `tabItem`.item_code
		Inner Join
			`tabBin`
			On
				`tabItem`.item_code = `tabBin`.item_code
		Where
			{conditions}
		""".format(fields=fields, conditions=conditions or "1 = 1"),
	filters, debug=False)

def get_columns(filters):
	"""
	Return Frappe columns ready to be used on report
	"""
	columns = (
		("Status", "status", "Date", 100),
		("Vim Number", "item_code", "Link/Item", 160),
		("Model", "model", "Link/Model", 100),
		("Year", "year", "Int", 50),
		("Gear", "gear", "Data", 90),
		("Color", "exterior_color", "Data", 65),
		("Engine", "engine_size", "Data", 55),
		("Trim", "trim", "Data", 60),
		("Drive Train", "drive_train", "Data", 80),
		("Customer", "customer", "Link/Customer", 150),
		("Price", "price", "Currency", 100),
		("Order", "order_name", "Link/Sales Order", 100),
		("Order Date", "order_date", "Date", 100),
		("Order Status", "order_status", "Data", 90),
		("Odometer", "odometer_value", "Data", 90),
		("Salvage", "salvage_title", "Check", 70),
		("MK", "mk", "Data", 60),
		("Purchase Inv.", "purchase_name", "Link/Purchase Invoice", 110),
		("Purchase Date", "p_date", "Date", 100),
		("Supplier", "supplier", "Link/Supplier", 150),
		("Title Status", "title_status", "Data", 90),
	)

	formatted_columns = []

	for label, fieldname, fieldtype, width in columns:
		formatted_column = get_formatted_field(label=label,
			fieldtype=fieldtype, width=width)

		formatted_columns.append(formatted_column)

	return formatted_columns

def get_fields(filters):
	"""
	Return SQL fields ready to be used on query
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
		("Sales Order", "customer"),
		("Sales Order Item", "amount"),
		("Sales Order", "name"),
		("Sales Order", "transaction_date"),
		("Sales Order", "status"),
		("Item", "odometer_value"),
		("Item", "salvage_title"),
		("Item", "mk"),
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
