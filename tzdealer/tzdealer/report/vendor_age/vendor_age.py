# Copyright (c) 2013, TZCODE SRL and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
from frappe import msgprint, _

def execute(filters=None):

	if not filters: filters = {}

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
			inv.supplier,
			inv.bill_no,
			inv.bill_date,
			inv.base_grand_total,
			inv.paid_amount,
			inv.outstanding_amount
		]

		data.append(row)

	return columns, data


def get_columns(invoice_list):
	"""return columns based on filters"""
	columns = [
		_("Item") + ":Data:350",
		_("Invoice") + ":Link/Purchase Invoice:120",
		_("Posting Date") + ":Date:80",
		_("Vendor") + ":Link/Supplier:120",
		_("Bill No") + "::120",
		_("Bill Date") + ":Date:80",
		_("Grand Total") + ":Currency/currency:120",
		_("Paid Amount") + ":Currency/currency:120",
		_("Outstanding Amount") + ":Currency/currency:120"
	]

	return columns

def get_conditions(filters):
	conditions = ""

	if filters.get("company"):
		conditions += " and company = %(company)s"
	if filters.get("supplier"):
		conditions += " and supplier = %(supplier)s"
	if filters.get("from_date"):
		conditions += " and posting_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " and posting_date <= %(to_date)s"
	if filters.get("mode_of_payment"):
		conditions += " and ifnull(mode_of_payment, '') = %(mode_of_payment)s"

	return conditions

def get_invoices(filters):

	conditions = get_conditions(filters)
	
	return frappe.db.sql("""
		SELECT
			(
				SELECT 
					CONCAT(`tabItem`.item_code,':',`tabItem`.item_name) as item
				FROM 
					`tabPurchase Invoice Item`
				JOIN
					`tabItem`
				ON
					`tabPurchase Invoice Item`.item_code = `tabItem`.item_code
				AND
					`tabPurchase Invoice Item`.idx = 1
				WHERE 
					`tabPurchase Invoice Item`.parent = `tabPurchase Invoice`.name
				LIMIT 
					1 

			) as item,
			`tabPurchase Invoice`.name,
			`tabPurchase Invoice`.posting_date,
			`tabPurchase Invoice`.supplier,
			`tabPurchase Invoice`.bill_no,
			`tabPurchase Invoice`.bill_date,
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
			) AS paid_amount,
			`tabPurchase Invoice`.outstanding_amount
		FROM 
			`tabPurchase Invoice`
		WHERE
			`tabPurchase Invoice`.docstatus = 1 %s
		ORDER BY 
			`tabPurchase Invoice`.posting_date DESC,
			`tabPurchase Invoice`.name DESC

	""" % conditions, filters, as_dict=1)


