# Copyright (c) 2013, TZCODE SRL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import cstr

__all__ = ["execute"]

def execute(filters={}):
	return get_columns(filters), \
		get_data(filters)

def get_columns(filters):
	"""
	Return Frappe columns ready to be used on report
	"""
	cols_obj = {
		"Stock Report": (
			("Item Code", "item_code", "Link/Item", 160),
			("Item Name", "item_name", "Data", 160),
			("Sales Price", "sales_price", "Currency", 100),
			("Status", "status", "Data", 90),
			("Purchase Date", "posting_date", "Date", 100),
			("Supplier", "supplier", "Link/Supplier", 200),
			("Invoice", "name", "Link/Purchase Invoice", 100),
			("Supplier Inv.", "name", "Data", 100),
		), 
		"Sold Report": (
			("Item Code", "item_code", "Link/Item", 160),
			("Item Name", "item_name", "Data", 160),
			("Price", "price", "Currency", 100),
			("Sold Qty", "qty", "Int", 100),
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
					`tabPurchase Invoice`.is_return = 0
				And 
					`tabPurchase Invoice`.docstatus = 1
			Inner Join
				`tabItem`
				On
					`tabPurchase Invoice Item`.item_code = `tabItem`.item_code
				And
					`tabItem`.item_type = 'Third Party Services'
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
			filters, debug=False)

	if filters.get("report_type") == "Sold Report":
		result = frappe.db.sql("""Select
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
				`tabItem`.item_type = 'Third Party Services'
			Where
				{conditions}
			""".format(fields=fields, conditions=conditions or "1 = 1"),
		filters, debug=False)

	return result

def get_fields(filters):
	"""
	Return sql fields ready to be used on query
	"""
	fields_obj = {
		"Stock Report":  (
			("Item", "item_code"),
			("Item", "item_name"),
			("""
				(
					Select
						(((`tabSingles`.value / 100) + 1) * `tabBin`.valuation_rate) As p
					From
						`tabSingles`
					Where
						`tabSingles`.doctype = "Configuration"
						And
							`tabSingles`.field = "default_revenue_rate"
				) As sales_price
			"""),
			("Item", "status"),
			# ("Purchase Invoice", "bill_date"),
			("Item", "purchase_date"),
			("Purchase Invoice", "supplier"),
			("Purchase Invoice", "name"),
			("Purchase Invoice", "bill_no"),
		),
		"Sold Report": (
			("Item", "item_code"),
			("Item", "item_name"),
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

def get_field(args):

	if len(args) == 2:
		doctype, fieldname = args
	else:
		return args if isinstance(args, basestring) \
			else " ".join(args)

	sql_field = "`tab{doctype}`.`{fieldname}`" \
		.format(doctype=doctype, fieldname=fieldname)

	return sql_field
