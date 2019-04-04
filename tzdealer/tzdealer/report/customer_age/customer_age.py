# Copyright (c) 2013, TZCODE SRL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _

def execute(filters=None):

	invoice_list = get_invoices(filters)
	columns = get_columns(invoice_list)

	if not invoice_list:
		msgprint(_("No record found"))
		return columns, invoice_list

	data = []
	for inv in invoice_list:
		# invoice details

		row = [
			inv.name,
			inv.posting_date,
			inv.customer,
			inv.base_grand_total,
			inv.paid_amount,
			inv.outstanding_amount
		]

		data.append(row)

	return columns, data

def get_columns(invoice_list):
	"""return columns based on filters"""
	columns = [
		_("Invoice") 			+ ":Link/Sales Invoice:120",
		_("Posting Date") 		+ ":Date:80",
		_("Customer") 			+ ":Link/Customer:120",
		_("Grand Total") 		+ ":Currency/currency:120",
		_("Paid Amount") 		+ ":Currency/currency:120",
		_("Outstanding Amount") + ":Currency/currency:120"
	]

	return columns

def get_conditions(filters):
	conditions = ""

	if filters.get("company"):
		conditions += " and company  = %(company)s"
	if filters.get("customer"):
		conditions += " and customer = %(customer)s"
	if filters.get("from_date"):
		conditions += " and posting_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " and posting_date <= %(to_date)s"

	return conditions

def get_invoices(filters):

	conditions = get_conditions(filters)

	return frappe.db.sql("""
		SELECT 
			`tabSales Invoice`.name,
			`tabSales Invoice`.posting_date,
			`tabSales Invoice`.customer,
			`tabSales Invoice`.owner,
			`tabSales Invoice`.base_net_total,
			`tabSales Invoice`.base_grand_total,
			`tabSales Invoice`.outstanding_amount,
			(
				SELECT 
					SUM(allocated_amount) 
				FROM
					`tabPayment Entry Reference` 
				WHERE 
					reference_name = `tabSales Invoice`.name
				AND
					docstatus = 1
			) as paid_amount
			
			FROM 
				`tabSales Invoice`
		WHERE 
			docstatus = 1 %s 
		ORDER BY 
			posting_date DESC, name DESC

	""" % conditions, filters, debug=True, as_dict=1)

