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
		("ID", "Link/Item", 325),
		("Vim Number", "Link/Item", 150),
		# ("Model", "Data", 100),
		# ("Year", "Data", 60),
		# ("Color", "Data", 70),
		("Inv. Date", "Date", 90),
		("Customer", "Link/Customer", 130),
		("Sale G/Total", "Currency", 100),
		("Pay Date", "Date", 90),
		("Payment Type", "Data", 100),
		("Breakdown", "Currency", 100),
		("Total Paid", "Currency", 100),
		("Outstanding", "Currency", 100),
		("Payment Entry", "Link/Payment Entry", 100),
		("Sales Inv.", "Link/Sales Invoice", 100),
	)

	formatted_columns = []
	
	for label, fieldtype, width in columns:
		formatted_columns.append(
			get_formatted_column(label, fieldtype, width)
		)

	return formatted_columns

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


	if filters.get('from_date'):
		conditions.append(
			("Sales Invoice", "posting_date", ">=", filters.get('from_date'))
		)

	if filters.get('to_date'):
		conditions.append(
			("Sales Invoice", "posting_date", "<=", filters.get('to_date'))
		)

	if filters.get('customer'):
		conditions.append(
			("Sales Invoice", "customer", "=", filters.get('customer'))
		)

	if filters.get('unpaid'):
		conditions.append(
			("Sales Invoice", "outstanding_amount", ">", 0)
		)

	if filters.get('item_code'):
		conditions.append(
			("Sales Invoice Item", "item_code", "=", filters.get('item_code'))
		)

	sql_conditions = []

	if not conditions:
		return sql_conditions
	
	for doctype, fieldname, compare, value in conditions:

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
		("Sales Invoice Item", "item_code"),
		("IF(ISNULL(`tabSales Invoice Item`.vim_number), `tabSales Invoice Item`.item_code, `tabSales Invoice Item`.vim_number) as vim_number"),
		("Sales Invoice Item", "item_name"),
		("Sales Invoice", "posting_date", "sinv_date"),
		("Sales Invoice", "customer"),
		("Sales Invoice", "grand_total"),
		("Payment Entry", "posting_date", "p_posting_date"),
		("Payment Entry", "mode_of_payment"),
		("Payment Entry Reference", "allocated_amount"),
		("Sales Invoice", "outstanding_amount"),
		("Payment Entry Reference", "parent", "payment_entry"),
		("Sales Invoice", "name", "sinv_name"),
	)
		
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

def get_data(filters):
	"""
	Return the data that needs to be rendered
	"""
	fields = get_fields(filters)
	conditions = get_conditions(filters)
	results = []
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
		Left Join
			`tabPayment Entry Reference`
			On
			`tabPayment Entry Reference`.reference_name = `tabSales Invoice`.name
			And
				`tabPayment Entry Reference`.docstatus = 1

		Left	 Join
			`tabPayment Entry`
			On
			`tabPayment Entry Reference`.parent = `tabPayment Entry`.name
			And 
			`tabPayment Entry`.docstatus = 1

		Where
			{conditions}
		Order By `tabSales Invoice`.name, `tabPayment Entry`.name
		""".format(fields=fields, conditions=conditions or "1 = 1"),
	filters, as_dict=True, debug=True)
	last_inv = ''
	vim = ''
	entry = ''
	pay_date = ''
	mode = ''
	for row in data:
		total_costs = flt(row.pinv_price) + flt(row.fee) + flt(row.transport) + \
			flt(row.delivery) + flt(row.parts) + flt(row.repair) + flt(row.others)
		vim_number = row.vim_number.split('-')[0] if row.vim_number and '-' in row.vim_number else row.vim_number
		
		if last_inv != row.sinv_name or vim_number != vim or entry != row.payment_entry:
			results.append(
				(
					"{}:{}".format(row.item_code, row.item_name) ,
					vim_number ,
					row.sinv_date,
					row.customer ,
					row.grand_total if last_inv != row.sinv_name else .00,
					row.p_posting_date if entry != row.payment_entry or mode != row.mode_of_payment or pay_date != row.p_posting_date else '-',
					row.mode_of_payment if entry != row.payment_entry or mode != row.mode_of_payment or pay_date != row.p_posting_date else ' ',
					row.allocated_amount if last_inv != row.sinv_name  or entry != row.payment_entry else .00,
					flt(row.grand_total) - flt(row.outstanding_amount) if last_inv != row.sinv_name else .00,
					row.outstanding_amount if last_inv != row.sinv_name else .00,
					row.payment_entry,
					row.sinv_name,
				)
			)
		else:
			results.append(
				(
					# "",
					# "",
					# "",
					"",
					"",
					"",
					"",
					"",
					row.p_posting_date,
					row.mode_of_payment,
					row.allocated_amount,
					"",
					"",
					row.payment_entry,
					"",
				)
			)
		last_inv = row.sinv_name
		vim = vim_number
		entry = row.payment_entry
		pay_date = row.p_posting_date
		mode = row.mode_of_payment
	return results
