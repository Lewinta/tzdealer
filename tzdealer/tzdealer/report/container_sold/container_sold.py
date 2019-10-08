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
			`tabSales Invoice`.docstatus = 1
		Inner Join 
			`tabItem`
		On
			`tabItem`.item_code = `tabSales Invoice Item`.item_code
		And
			`tabItem`.item_type = 'Containers'
		Where
			{conditions}
		""".format(fields=fields, conditions=conditions or "1 = 1"),
	filters, debug=False)

def get_columns(filters):
	"""
	Return Frappe columns ready to be used on report
	"""
	columns = (
		("Item Code", "item_code", "Link/Item", 110),
		("Container", "container", "Data", 110),
		("Seal No.", "seal", "Data", 100),
		("Booking No.", "booking", "Data", 100),
		("Shipping Line", "shipping_line", "Data", 110),
		("Price", "price", "Currency", 100),
		("Purchased Qty", "qty", "Int", 100),
		("Sales Inv.", "purchase_name", "Link/Sales Invoice", 110),
		("Sold Date", "p_date", "Date", 100),
		("Customer", "customer", "Link/Customer", 150),
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
		("Item", "item_code"),
		("Item", "container_no"),
		("Item", "seal_no"),
		("Item", "booking_no"),
		("Item", "shipping_line"),
		("Sales Invoice Item", "amount"),
		("Sales Invoice Item", "qty"),
		("Sales Invoice", "name"),
		("Sales Invoice", "posting_date"),
		("Sales Invoice", "customer"),
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
