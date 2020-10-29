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
		("Company", "Data", 120),
		("S. Location", "Data", 230),
		("Stock No.", "Link/Item", 110),
		("Item Type", "Data", 100),
		("Vim Number", "Data", 150),
		("Details", "Data", 250),
		# ("Model", "Data", 100),
		# ("Year", "Data", 60),
		# ("Color", "Data", 70),
		("Due Date", "Date", 90),
		("Inv. Date", "Date", 90),
		("Customer", "Link/Customer", 130),
		("Sale N/Total", "Currency", 100),
		("GST", "Currency", 100),
		("PST", "Currency", 100),
		("Sale G/Total CAD", "Currency", 150),
		("Sale G/Total USD", "Currency", 150),
		("Pay Date", "Date", 90),
		("Payment Type", "Data", 100),
		("Breakdown", "Currency", 100),
		("Total Paid", "Currency", 100),
		("Outstanding", "Currency", 100),
		("Payment Entry", "Link/Payment Entry", 100),
		("Sales Inv.", "Link/Sales Invoice", 100),
		("G Price", "Currency", 100),
		("Checklist", "Data", 90),
		("VEH Status", "Data", 100),
		("Title Status", "Data", 100),
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
		{pinv_date}
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
		Group By 
			`tabSales Invoice`.name, `tabPayment Entry Reference`.name
 		Order By 
 			`tabSales Invoice`.name, `tabPayment Entry`.name

		""".format(
				fields=fields,
				sinv_date=sinv_date,
				pinv_date=pinv_date,
				conditions=conditions or "1 = 1"),
		filters, as_dict=True, debug=False)
	last_inv = ''
	vim = ''
	entry = ''
	pay_date = ''
	mode = ''
	for row in data:
		total_costs = flt(row.pinv_price) + flt(row.fee) + flt(row.transport) + \
			flt(row.delivery) + flt(row.parts) + flt(row.repair) + flt(row.others)
		vim_number = row.cont_vim.split('-')[0] if row.cont_vim and '-' in row.cont_vim else row.vim_number
		details = "-" 
		if row.invoice_type == "Vehicles":
			details = "{} {} {} {}".format(row.make, row.model, row.exterior_color, row.year)
		if row.cont_vim:
			details = row.cont_vim.split("-")[1]
		if row.invoice_type == "Parts":
			details = row.part_type
		
		if last_inv != row.sinv_name or vim_number != vim or entry != row.payment_entry:
			paid_arr = [flt(x.allocated_amount) for x in filter(lambda x, n=row.sinv_name : x.get('sinv_name') == n, data)]
			total_paid = sum(paid_arr) if paid_arr else .00
			results.append(
				(
					row.company,
					row.location,
					row.item_code,
					row.item_type,			#Item Type.
					vim_number,
					details,
					row.due_date if last_inv != row.sinv_name else '',
					row.sinv_date if last_inv != row.sinv_name else '',
					row.customer  if last_inv != row.sinv_name else '',
					row.net_total if last_inv != row.sinv_name else '',
					row.gst_total if last_inv != row.sinv_name else '',
					row.pst_total if last_inv != row.sinv_name else '',
					row.base_grand_total if last_inv != row.sinv_name else .00,
					row.grand_total if last_inv != row.sinv_name  and row.currency == "USD" else .00,
					row.p_posting_date if entry != row.payment_entry or mode != row.mode_of_payment or pay_date != row.p_posting_date else '-',
					row.mode_of_payment if entry != row.payment_entry or mode != row.mode_of_payment or pay_date != row.p_posting_date else ' ',
					row.allocated_amount if last_inv != row.sinv_name  or entry != row.payment_entry else .00,
					# flt(row.grand_total) - flt(row.outstanding_amount) if last_inv != row.sinv_name else .00, # Total Paid
					total_paid if last_inv != row.sinv_name else .00,
					row.outstanding_amount if last_inv != row.sinv_name else .00, 
					row.payment_entry,
					row.sinv_name if last_inv != row.sinv_name else '',
					row.gprice,
					row.checklist,
					row.status,
					row.title_status,
				)
			)
		else:
			results.append(
				(
					"", # Company
					"", # Location
					"", # Stock No.
					"", #Item Type
					"", # Vim Number
					"", # Details
					"", # Due Date
					"", # Inv Date
					"", # Customer 
					"", # Sale N/ Total
					"", # GST
					"", # PST
					row.p_posting_date, # Pay Date
					row.mode_of_payment, # Payment Type
					row.allocated_amount, # Breakdown
					"", # Total Paid
					"", # Outstanding
					row.payment_entry, # Payment Entry
					"", # Checklist
					"", # Sales Inv.
					"", #  GPrice
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
		("Item", "part_type"),
		("Item", "year"),
		("Item", "exterior_color"),
		("Vehicle Release", "status", "checklist"),
		("Sales Invoice Item", "vim_number", "cont_vim"),
		("Sales Invoice Item", "item_name"),
		("Sales Invoice", "due_date", "due_date"),
		("Sales Invoice", "posting_date", "sinv_date"),
		("Sales Invoice", "customer"),
		("Sales Invoice", "invoice_type"),
		("Sales Invoice", "net_total"),
		("""
			SUM(
				IF(
					`tabSales Taxes and Charges`.account_head != 'PST/QST receivable - 9.975%% - EZ',
					IFNULL(`tabSales Taxes and Charges`.tax_amount, 0), 0
				)
			) as gst_total
		"""
		),
		("""
			SUM(
				IF(
					`tabSales Taxes and Charges`.account_head = 'PST/QST receivable - 9.975%% - EZ',
					IFNULL(`tabSales Taxes and Charges`.tax_amount, 0), 0
				)
			) as pst_total
		"""
		),
		("Sales Invoice", "currency"),
		("Sales Invoice", "base_grand_total"),
		("Sales Invoice", "grand_total"),
		("Payment Entry", "posting_date", "p_posting_date"),
		("Payment Entry", "mode_of_payment"),
		("Payment Entry Reference", "allocated_amount"),
		("Sales Invoice", "outstanding_amount"),
		("Payment Entry Reference", "parent", "payment_entry"),
		("Sales Invoice", "name", "sinv_name"),
		("Sales Invoice Item", "gprice"),
		("Item", "status"),
		("Item", "title_status"),
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
