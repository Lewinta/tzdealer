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
			details = "-" 
			if inv.model:
				details = "{} {} {} {}".format(inv.make, inv.model, inv.exterior_color, inv.year)
			# elif inv.cont_vim:
			# 	details = inv.cont_vim.split("-")[1]
			row = [
				inv.company,
				inv.item_code,
				inv.vim_number,
				details,
				inv.due_date,
				inv.posting_date,
				inv.supplier,
				inv.invoice_type,
				inv.total,
				inv.gst_total,
				inv.pst_total,
				inv.grand_total,
				inv.trans_type,
				inv.payment_date or "",
				inv.name,
				inv.breakdown,
				inv.paid_amount,
				inv.outstanding_amount,
				inv.pinv,
			]
		else:
			row = [
				"", # Company
				"",	# Stock No.
				"",	# Vim Number
				"",	# Details
				"", # Due Date
				"", # Inv. Date
				inv.supplier,
				inv.invoice_type,
				.000,
				.000,
				.000,
				.000,
				inv.trans_type,
				inv.payment_date or "",
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
		_("Company") 			+ ":Company:120",
		_("Stock No.") 			+ ":Link/Item:120",
		_("Vim Number") 		+ ":Data:150",
		_("Details") 			+ ":Data:250",
		_("Due Date") 			+ ":Date:80",
		_("Inv.Date") 			+ ":Date:80",
		_("Supplier") 			+ ":Link/Supplier:180",
		_("Invoice Type") 		+ ":Link/Purchase Invoice:90",
		_("Net Total") 			+ ":Currency/currency:120",
		_("GST") 				+ ":Currency/currency:100",
		_("PST") 				+ ":Currency/currency:100",
		_("Grand Total") 		+ ":Currency/currency:120",
		_("Trs. Type") 			+ ":Data:80",
		_("Payment Date") 		+ ":Date:100",
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
	conditions = ''
	if filters.get("company"):
		conditions = " `viewSupplier Age`.company = '{}'".format(filters.get("company"))
	# conditions += " and IFNULL(`tabPayment Entry Reference`.allocated_amount, 0) >= 0"

		# conditions += " and company = %(company)s"
	if filters.get("supplier"):
		conditions += " and `viewSupplier Age`.supplier  = '{}'".format(filters.get("supplier"))
	if filters.get("from_date"):
		conditions += " and `viewSupplier Age`.posting_date >= '{}'".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and `viewSupplier Age`.posting_date <= '{}'".format(filters.get("to_date"))
	if filters.get("item_code"):
		conditions += " and `viewSupplier Age`.item_code = '{}'".format(filters.get("item_code"))
	if filters.get("unpaid") == 1:
		if conditions:
			conditions += " and "
		conditions += " `viewSupplier Age`.outstanding_amount > 0"
		
	# if filters.get("limit"):
	# 	conditions += " LIMIT {}".format(filters.get("limit"))
	
	return conditions

def get_invoices(filters):

	conditions = get_conditions(filters)

	return frappe.db.sql("""
		SELECT 
			`viewSupplier Age`.company,
			`viewSupplier Age`.due_date,
			`viewSupplier Age`.posting_date,
			`viewSupplier Age`.supplier,
			`viewSupplier Age`.item_code,
			`viewSupplier Age`.make,
			`viewSupplier Age`.model,
			`viewSupplier Age`.exterior_color,
			`viewSupplier Age`.year,
			`viewSupplier Age`.vim_number,
			`viewSupplier Age`.invoice_type,
			IF(
				`tabPayment Entry Reference`.allocated_amount AND `tabPayment Entry Reference`.allocated_amount < 0,
				`viewSupplier Age`.base_total * -1,
				`viewSupplier Age`.base_total
			) as total,
			`viewSupplier Age`.gst_total,
			`viewSupplier Age`.pst_total,
			`viewSupplier Age`.name,
			`tabPayment Entry Reference`.allocated_amount as breakdown,
			IF(
				`tabPayment Entry Reference`.allocated_amount AND `tabPayment Entry Reference`.allocated_amount < 0,
				`viewSupplier Age`.base_grand_total * -1,
				`viewSupplier Age`.base_grand_total
			) as grand_total,
			`viewSupplier Age`.trans_type,
			IF(
				`tabPayment Entry Reference`.allocated_amount AND `tabPayment Entry Reference`.allocated_amount < 0,
				`tabPayment Entry Reference`.allocated_amount,
				`viewSupplier Age`.paid_amount
			) as paid_amount,
			`viewSupplier Age`.outstanding_amount,
			`tabPayment Entry Reference`.parent as pinv,
			`tabPayment Entry`.date as payment_date
		FROM
			`viewSupplier Age`
		Left Join
			`tabPayment Entry Reference`
			On
			`tabPayment Entry Reference`.reference_name = `viewSupplier Age`.name
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
			`viewSupplier Age`.item_code, `viewSupplier Age`.posting_date ASC, `viewSupplier Age`.name ASC, `tabPayment Entry Reference`.parent

	""".format(conditions=conditions or "1 = 1"), debug=False, as_dict=True)