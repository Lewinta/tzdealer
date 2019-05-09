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
	cond_obj = {
		# "Stock Report": (
		# 	(),
		# ),
		# "Sold Report": (
		# 	(),
		# ),
		"Sales Order To Be Billed": (
			("Sales Invoice Item", "parent", "IS", "NULL"),
		)
	}

	conditions = cond_obj.get(filters.get("report_type"))

	sql_conditions = []

	if not conditions:
		return sql_conditions
	
	for doctype, fieldname, compare, value in conditions:

		if not value:
			continue

		sql_condition = "`tab{doctype}`.`{fieldname}` {compare} {value}" \
			.format(doctype=doctype, fieldname=fieldname, compare=compare,
				value=value)

		sql_conditions.append(sql_condition)

	frappe.errprint(conditions)

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
	results = []
	if filters.get("report_type") == "Stock Report":
		results = frappe.db.sql("""
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
					`tabItem`.item_type = 'Vehicles'
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
	
	if filters.get("report_type") == "Sold Report":
		results = frappe.db.sql("""
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
		filters, debug=True)

	if filters.get("report_type") == "Sales Order To Be Billed":
		results = frappe.db.sql("""
			Select
				{fields}
			FROM 
				`tabSales Order Item` 
			LEFT JOIN
				`tabSales Invoice Item`
			ON
				`tabSales Order Item`.item_code = `tabSales Invoice Item`.item_code
			JOIN
				`tabItem`
			ON
				`tabSales Order Item`.item_code = `tabItem`.item_code
			JOIN 
				`tabSales Order`
			ON 
				`tabSales Order Item`.parent = `tabSales Order`.name
			AND
				`tabSales Order`.status in ('Not Billed', 'Partly Billed', 'To Deliver and Bill')
			JOIN
				`tabPurchase Invoice Item`
			ON
				`tabSales Order Item`.item_code = `tabPurchase Invoice Item`.item_code
			JOIN
				`tabPurchase Invoice`
			ON
				`tabPurchase Invoice Item`.parent = `tabPurchase Invoice`.name
			AND
				`tabPurchase Invoice`.docstatus = 1
			Where
				{conditions}
			""".format(fields=fields, conditions=conditions or "1 = 1"),
		filters, debug=True)

	return results

def get_columns(filters):
	"""
	Return Frappe columns ready to be used on report
	"""
	cols_obj = {
		"Stock Report": (
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
			("Purchase Date", "posting_date", "Date", 100),
			("Supplier", "supplier", "Link/Supplier", 200),
			("Invoice", "name", "Link/Purchase Invoice", 100),
			("Odometer", "odometer_value", "Data", 90),
			("Salvage", "salvage_title", "Check", 70),
			("MK", "mk", "Data", 60),
			("Title Status", "title_status", "Data", 90),
			("Supplier Inv.", "name", "Data", 100),
		),
		"Sold Report":(
			("Vim Number", "item_code", "Link/Item", 160),
			("Model", "model", "Link/Model", 100),
			("Year", "year", "Int", 50),
			("Gear", "gear", "Data", 90),
			("Color", "exterior_color", "Data", 65),
			("Engine", "engine_size", "Data", 55),
			("Trim", "trim", "Data", 60),
			("Drive Train", "drive_train", "Data", 80),
			("Sales Price", "sales_price", "Currency", 100),
			("Status", "status", "data", 100),
			("Sold Date", "posting_date", "Date", 100),
			("Customer", "customer", "Link/Customer", 200),
			("Billing Status", "billing_status", "Data", 100),
			("Sales Inv.", "sales_name", "Link/Sales Invoice", 100),
			("Purchase Inv.", "purchase_name", "Link/Purchase Invoice", 100),
			("Purchase Date", "purchase_date", "Date", 100),
			("Supplier", "supplier", "Link/Supplier", 100),
			("Title", "title_status", "data", 100),
		),
		"Sales Order To Be Billed":(
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
		),

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
			("Item", "salvage_title"),
			("Item", "mk"),
			("Item", "title_status"),
			("Purchase Invoice", "bill_no"),
			# ("Sales Price", "margin_amount"),
		),
		"Sold Report": (
			("Item", "item_code"),
			("Item", "model"),
			("Item", "year"),
			("Item", "gear"),
			("Item", "exterior_color"),
			("Item", "engine_size"),
			("Item", "trim"),
			("Item", "drive_train"),
			("Sales Invoice Item", "amount"),
			("Item", "status"),
			("Sales Invoice", "posting_date"),
			("Sales Invoice", "customer"),
			("Sales Invoice Item", "sales_order"),
			# ("Sales Order", "billing_status"),
			("Sales Invoice", "name"),
			("Purchase Invoice", "name"),
			("Purchase Invoice", "posting_date"),
			("Purchase Invoice", "supplier"),
			("Item", "title_status"),
		),
		"Sales Order To Be Billed":(
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
	else:
		return args if isinstance(args, basestring) \
			else " ".join(args)

	sql_field = "`tab{doctype}`.`{fieldname}`" \
		.format(doctype=doctype, fieldname=fieldname)

	return sql_field
