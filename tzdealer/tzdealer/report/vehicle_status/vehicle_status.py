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

	default_condition = []
	
	if filters.get('title_status'):
		default_condition.append(("Item", "title_status", "=", filters.get('title_status')))
	
	if filters.get('status'):
		default_condition.append(("Item", "status", "=", filters.get('status')))	
	
	if filters.get('company'):
		default_condition.append(("Item", "company", "=", company))



	cond_obj = {
		"All": default_condition,
		"Stock Report": default_condition,
		"Sold Report": default_condition,
		"Sales Order To Be Billed": default_condition + [("Sales Invoice Item", "parent", "IS", "NULL")]
	}
	# else:
	# 	cond_obj = {
	# 		"Stock Report": (
	# 			("Item", "company", "=", company),
	# 		),
	# 		"Sold Report": (
	# 			("Item", "company", "=", company),
	# 		),
	# 		"Sales Order To Be Billed": (
	# 			("Sales Invoice Item", "parent", "IS", "NULL"),
	# 			("Item", "company", "=", company),
	# 		)
	# 	}


	conditions = cond_obj.get(filters.get("report_type"))

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
	
	if filters.get("report_type") == "All":
		cond_1   = get_conditions({"report_type": "All-1"})
		fields_1 = get_fields({"report_type": "All-1"})
		cond_2   = get_conditions({"report_type": "All-2"})
		fields_2 = get_fields({"report_type": "All-2"})

		results = frappe.db.sql("""
			Select
				{fields_1},
				(Select Sum(actual_qty) from `tabStock Ledger Entry` where item_code = `tabPurchase Invoice Item`.item_code) as qty
			From
				`tabPurchase Invoice`
			Inner Join
				`tabSupplier`
			ON
				`tabSupplier`.name = `tabPurchase Invoice`.supplier
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
			Left Join
				`tabAddress`
			On
				`tabItem`.location = `tabAddress`.name
			Where
				{cond_1}
				Having 
				qty > 0

			UNION 
			
			Select
				{fields_2},
				0 as other_sum
			From
				`tabSales Invoice`
			Inner Join
				`tabCustomer`
			ON
				`tabCustomer`.name = `tabSales Invoice`.customer
			Inner Join
				`tabSales Invoice Item`
				On
					`tabSales Invoice`.name = `tabSales Invoice Item`.parent
				And 
					`tabSales Invoice`.is_return = 0
				And 
					`tabSales Invoice`.docstatus = 1
			Inner Join
				`tabItem`
				On
					`tabSales Invoice Item`.item_code = `tabItem`.item_code
				And 
					`tabItem`.item_type = 'Vehicles'
		
			Left Join
			`tabBin`
				On
					`tabItem`.item_code = `tabBin`.item_code
			
			Left Join
				`tabPurchase Invoice Item`
				On
					`tabPurchase Invoice Item`.item_code = `tabItem`.item_code
	
			Left Join
				`tabPurchase Invoice`
				On
					`tabPurchase Invoice Item`.parent = `tabPurchase Invoice`.name
				And
					`tabPurchase Invoice`.docstatus = 1
			Left Join
				`tabSupplier`
			ON
				`tabSupplier`.name = `tabPurchase Invoice`.supplier
			Left Join
				`tabAddress`
			On
				`tabItem`.location = `tabAddress`.name
			
			Where
				`tabPurchase Invoice`.is_return = 0 AND
				{cond_2}

			""".format(
				fields_1=fields_1,
				fields_2=fields_2,
				cond_1=cond_1 or "1 = 1",
				cond_2=cond_2 or "1 = 1"
			), debug=False)

	if filters.get("report_type") == "Stock Report":
		results = frappe.db.sql("""
			Select
				{fields},
				(Select Sum(actual_qty) from `tabStock Ledger Entry` where item_code = `tabPurchase Invoice Item`.item_code) as qty
			From
				`tabPurchase Invoice`
			Inner Join
				`tabSupplier`
			ON
				`tabSupplier`.name = `tabPurchase Invoice`.supplier
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
			Left Join
				`tabAddress`
			On
				`tabItem`.location = `tabAddress`.name
			Left Join
				`tabVehicle Release`
			On
				`tabVehicle Release`.name = `tabItem`.name	
			Where
				{conditions}
				Having 
				qty > 0
			""".format(fields=fields, conditions=conditions or "1 = 1"),
		filters, debug=False)
	
	if filters.get("report_type") == "Sold Report":
		results = frappe.db.sql("""
			Select
				{fields}
			From
				`tabSales Invoice`
			Inner Join
				`tabCustomer`
			ON
				`tabCustomer`.name = `tabSales Invoice`.customer
			Inner Join
				`tabSales Invoice Item`
				On
					`tabSales Invoice`.name = `tabSales Invoice Item`.parent
				And 
					`tabSales Invoice`.is_return = 0
				And 
					`tabSales Invoice`.docstatus = 1
			Inner Join
				`tabItem`
				On
					`tabSales Invoice Item`.item_code = `tabItem`.item_code
				And 
					`tabItem`.item_type = 'Vehicles'
		
			Left Join
			`tabBin`
				On
					`tabItem`.item_code = `tabBin`.item_code
			
			Left Join
				`tabPurchase Invoice Item`
				On
					`tabPurchase Invoice Item`.item_code = `tabItem`.item_code
	
			Left Join
				`tabPurchase Invoice`
				On
					`tabPurchase Invoice Item`.parent = `tabPurchase Invoice`.name
				And
					`tabPurchase Invoice`.docstatus = 1
			Left Join
				`tabSupplier`
			ON
				`tabSupplier`.name = `tabPurchase Invoice`.supplier
			Left Join
				`tabAddress`
			On
				`tabItem`.location = `tabAddress`.name
			Left Join
				`tabVehicle Release`
			On
				`tabVehicle Release`.name = `tabItem`.name	
			Where
				`tabPurchase Invoice`.is_return = 0 AND
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
			And 
				`tabItem`.item_type = 'Vehicles'
			JOIN 
				`tabSales Order`
			ON 
				`tabSales Order Item`.parent = `tabSales Order`.name
			AND
				`tabSales Order`.status in ('Not Billed', 'Partly Billed', 'To Deliver and Bill')
			JOIN
				`tabCustomer`
			ON
				`tabCustomer`.name = `tabSales Order`.customer
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
			JOIN
				`tabSupplier`
			ON
				`tabSupplier`.name = `tabPurchase Invoice`.supplier
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
			Left Join
				`tabAddress`
			On
				`tabItem`.location = `tabAddress`.name
			Where
				{conditions}
			""".format(fields=fields, conditions=conditions or "1 = 1"),
		filters, debug=False)

	return results

def get_columns(filters):
	"""
	Return Frappe columns ready to be used on report
	"""
	cols_obj = {
		"All": (
			("Status", "status", "Data", 90),
			("Company", "company", "Data", 120),
			("S. Location", "location", "Data", 230),
			("Kijiji", "kijiji", "Check", 50),
			("Auto Trd", "auto_trd", "Check", 50),
			("Web", "web", "Check", 50),
			("Stock No.", "item_code", "Link/Item", 105),
			("Vim Number", "vim_number", "Data", 160),
			("Model", "model", "Link/Model", 100),
			("Year", "year", "Int", 50),
			("Color", "exterior_color", "Data", 65),
			("Gear", "gear", "Data", 50),
			("Engine", "engine_size", "Data", 55),
			("Trim", "trim", "Data", 60),
			("Drive Train", "drive_train", "Data", 80),
			("Voucher", "landed_cost_voucher_amount", "Currency", 90),
			("Sales Price", "sales_price", "Currency", 100),
			("Purchase Date", "posting_date", "Date", 100),
			("Supplier", "supplier", "Link/Supplier", 200),
			("Invoice", "name", "Link/Purchase Invoice", 100),
			("Salvage", "salvage_title", "Check", 70),
			("Odometer", "odometer_value", "Int", 90),
			("MK", "mk", "Data", 60),
			("Title Status", "title_status", "Data", 90),
			("Supplier Inv.", "name", "Data", 100),
			("Telephone", "s_phone", "data", 90),
		),
		"Stock Report": (
			("Status", "status", "Data", 90),
			("Company", "company", "Data", 120),
			("S. Location", "location", "Data", 230),
			("Kijiji", "kijiji", "Check", 50),
			("Auto Trd", "auto_trd", "Check", 50),
			("Web", "web", "Check", 50),
			("Checklist", "checklist", "Data", 90),
			("Stock No.", "item_code", "Link/Item", 105),
			("Vim Number", "vim_number", "Data", 160),
			("Model", "model", "Link/Model", 100),
			("Year", "year", "Int", 50),
			("Color", "exterior_color", "Data", 65),
			("Gear", "gear", "Data", 50),
			("Engine", "engine_size", "Data", 55),
			("Trim", "trim", "Data", 60),
			("Drive Train", "drive_train", "Data", 80),
			("Voucher", "landed_cost_voucher_amount", "Currency", 90),
			("Sales Price", "sales_price", "Currency", 100),
			("Purchase Date", "posting_date", "Date", 100),
			("Supplier", "supplier", "Link/Supplier", 200),
			("Invoice", "name", "Link/Purchase Invoice", 100),
			("Salvage", "salvage_title", "Check", 70),
			("Odometer", "odometer_value", "Int", 90),
			("MK", "mk", "Data", 60),
			("Title Status", "title_status", "Data", 90),
			("Supplier Inv.", "name", "Data", 100),
			("Telephone", "s_phone", "data", 90),
		),
		"Sold Report":(
			("Status", "status", "data", 100),
			("Company", "company", "Data", 120),
			("S. Location", "location", "Data", 230),
			("Kijiji", "kijiji", "Check", 50),
			("Auto Trd", "auto_trd", "Check", 50),
			("Web", "web", "Check", 50),
			("Checklist", "checklist", "Data", 90),
			("Stock No.", "item_code", "Link/Item", 105),
			("Sold Date", "posting_date", "Date", 100),
			("Customer", "customer", "Link/Customer", 200),
			("Vim Number", "item_code", "Data", 160),
			("Model", "model", "Link/Model", 100),
			("Year", "year", "Int", 50),
			("Color", "exterior_color", "Data", 65),
			("Gear", "gear", "Data", 50),
			("Engine", "engine_size", "Data", 55),
			("Trim", "trim", "Data", 60),
			("Drive Train", "drive_train", "Data", 80),
			("Sales Price", "sales_price", "Currency", 100),
			("Sales Order", "sales_order", "Link/Sales Order", 100),
			("Sales Inv.", "sales_name", "Link/Sales Invoice", 100),
			("Purchase Inv.", "purchase_name", "Link/Purchase Invoice", 100),
			("Purchase Date", "purchase_date", "Date", 100),
			("Supplier", "supplier", "Link/Supplier", 100),
			("Odometer", "odometer_value", "Data", 90),
			("Telephone", "s_phone", "data", 90),
			("Title", "title_status", "data", 100),
			("BL", "bl", "data", 100),
			("Cost", "price", "Currency", 100),
			("Voucher", "landed_cost_voucher_amount", "Currency", 90),
			("Telephone", "c_phone", "data", 90),
		),
		"Sales Order To Be Billed":(
			("Status", "status", "Data", 100),
			("Company", "company", "Data", 120),
			("S. Location", "location", "Data", 230),
			("Stock No.", "item_code", "Link/Item", 105),
			("Order Date", "order_date", "Date", 100),
			("Customer", "customer", "Link/Customer", 150),
			("Vim Number", "vim_number", "Data", 160),
			("Model", "model", "Link/Model", 100),
			("Year", "year", "Int", 50),
			("Color", "exterior_color", "Data", 65),
			("Gear", "gear", "Data", 50),
			("Engine", "engine_size", "Data", 55),
			("Trim", "trim", "Data", 60),
			("Drive Train", "drive_train", "Data", 80),
			("Voucher", "landed_cost_voucher_amount", "Currency", 90),
			("Price", "price", "Currency", 100),
			("Order", "order_name", "Link/Sales Order", 100),
			("Order Status", "order_status", "Data", 90),
			("Odometer", "odometer_value", "Data", 90),
			("Salvage", "salvage_title", "Check", 70),
			("MK", "mk", "Data", 60),
			("Purchase Inv.", "purchase_name", "Link/Purchase Invoice", 110),
			("Purchase Date", "p_date", "Date", 100),
			("Supplier", "supplier", "Link/Supplier", 150),
			("S.Telephone", "s_phone", "data", 90),
			("Title Status", "title_status", "Data", 90),
			("Cost", "price", "Currency", 100),
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
		"All-1":  (
			("Item", "status"),
			("Item", "company"),
			("CONCAT(`tabItem`._default_supplier, ' - ', `tabAddress`.city, ', ', `tabAddress`.state) as location"),
			("Item", "kijiji_post"),
			("Item", "auto_trader_post"),
			("Item", "website_post"),
			("Item", "item_code"),
			("Item", "vim_number"),
			("Item", "model"),
			("Item", "year"),
			("Item", "exterior_color"),
			("CASE WHEN `tabItem`.gear = 'AUTOMATIC' THEN 'AT' WHEN `tabItem`.gear = 'MANUAL' THEN 'MT' END "),
			("Item", "engine_size"),
			("Item", "trim"),
			("Item", "drive_train"),
			("Purchase Invoice Item", "landed_cost_voucher_amount"),
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
			("Purchase Invoice", "posting_date"),
			("Purchase Invoice", "supplier"),
			("Purchase Invoice", "name"),
			("Item", "salvage_title"),
			("Item", "odometer_value"),
			("Item", "mk"),
			("Item", "title_status"),
			("Purchase Invoice", "bill_no"),
			("Supplier", "phone_number"),
		),
		"All-2": (
			("Item", "status"),
			("Item", "company"),
			("CONCAT(`tabItem`._default_supplier, ' - ', `tabAddress`.city, ', ', `tabAddress`.state) as location"),
			("Item", "kijiji_post"),
			("Item", "auto_trader_post"),
			("Item", "website_post"),
			("Item", "item_code"),
			("Item", "vim_number"),
			("Item", "model"),
			("Item", "year"),
			("Item", "exterior_color"),
			("CASE WHEN `tabItem`.gear = 'AUTOMATIC' THEN 'AT' WHEN `tabItem`.gear = 'MANUAL' THEN 'MT' END "),
			("Item", "engine_size"),
			("Item", "trim"),
			("Item", "drive_train"),
			("Purchase Invoice Item", "landed_cost_voucher_amount"),
			("Sales Invoice Item", "amount"),
			("Purchase Invoice", "posting_date"),
			("Purchase Invoice", "supplier"),
			("Purchase Invoice", "name"),
			("Item", "salvage_title"),
			("Item", "odometer_value"),
			("Item", "mk"),
			("Item", "title_status"),
			("Purchase Invoice", "bill_no"),
			("Supplier", "phone_number"),
		),
		"Stock Report":  (
			("Item", "status"),
			("Item", "company"),
			("CONCAT(`tabItem`._default_supplier, ' - ', `tabAddress`.city, ', ', `tabAddress`.state) as location"),
			("Item", "kijiji_post"),
			("Item", "auto_trader_post"),
			("Item", "website_post"),
			("Vehicle Release", "status"),
			("Item", "item_code"),
			("Item", "vim_number"),
			("Item", "model"),
			("Item", "year"),
			("Item", "exterior_color"),
			("CASE WHEN `tabItem`.gear = 'AUTOMATIC' THEN 'AT' WHEN `tabItem`.gear = 'MANUAL' THEN 'MT' END "),
			("Item", "engine_size"),
			("Item", "trim"),
			("Item", "drive_train"),
			("Purchase Invoice Item", "landed_cost_voucher_amount"),
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
			("Purchase Invoice", "posting_date"),
			# ("Bin", "valuation_rate"),
			("Purchase Invoice", "supplier"),
			("Purchase Invoice", "name"),
			("Item", "salvage_title"),
			("Item", "odometer_value"),
			("Item", "mk"),
			("Item", "title_status"),
			("Purchase Invoice", "bill_no"),
			("Supplier", "phone_number"),
			# ("Sales Price", "margin_amount"),
		),
		"Sold Report": (
			("Item", "status"),
			("Item", "company"),
			("CONCAT(`tabItem`._default_supplier, ' - ', `tabAddress`.city, ', ', `tabAddress`.state) as location"),
			("Item", "kijiji_post"),
			("Item", "auto_trader_post"),
			("Item", "website_post"),
			("Vehicle Release", "status"),
			("Item", "item_code"),
			("Sales Invoice", "posting_date"),
			("Sales Invoice", "customer"),
			("Item", "vim_number"),
			("Item", "model"),
			("Item", "year"),
			("Item", "exterior_color"),
			("CASE WHEN `tabItem`.gear = 'AUTOMATIC' THEN 'AT' WHEN `tabItem`.gear = 'MANUAL' THEN 'MT' END "),
			("Item", "engine_size"),
			("Item", "trim"),
			("Item", "drive_train"),
			("Sales Invoice Item", "amount"),
			# ("Sales Order", "billing_status"),
			("Sales Invoice Item", "sales_order"),
			("Sales Invoice", "name"),
			("Purchase Invoice", "name"),
			("Purchase Invoice", "posting_date"),
			("Purchase Invoice", "supplier"),
			("Item", "odometer_value"),
			("Supplier", "phone_number"),
			("Item", "title_status"),
			("Item", "bl"),
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
			("Purchase Invoice Item", "landed_cost_voucher_amount"),
			("Customer", "phone_number"),
		),
		"Sales Order To Be Billed":(
			("Item", "status"),
			("Item", "company"),
			("CONCAT(`tabItem`._default_supplier, ' - ', `tabAddress`.city, ', ', `tabAddress`.state) as location"),
			("Item", "item_code"),
			("Sales Order", "transaction_date"),
			("Sales Order", "customer"),
			("Item", "vim_number"),
			("Item", "model"),
			("Item", "year"),
			("Item", "exterior_color"),
			("CASE WHEN `tabItem`.gear = 'AUTOMATIC' THEN 'AT' WHEN `tabItem`.gear = 'MANUAL' THEN 'MT' END "),
			("Item", "engine_size"),
			("Item", "trim"),
			("Item", "drive_train"),
			("Purchase Invoice Item", "landed_cost_voucher_amount"),
			("Sales Order Item", "amount"),
			("Sales Order", "name"),
			("Sales Order", "status"),
			("Item", "odometer_value"),
			("Item", "salvage_title"),
			("Item", "mk"),
			("Purchase Invoice", "name"),
			("Purchase Invoice", "posting_date"),
			("Purchase Invoice", "supplier"),
			("Supplier", "phone_number"),
			("Item", "title_status"),
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
		)
	}

	fields = fields_obj.get(filters.get("report_type"))
	
	if not fields:
		return ""
	
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
