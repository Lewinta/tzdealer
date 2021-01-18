# Copyright (c) 2013, TZCODE SRL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cstr, flt

mop_1 = frappe.get_list("Mode of Payment", as_list=True, limit=5)[0][0]
mop_2 = frappe.get_list("Mode of Payment", as_list=True, limit=5)[1][0]
mop_3 = frappe.get_list("Mode of Payment", as_list=True, limit=5)[2][0]
mop_4 = frappe.get_list("Mode of Payment", as_list=True, limit=5)[3][0]
mop_5 = frappe.get_list("Mode of Payment", as_list=True, limit=5)[4][0]

def execute(filters=None):
	return get_columns(), get_data(filters)

def get_columns():
	columns = (
		("Company", "Data", 120),
		("S. Location", "Data", 180),
		("Stock No.", "Link/Item", 110),
		("Item Type", "Data", 90),
		("Vim Number", "Data", 150),
		("Details", "Data", 180),
		# ("Due Date", "Date", 90),
		# ("Inv. Date", "Date", 90),
		("Customer", "Link/Customer", 160),
		("Net Sale", "Currency", 90),
		("GST", "Currency", 90),
		("PST", "Currency", 90),
		("NET Cost G", "Currency", 90),
		("G Price", "Currency", 90),
		("Total Sale", "Currency", 90),
		# ("Total Sale USD", "Currency", 110),
		# (mop_1, "Currency", len(mop_1) * 8),
		# ("CASH CAD", "Currency", len("CASH CAD") * 10),
		# (mop_2, "Currency", len(mop_2) * 9),
		# (mop_3, "Currency", len(mop_3) * 9),
		# (mop_5, "Currency", len(mop_5) * 9),
		("Total CASH", "Currency", 90),
		("Total BANK", "Currency", 100),
		("Total Paid", "Currency", 100),
		("Outstanding", "Currency", 100),
		("Sales Inv.", "Link/Sales Invoice", 100),
		("Checklist", "Data", 90),
		# ("VEH Status", "Data", 100),
		# ("Title Status", "Data", 100),
		# ("G GST", "Currency", 100),
		# ("G PST", "Currency", 100),
		# ("Total", "Currency", 100),
		("CASH OVER/SHORT", "Currency", 120),
	)

	formatted_columns = []
	
	for label, fieldtype, width in columns:
		formatted_columns.append(
			get_formatted_column(label, fieldtype, width)
		)

	return formatted_columns

def get_data(filters):
	"""
	Return the data that needs to be rendered
	"""
	fields = get_fields(filters)
	conditions = get_conditions(filters)
	results = []
	pinv_date = " "
	sinv_date = " "

	if filters.get('from_date'):
		sinv_date = sinv_date + " AND `tabSales Invoice`.posting_date >= '{}' ".format(filters.get('from_date'))
		pinv_date = pinv_date + " AND `tabPayment Entry`.posting_date >= '{}' ".format(filters.get('from_date'))

	if filters.get('to_date'):
		sinv_date = sinv_date + " AND `tabSales Invoice`.posting_date <= '{}' ".format(filters.get('to_date'))
		pinv_date = pinv_date + " AND `tabPayment Entry`.posting_date <= '{}' ".format(filters.get('to_date'))


	data =  frappe.db.sql("""
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

		{sinv_date}
		Inner Join
			`tabItem`
		On
			`tabSales Invoice Item`.item_code = `tabItem`.item_code

		Left Join
			`tabSales Taxes and Charges`
		On  
			`tabSales Invoice`.name = `tabSales Taxes and Charges`.parent

		Left Join
			`tabPayment Entry Reference`
		On
			`tabPayment Entry Reference`.reference_name = `tabSales Invoice`.name
		And
			`tabPayment Entry Reference`.docstatus = 1
		Left Join
			`tabPayment Entry`
		On
			`tabPayment Entry Reference`.parent = `tabPayment Entry`.name
		And 
			`tabPayment Entry`.docstatus = 1
		Left Join 
			`tabAccount`
		On	
			`tabPayment Entry`.paid_to = `tabAccount`.name

		{pinv_date}
		Left Join
			`tabAddress`
		On
			`tabItem`.location = `tabAddress`.name
		Left Join
			`tabDelivery Checklist`
		On
			`tabDelivery Checklist`.name = `tabItem`.name	
		Where
			{conditions}
		Group By 
			`tabSales Invoice`.name
 		Order By 
 			`tabSales Invoice`.name

		""".format(
				fields=fields,
				sinv_date=sinv_date,
				pinv_date=pinv_date,
				conditions=conditions or "1 = 1"),
		filters, as_dict=True, debug=False)
	
	last_inv = vim = entry = pay_date = mode = ''
	
	for row in data:
		total_costs = flt(row.pinv_price) + flt(row.fee) + flt(row.transport) + \
			flt(row.delivery) + flt(row.parts) + flt(row.repair) + flt(row.others)
		vim_number = row.cont_vim.split('-')[0] if row.cont_vim and '-' in row.cont_vim else row.vim_number

		details = "-" 
		if row.item_type == "Vehicles":
			details = "{} {} {} {}".format(row.make or "", row.model or "", row.exterior_color or "", row.year or "")
		if row.item_type == "Containers":
			details = "{} {}".format(row.booking_no or "", row.container_no or "")
		if row.item_type == "Parts":
			details = row.part_type
		if row.item_type == "Services":
			details = row.item_type

		
		paid_arr = [flt(x.allocated_amount) for x in filter(lambda x, n=row.sinv_name : x.get('sinv_name') == n, data)]
		total_paid = sum(paid_arr) if paid_arr else .00
		g_total = flt(row.gprice) + flt(row.g_gst_total) + flt(row.g_pst_total)
		total_received = row.base_grand_total  - row.outstanding_amount
		results.append(
			(
				row.company, 			#Company
				row.location,			#S.Location
				row.item_code,			#Stock No.
				row.item_type,			#Item Type.
				vim_number,				#Vim Number
				details,				#Details
				# row.due_date if last_inv != row.sinv_name else '', 		#Due Date
				# row.sinv_date if last_inv != row.sinv_name else '',		#Inv Date
				row.customer  if last_inv != row.sinv_name else '',		#Customer
				row.net_total if last_inv != row.sinv_name else '',		#Net Sale
				row.gst_total,											#GST
				row.pst_total ,											#PST
				row.net_cost,			#Net Cost
				row.gprice,				#G Price
				row.base_grand_total if last_inv != row.sinv_name else .00, 	#Total Sale 
				# row.grand_total if last_inv != row.sinv_name  and row.currency == "USD" else .00, 		#Total Sale USD
				# row.mop_1 if last_inv != row.sinv_name  or entry != row.payment_entry else .00,			#MOP1	
				# row.mop_4 if last_inv != row.sinv_name  or entry != row.payment_entry else .00,			#MOP4
				# row.mop_2 if last_inv != row.sinv_name  or entry != row.payment_entry else .00,			#MOP2
				# row.mop_3 if last_inv != row.sinv_name  or entry != row.payment_entry else .00,			#MOP3
				# row.mop_5 if last_inv != row.sinv_name  or entry != row.payment_entry else .00,			#MOP5
				row.cash_paid,																							#Total CASH Paid
				row.bank_paid,																							#Total BANK Paid
				total_received,																			#Total Paid
				row.outstanding_amount if last_inv != row.sinv_name else .00, 							#Outstanding
				row.sinv_name if last_inv != row.sinv_name else '',										#Sales Inv.
				row.vehicle_release,	#VEH Status
				# row.status,				#VEH Status
				# row.title_status,		#Title Status
				# row.g_gst_total,		#G_GST
				# row.g_pst_total,		#G_PST
				# g_total,				#Total
				g_total - total_received if row.outstanding_amount == .00 and g_total else .000,		#CashOver
			)
		)
		
		last_inv = row.sinv_name
		vim = vim_number
		entry = row.payment_entry
		pay_date = row.p_posting_date
		mode = row.mode_of_payment
	return results

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

	if filters.get('company'):
		conditions.append(
			("Sales Invoice", "company", "=", filters.get('company'))
		)
	
	if filters.get('customer'):
		conditions.append(
			("Sales Invoice", "customer", "=", filters.get('customer'))
		)

	if filters.get('payment_status') == "Unpaid Only":
		conditions.append(
			("Sales Invoice", "outstanding_amount", ">", 0)
		)

	if filters.get('payment_status') == "Paid Only":
		conditions.append(
			("Sales Invoice", "outstanding_amount", "=", 0)
		)
	if filters.get('item_code'):
		conditions.append(
			("Sales Invoice Item", "item_code", "=", filters.get('item_code'))
		)
	sql_conditions = []

	if not conditions:
		return sql_conditions
	
	for doctype, fieldname, compare, value in conditions:
		if fieldname == '-':
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
		("Sales Invoice", "company"),
		("CONCAT(`tabItem`._default_supplier, ' - ', `tabAddress`.city, ', ', `tabAddress`.state) as location"),
		("Sales Invoice Item", "item_code"),
		("Item", "vim_number"),
		("Item", "make"),
		("Item", "model"),
		("Item", "item_type"),
		("Item", "booking_no"),
		("Item", "container_no"),
		("Item", "part_type"),
		("Item", "year"),
		("Item", "exterior_color"),
		("Delivery Checklist", "status", "vehicle_release"),
		("Sales Invoice Item", "vim_number", "cont_vim"),
		("Sales Invoice Item", "item_name"),
		# ("Sales Invoice", "due_date", "due_date"),
		# ("Sales Invoice", "posting_date", "sinv_date"),
		("Sales Invoice", "customer"),
		("Sales Invoice", "invoice_type"),
		("Sales Invoice", "net_total"),
		("""(SELECT SUM(IFNULL(tax_amount, 0)) FROM `tabSales Taxes and Charges` WHERE tax_type = 'GST' AND parent = `tabSales Invoice`.name AND docstatus = 1 ) as gst_total"""),
		("""(SELECT SUM(IFNULL(tax_amount, 0)) FROM `tabSales Taxes and Charges` WHERE tax_type = 'PST' AND parent = `tabSales Invoice`.name AND docstatus = 1 ) as pst_total"""),
		("""(SELECT SUM(IFNULL(g_tax, 0)) FROM `tabSales Taxes and Charges` WHERE tax_type = 'GST' AND parent = `tabSales Invoice`.name AND docstatus = 1 ) as g_gst_total"""), 
		("Sales Invoice", "currency"),
		("Sales Invoice", "base_grand_total"),
		("Sales Invoice", "grand_total"),
		("Payment Entry", "posting_date", "p_posting_date"),
		("Payment Entry", "mode_of_payment"),
		("""
			SUM(
				IF(
					`tabAccount`.account_type = 'Cash',
					IFNULL(`tabPayment Entry Reference`.allocated_amount, 0), 0
				)
			) as cash_paid,
			SUM(
				IF(
					`tabAccount`.account_type = 'Bank',
					IFNULL(`tabPayment Entry Reference`.allocated_amount, 0), 0
				)
			) as bank_paid
		"""
		),
		("Sales Invoice", "outstanding_amount"),
		("Payment Entry Reference", "parent", "payment_entry"),
		("Sales Invoice", "name", "sinv_name"),
		("Sales Invoice Item", "gprice"),
		("Item", "status"),
		("Item", "title_status"),
		("(SELECT `view_vehicle_g_cost`.purchase_cost + view_vehicle_g_cost.lcv from `view_vehicle_g_cost` where `view_vehicle_g_cost`.item_code = `tabItem`.item_code) as net_cost")
	)

	sql_fields = []

	for args in fields:
		sql_field = get_field(args)

		sql_fields.append(sql_field)
	# frappe.errprint(", ".join(sql_fields))
	return ", ".join(sql_fields)

def get_field(args):

	if len(args) == 2:
		doctype, fieldname = args
		alias = fieldname
	elif len(args) == 3:
		doctype, fieldname, alias = args
	else:
		return args

	sql_field = "`tab{doctype}`.`{fieldname}` as {alias}" \
		.format(doctype=doctype, fieldname=fieldname, alias=alias)

	return sql_field
