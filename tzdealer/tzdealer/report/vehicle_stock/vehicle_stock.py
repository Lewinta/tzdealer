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
		("Purchase Invoice", "posting_date", "=", "%(purchase_date)s"),
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
			{fields},
			(Select Sum(actual_qty) from `tabStock Ledger Entry` where item_code = `tabPurchase Invoice Item`.item_code) as qty
		From
			`tabPurchase Invoice`
		Inner Join
			`tabPurchase Invoice Item`
			On
				`tabPurchase Invoice`.name = `tabPurchase Invoice Item`.parent
			And 
				`tabPurchase Invoice`.is_return = 0
			And 
				`tabPurchase Invoice`.docstatus = 1
		Inner Join
			`tabItem`
			On
				`tabPurchase Invoice Item`.item_code = `tabItem`.item_code
			And
				`tabItem`.item_code not in (
					Select 
						item_code 
					From 
						`tabSales Order Item` 
					Where
						`tabSales Order Item`.docstatus = 1
				)
		Inner Join
			`tabBin`
			On
				`tabItem`.item_code = `tabBin`.item_code
		Inner Join
			(
				Select
					`tabSingles`.value As margin_rate
				From
					`tabSingles`
				Where
					`tabSingles`.doctype = "Configuration"
					And
						`tabSingles`.field = "default_revenue_rate"
			) As `tabSales Price`
		Where
			{conditions}
			Having 
			qty > 0
		""".format(fields=fields, conditions=conditions or "1 = 1"),
	filters, debug=True)

def get_columns(filters):
	"""
	Return Frappe columns ready to be used on report
	"""
	columns = (
		("Vim Number", "item_code", "Link/Item", 160),
		("Model", "model", "Link/Model", 100),
		("Year", "year", "Int", 50),
		("Gear", "gear", "Data", 90),
		("Color", "exterior_color", "Data", 65),
		("Engine", "engine_size", "Data", 55),
		("Trim", "trim", "Data", 60),
		("Drive Train", "drive_train", "Data", 80),
		("Sales Price", "sales_price", "Currency", 100),
		("Status", "status", "Data", 90),
		# ("Item Name", "item_name", "Data", 200),
		("Purchase Date", "posting_date", "Date", 100),
		# ("Valuation Rate", "valuation_rate", "Currency", 100),
		("Supplier", "supplier", "Link/Supplier", 200),
		("Invoice", "name", "Link/Purchase Invoice", 100),
		("Odometer", "odometer_value", "Data", 90),
		("MK", "mk", "Data", 60),
		("Title Status", "title_status", "Data", 90),
		("Supplier Inv.", "name", "Data", 100),
		# ("Margin Amount", "margin_amount", "Currency"),
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
		("Item", "model"),
		("Item", "year"),
		("Item", "gear"),
		("Item", "exterior_color"),
		("Item", "engine_size"),
		("Item", "trim"),
		("Item", "drive_train"),
		# ("Item", "item_name"),
		("""
			(
				Select
					(((`tabSingles`.value / 100) + 1) * (`tabBin`.valuation_rate + `tabPurchase Invoice`.total - `tabPurchase Invoice Item`.rate)) As p
				From
					`tabSingles`
				Where
					`tabSingles`.doctype = "Configuration"
					And
						`tabSingles`.field = "default_revenue_rate"
			) As sales_price
		"""),
		("Item", "status"),
		("Purchase Invoice", "bill_date"),
		# ("Bin", "valuation_rate"),
		("Purchase Invoice", "supplier"),
		("Purchase Invoice", "name"),
		("Item", "odometer_value"),
		("Item", "mk"),
		("Item", "title_status"),
		("Purchase Invoice", "bill_no"),
		# ("Sales Price", "margin_amount"),
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
