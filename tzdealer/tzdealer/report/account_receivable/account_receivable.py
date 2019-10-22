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
			inv.item,
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
		_("Item") 			+ ":Data:350",
		_("Invoice") 			+ ":Link/Sales Invoice:120",
		_("Posting Date") 		+ ":Date:80",
		_("Customer") 			+ ":Link/Customer:120",
		_("Grand Total") 		+ ":Currency/currency:120",
		_("Paid Amount") 		+ ":Currency/currency:120",
		_("Outstanding Amount") + ":Currency/currency:120"
	]

	return columns

def get_conditions(filters):
	company = frappe.get_value("User Permission", {
		"user":frappe.session.user,
		"allow":"Company",
	}, "for_value")

	conditions = "`tabSales Invoice`.company = '{}'".format(company)

	# if filters.get("company"):
		# conditions += " and company = %(company)s"
	if filters.get("customer"):
		conditions += " and `tabSales Invoice`.customer = %(customer)s"
	if filters.get("from_date"):
		conditions += " and `tabSales Invoice`.posting_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " and `tabSales Invoice`.posting_date <= %(to_date)s"
	if filters.get("unpaid"):
		conditions += " and `tabSales Invoice`.outstanding_amount > 0"

	return conditions

def get_invoices(filters):

	conditions = get_conditions(filters)

	return frappe.db.sql("""
		SELECT 
			(
				SELECT 
					CONCAT(`tabItem`.item_code,':',`tabItem`.item_name) as item
				FROM 
					`tabSales Invoice Item`
				JOIN
					`tabItem`
				ON
					`tabSales Invoice Item`.item_code = `tabItem`.item_code
				AND
					`tabSales Invoice Item`.idx = 1
				WHERE 
					`tabSales Invoice Item`.parent = `tabSales Invoice`.name
				LIMIT 
					1 

			) as item,
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
			`tabSales Invoice`.docstatus = 1 and %s 
		ORDER BY 
			`tabSales Invoice`.posting_date DESC, `tabSales Invoice`.name DESC

	""" % conditions, filters, debug=True, as_dict=True)

