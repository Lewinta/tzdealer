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
			inv.total,
			inv.gst_total,
			inv.pst_total,
			inv.grand_total,
			inv.paid_amount,
			inv.outstanding_amount,
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
		_("Net Total") 			+ ":Currency/currency:120",
		_("GST") 				+ ":Currency/currency:100",
		_("PST") 				+ ":Currency/currency:100",
		_("Grand Total") 		+ ":Currency/currency:120",
		_("Paid Amount") 		+ ":Currency/currency:120",
		_("Outstanding Amount") + ":Currency/currency:120",
	]

	return columns

def get_conditions(filters):
	company = frappe.get_value("User Permission", {
		"user":frappe.session.user,
		"allow":"Company",
	}, "for_value")

	conditions = " `tabPurchase Invoice`.company = '{}'".format(company)

	# if filters.get("company"):
		# conditions += " and company = %(company)s"
	if filters.get("supplier"):
		conditions += " and `tabPurchase Invoice`.supplier  = '{}'".format(filters.get("supplier"))
	if filters.get("from_date"):
		conditions += " and `tabPurchase Invoice`.posting_date >= '{}'".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and `tabPurchase Invoice`.posting_date <= '{}'".format(filters.get("to_date"))
	if filters.get("item_code"):
		conditions += " and `tabItem`.item_code = '{}'".format(filters.get("item_code"))
	if filters.get("unpaid") == 1:
		conditions += " and outstanding_amount > 0"
	
	conditions += " ORDER BY `tabItem`.item_code, `tabPurchase Invoice`.posting_date ASC, `tabPurchase Invoice`.name ASC"
	
	# if filters.get("limit"):
	# 	conditions += " LIMIT {}".format(filters.get("limit"))
	
	frappe.errprint(conditions)
	return conditions

def get_invoices(filters):

	conditions = get_conditions(filters)

	return frappe.db.sql("""
		SELECT 
			* 
		FROM (
				SELECT 
				CONCAT(`tabItem`.item_code,':',`tabItem`.item_name) as item,
				`tabPurchase Invoice Item`.item_code,
				`tabPurchase Invoice`.name,
				`tabPurchase Invoice`.posting_date,
				`tabPurchase Invoice`.supplier,
				`tabPurchase Invoice`.total,
				SUM(
					IF(
						`tabPurchase Taxes and Charges`.account_head = 'GST to pay - EZ',
							IFNULL(`tabPurchase Taxes and Charges`.tax_amount, 0),
							0
						)
					) as gst_total,
				SUM(
					IF(
						`tabPurchase Taxes and Charges`.account_head = 'PST/QST to pay - 9.975 - EZ',
							IFNULL(`tabPurchase Taxes and Charges`.tax_amount, 0),
							0
						)
					) as pst_total,
				`tabPurchase Invoice`.grand_total,
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
				`tabPurchase Invoice`.company
				
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
				JOIN
					`tabPurchase Taxes and Charges`
				ON
					`tabPurchase Invoice`.name = `tabPurchase Taxes and Charges`.parent
					WHERE 
		 		{conditions}  
		) as A
		UNION 
		SELECT 
			* 
		FROM 
			(
				SELECT 
		CONCAT(`tabItem`.item_code,':',`tabItem`.item_name) as item,
	`tabLanded Cost Item`.item_code,
	`tabLanded Cost Taxes and Charges`.invoice as name,
	`tabPurchase Invoice`.posting_date,
	`tabPurchase Invoice`.supplier,
	`tabPurchase Invoice`.total,
	t_c.gst_total,
	t_c.pst_total,
	`tabPurchase Invoice`.grand_total,
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
	`tabPurchase Invoice`.company
From 
	`tabLanded Cost Taxes and Charges`
Join
	`tabLanded Cost Purchase Receipt`
On
	`tabLanded Cost Purchase Receipt`.parent = `tabLanded Cost Taxes and Charges`.parent
And
	`tabLanded Cost Purchase Receipt`.docstatus = `tabLanded Cost Taxes and Charges`.docstatus
And
	`tabLanded Cost Taxes and Charges`.docstatus = 1
And
	`tabLanded Cost Taxes and Charges`.create_invoice = 1
Join
	`tabLanded Cost Item`
On
	`tabLanded Cost Item`.parent = `tabLanded Cost Purchase Receipt`.parent
And
	`tabLanded Cost Purchase Receipt`.docstatus = `tabLanded Cost Item`.docstatus
And
	`tabLanded Cost Item`.docstatus = 1
Join
	`tabItem`
On
	`tabItem`.item_code = `tabLanded Cost Item`.item_code
Join
	`tabPurchase Invoice`
On
	`tabPurchase Invoice`.name = `tabLanded Cost Taxes and Charges`.invoice	
Join
	(
		Select
			`tabPurchase Invoice`.name,
			`tabPurchase Taxes and Charges`.account_head,
				SUM(
					IF(
						`tabPurchase Taxes and Charges`.account_head = 'GST to pay - EZ',
						`tabPurchase Taxes and Charges`.tax_amount,
						0
					)
				) as gst_total,
				SUM(
					IF(
						`tabPurchase Taxes and Charges`.account_head = 'PST/QST to pay - 9.975 - EZ',
						`tabPurchase Taxes and Charges`.tax_amount,
						0
					)
				) as pst_total
		From
			`tabPurchase Invoice`
		Join
			`tabPurchase Taxes and Charges`
		On
			`tabPurchase Invoice`.name = `tabPurchase Taxes and Charges`.parent
		And
			`tabPurchase Invoice`.docstatus = 1
		Group By 
			`tabPurchase Invoice`.name
	) as t_c
On
	`tabLanded Cost Taxes and Charges`.invoice = t_c.name
		WHERE 
		{conditions}  
			) as b
	Order By item_code, name ASC

		

	""".format(conditions=conditions or "1 = 1"), debug=False, as_dict=True)