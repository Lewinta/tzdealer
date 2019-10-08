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
	company = frappe.get_value("User Permission", {
		"user":frappe.session.user,
		"allow":"Company",
	}, "for_value")

	conditions = (
		("Item", "company", "=", company),
	)

	sql_conditions = []

	for doctype, fieldname, compare, value in conditions:

		if not value:
			continue

		sql_condition = "`tab{doctype}`.`{fieldname}` {compare} '{value}'" \
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

	if filters.get("report_type") == "Stock Report":
		result = frappe.db.sql("""
			Select
				{fields},
				(Select Sum(actual_qty) from `tabStock Ledger Entry` where item_code = `tabPurchase Invoice Item`.item_code) as qty
			From
				`tabPurchase Invoice`
			Inner Join
				`tabPurchase Invoice Item`
				On
					`tabPurchase Invoice`.name = `tabPurchase Invoice Item`.parent
				And
					`tabPurchase Invoice`.docstatus = 1
			Inner Join 
					`tabItem`
				On
					`tabItem`.item_code = `tabPurchase Invoice Item`.item_code
				And
					`tabItem`.item_type = 'Containers'
			Inner Join 
				`tabItem Description`
			On
				`tabItem Description`.parent = `tabItem`.item_code
			Where
				{conditions}
			Having 
				qty > 0
				
		""".format(fields=fields, conditions=conditions or "1 = 1"),
		filters, debug=False)

	if filters.get("report_type") == "Sold Report":
		result = frappe.db.sql("""
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
				`tabItem Description`
			On
				`tabItem Description`.item_code = SUBSTRING_INDEX(`tabSales Invoice Item`.vim_number,'-', 1)
			Inner Join 
				`tabItem`
			On
				`tabItem`.item_code = `tabSales Invoice Item`.item_code
			And
				`tabItem`.item_type = 'Containers'
			Where
				{conditions}
			Group By
				`tabItem Description`.item_code

			""".format(fields=fields, conditions=conditions or "1 = 1"),
		filters, debug=False)

	return result
# SUBSTRING_INDEX(`tabSales Invoice Item`.vim_number, '-', 1)
def get_columns(filters):
	"""
	Return Frappe columns ready to be used on report
	"""
	cols_obj = {
		"Stock Report":(
			("Item Code", "item_code", "Link/Item", 110),
			("Booking No.", "booking", "Data", 100),
			("Container", "container", "Data", 110),
			("Shipping Line", "shipping_line", "Data", 110),
			("Vim Number", "vim_number", "Link/Item", 150),
			("Make", "make", "Data", 80),
			("Year", "year", "Data", 80),
			("Price", "rate", "Currency", 90),
			("Purchased Qty", "conversion_factor", "Int", 100),
			("Purchase Date", "p_date", "Date", 100),
			("Supplier", "supplier", "Link/Supplier", 150),
			("Purchase Inv.", "purchase_name", "Link/Purchase Invoice", 110),
			("Actual Qty", "qty", "Int", 100),
		),
		"Sold Report":(
			("Item Code", "item_code", "Link/Item", 110),
			("Booking No.", "booking", "Data", 100),
			("Container", "container", "Data", 110),
			("Shipping Line", "shipping_line", "Data", 110),
			("Vim Number", "vim_number", "Link/Item", 150),
			("Make", "make", "Data", 80),
			("Year", "year", "Data", 80),
			("Price", "price", "Currency", 90),
			("Purchased Qty", "qty", "Int", 100),
			("Sales Inv.", "purchase_name", "Link/Sales Invoice", 110),
			("Sold Date", "p_date", "Date", 100),
			("Customer", "customer", "Link/Customer", 150),
		)
	}

	columns = cols_obj.get(filters.get("report_type"))
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
	fields_obj = {
		"Stock Report":  (
			("Item", "item_code"),
			("Item", "booking_no"),
			("Item", "container_no"),
			("Item", "shipping_line"),
			("Item Description", "item_code", "vim_number"),
			("Item Description", "model", "model"),
			("Item Description", "year", "year"),
			("Purchase Invoice Item", "rate"),
			("Purchase Invoice Item", "conversion_factor"),
			("Purchase Invoice", "posting_date"),
			("Purchase Invoice", "supplier"),
			("Purchase Invoice", "name"),
		),
		"Sold Report":(
			("Item", "item_code"),
			("Item", "booking_no"),
			("Item", "container_no"),
			("Item", "shipping_line"),
			("Item Description", "item_code", "vim_number"),
			("Item Description", "model", "model"),
			("Item Description", "year", "year"),
			("Sales Invoice Item", "amount"),
			("Sales Invoice Item", "qty"),
			("Sales Invoice", "name"),
			("Sales Invoice", "posting_date"),
			("Sales Invoice", "customer"),
		)
	}

	fields = fields_obj.get(filters.get("report_type"))

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
