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
	last_vim = ''
	last_inv = ''

	for inv in invoice_list:
		# invoice details
		if last_inv != inv.name or last_vim != inv.item_code:
			row = [
				inv.due_date,
				inv.posting_date,
				inv.supplier,
				inv.item_code,
				inv.vim_number,
				inv.invoice_type,
				inv.total,
				inv.gst_total,
				inv.pst_total,
				inv.grand_total,
				inv.trans_type,
				inv.name,
				inv.breakdown,
				inv.paid_amount,
				inv.outstanding_amount,
				inv.pinv,
			]
		else:
			row = [
				"",
				"",
				inv.supplier,
				"",
				"",
				inv.invoice_type,
				.000,
				.000,
				.000,
				.000,
				inv.trans_type,
				inv.name,
				inv.breakdown,
				.000,
				inv.outstanding_amount,
				inv.pinv,
			]		
		last_inv = inv.name
		last_vim = inv.item_code
		data.append(row)

	return columns, data

def get_columns(invoice_list):
	"""return columns based on filters"""
	columns = [
		_("Due Date") 			+ ":Date:80",
		_("Date") 				+ ":Date:80",
		_("Supplier") 			+ ":Link/Supplier:180",
		_("Item") 				+ ":Link/Item:105",
		_("Vim Number") 		+ ":Data:150",
		_("Invoice Type") 		+ ":Link/Purchase Invoice:90",
		_("Net Total") 			+ ":Currency/currency:120",
		_("GST") 				+ ":Currency/currency:100",
		_("PST") 				+ ":Currency/currency:100",
		_("Grand Total") 		+ ":Currency/currency:120",
		_("Trs. Type") 			+ ":Data:80",
		_("Invoice") 			+ ":Link/Purchase Invoice:120",
		_("Breakdown") 			+ ":Currency/currency:120",
		_("Paid Amount") 		+ ":Currency/currency:120",
		_("Outstanding Amount") + ":Currency/currency:120",
		_("Payment") 			+ ":Link/Payment Entry:90",
	]

	return columns

def get_conditions(filters):
	# company = frappe.get_value("User Permission", {
	# 	"user":frappe.session.user,
	# 	"allow":"Company",
	# }, "for_value")

	conditions = " `viewPurchase Invoice`.company = '{}'".format(filters.get("company"))
	# conditions += " and IFNULL(`tabPayment Entry Reference`.allocated_amount, 0) >= 0"

	# if filters.get("company"):
		# conditions += " and company = %(company)s"
	if filters.get("supplier"):
		conditions += " and `viewPurchase Invoice`.supplier  = '{}'".format(filters.get("supplier"))
	if filters.get("from_date"):
		conditions += " and `viewPurchase Invoice`.posting_date >= '{}'".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and `viewPurchase Invoice`.posting_date <= '{}'".format(filters.get("to_date"))
	if filters.get("item_code"):
		conditions += " and `viewPurchase Invoice`.item_code = '{}'".format(filters.get("item_code"))
	if filters.get("unpaid") == 1:
		conditions += " and `viewPurchase Invoice`.outstanding_amount > 0"
		
	# if filters.get("limit"):
	# 	conditions += " LIMIT {}".format(filters.get("limit"))
	
	return conditions

def get_invoices(filters):

	conditions = get_conditions(filters)

	return frappe.db.sql("""
		SELECT 
			`viewPurchase Invoice`.due_date,
			`viewPurchase Invoice`.posting_date,
			`viewPurchase Invoice`.supplier,
			`viewPurchase Invoice`.item_code,
			`viewPurchase Invoice`.vim_number,
			`viewPurchase Invoice`.invoice_type,
			IF(
				`tabPayment Entry Reference`.allocated_amount AND `tabPayment Entry Reference`.allocated_amount < 0,
				`viewPurchase Invoice`.total * -1,
				`viewPurchase Invoice`.total
			) as total,
			`viewPurchase Invoice`.gst_total,
			`viewPurchase Invoice`.pst_total,
			`viewPurchase Invoice`.name,
			`tabPayment Entry Reference`.allocated_amount as breakdown,
			IF(
				`tabPayment Entry Reference`.allocated_amount AND `tabPayment Entry Reference`.allocated_amount < 0,
				`viewPurchase Invoice`.grand_total * -1,
				`viewPurchase Invoice`.grand_total
			) as grand_total,
			`viewPurchase Invoice`.trans_type,
			IF(
				`tabPayment Entry Reference`.allocated_amount AND `tabPayment Entry Reference`.allocated_amount < 0,
				`tabPayment Entry Reference`.allocated_amount,
				`viewPurchase Invoice`.paid_amount
			) as paid_amount,
			`viewPurchase Invoice`.outstanding_amount,
			`tabPayment Entry Reference`.parent as pinv
		FROM
			`viewPurchase Invoice`
		Left Join
			`tabPayment Entry Reference`
			On
			`tabPayment Entry Reference`.reference_name = `viewPurchase Invoice`.name
			And
				`tabPayment Entry Reference`.docstatus = 1
		Left Join
			`tabPayment Entry`
			On
			`tabPayment Entry Reference`.parent = `tabPayment Entry`.name
			And 
			`tabPayment Entry`.docstatus = 1 
		WHERE 
			{conditions}  
		ORDER BY 
			`viewPurchase Invoice`.item_code, `viewPurchase Invoice`.posting_date ASC, `viewPurchase Invoice`.name ASC, `tabPayment Entry Reference`.parent

	""".format(conditions=conditions or "1 = 1"), debug=True, as_dict=True)