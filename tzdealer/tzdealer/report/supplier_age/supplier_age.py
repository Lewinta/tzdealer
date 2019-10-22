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
			inv.item_code,
			inv.name,
			inv.posting_date,
			inv.supplier,
			inv.base_grand_total,
			inv.paid_amount,
			inv.outstanding_amount,
			inv.landed_cost_voucher_amount
		]

		data.append(row)

	return columns, data

def get_columns(invoice_list):
	"""return columns based on filters"""
	columns = [
		_("Item") 			+ ":Data:350",
		_("Vim Number") 		+ ":Data:150",
		_("Invoice") 			+ ":Link/Purchase Invoice:120",
		_("Posting Date") 		+ ":Date:80",
		_("Supplier") 			+ ":Link/Supplier:120",
		_("Grand Total") 		+ ":Currency/currency:120",
		_("Paid Amount") 		+ ":Currency/currency:120",
		_("Outstanding Amount") + ":Currency/currency:120",
		_("Voucher") 			+ ":Currency/currency:120",
	]

	return columns

def get_conditions(filters):
	company = frappe.get_value("User Permission", {
		"user":frappe.session.user,
		"allow":"Company",
	}, "for_value")

	conditions = "`tabPurchase Invoice`.company = '{}'".format(company)

	# if filters.get("company"):
		# conditions += " and company = %(company)s"
	if filters.get("supplier"):
		conditions += " and `tabPurchase Invoice`.supplier = %(supplier)s"
	if filters.get("from_date"):
		conditions += " and `tabPurchase Invoice`.posting_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " and `tabPurchase Invoice`.posting_date <= %(to_date)s"
	if filters.get("item_code"):
		conditions += " and `tabPurchase Invoice Item`.item_code = %(item_code)s"
	if filters.get("unpaid") == 1:
		conditions += " and `tabPurchase Invoice`.outstanding_amount > 0"
	
	conditions += " ORDER BY `tabPurchase Invoice`.posting_date DESC, `tabPurchase Invoice`.name DESC"
	
	if filters.get("limit"):
		conditions += " LIMIT %(limit)s"
	
	frappe.errprint(conditions)
	return conditions

def get_invoices(filters):

	conditions = get_conditions(filters)

	return frappe.db.sql("""
		SELECT 
			CONCAT(`tabItem`.item_code,':',`tabItem`.item_name) as item,
			`tabPurchase Invoice Item`.item_code,
			`tabPurchase Invoice`.name,
			`tabPurchase Invoice`.posting_date,
			`tabPurchase Invoice`.supplier,
			`tabPurchase Invoice`.base_grand_total,
			(
				SELECT 
					SUM(allocated_amount) 
				FROM
					`tabPayment Entry Reference` 
				WHERE 
					reference_name = `tabPurchase Invoice`.name
				AND
					docstatus = 1
			) as paid_amount,
			`tabPurchase Invoice`.outstanding_amount,
			`tabPurchase Invoice Item`.landed_cost_voucher_amount
			
			FROM 
				`tabPurchase Invoice`
			JOIN
				`tabPurchase Invoice Item`
			ON
				`tabPurchase Invoice`.name = `tabPurchase Invoice Item`.parent
			JOIN
				`tabItem`
			ON
				`tabItem`.item_code = `tabPurchase Invoice Item`.item_code
			AND
				`tabPurchase Invoice Item`.idx = 1
		WHERE 
			`tabPurchase Invoice`.docstatus = 1 and %s  
		

	""" % conditions, filters, debug=True, as_dict=True)