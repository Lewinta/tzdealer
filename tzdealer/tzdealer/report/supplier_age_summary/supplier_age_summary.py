# Copyright (c) 2013, TZCODE SRL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _

mop_1 = frappe.get_list("Mode of Payment", as_list=True, limit=5)[0][0]
mop_2 = frappe.get_list("Mode of Payment", as_list=True, limit=5)[1][0]
mop_3 = frappe.get_list("Mode of Payment", as_list=True, limit=5)[2][0]
mop_4 = frappe.get_list("Mode of Payment", as_list=True, limit=5)[3][0]
mop_5 = frappe.get_list("Mode of Payment", as_list=True, limit=5)[4][0]

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

		details = "-" 
		if inv.invoice_type == "Vehicles":
			details = "{} {} {} {}".format(inv.make, inv.model, inv.exterior_color or "", inv.year or "")
		if inv.invoice_type == "Containers":
			details = "{} {}".format(inv.booking_no or "", inv.container_no or "")
		if inv.invoice_type == "Parts":
			details = inv.part_type or ""
		if inv.invoice_type == "Services":
			details = inv.item_name or ""
		# elif inv.cont_vim:
		# 	details = inv.cont_vim.split("-")[1]
		total_paid = inv.mop_1 + inv.mop_2 + inv.mop_3 + inv.mop_4 + inv.mop_5
		row = (
			inv.company, 										# Company
			inv.invoice_type,									# Invoice Type
			inv.stock_no,										# Stock No.
			inv.vim_number,										# Vim Number
			details,											# Details
			inv.due_date,
			inv.posting_date,
			inv.supplier,
			inv.base_total,
			inv.total if inv.currency == "USD" else .00,
			inv.gst_total,
			inv.pst_total,
			inv.base_grand_total,
			inv.grand_total if inv.currency == "USD" else .00,
			inv.trans_type,
			inv.mop_1 if last_inv != inv.name  or entry != inv.payment_entry else .00,			#MOP1	
			inv.mop_2 if last_inv != inv.name  or entry != inv.payment_entry else .00,			#MOP2
			inv.mop_3 if last_inv != inv.name  or entry != inv.payment_entry else .00,			#MOP3
			inv.mop_4 if last_inv != inv.name  or entry != inv.payment_entry else .00,			#MOP4
			inv.mop_5 if last_inv != inv.name  or entry != inv.payment_entry else .00,			#MOP5
			total_paid, 																			#Total Paid
			inv.outstanding_amount if last_inv != inv.name else .00, 							#Outstanding
			inv.name,
		)
	
		last_inv = inv.name
		last_vim = inv.item_code
		data.append(row)

	return columns, data

def get_columns(invoice_list):
	"""return columns based on filters"""
	columns = [
		_("Company") 			+ ":Company:120",
		_("Invoice Type") 		+ ":Data:90",
		_("Stock No.") 			+ ":Link/Item:120",
		_("Vim Number") 		+ ":Data:150",
		_("Details") 			+ ":Data:220",
		_("Due Date") 			+ ":Date:80",
		_("Inv.Date") 			+ ":Date:80",
		_("Supplier") 			+ ":Link/Supplier:180",
		_("Net") 				+ ":Currency/currency:120",
		_("Net USD") 			+ ":Currency/currency:120",
		_("GST") 				+ ":Currency/currency:100",
		_("PST") 				+ ":Currency/currency:100",
		_("Total CAD") 			+ ":Currency/currency:120",
		_("Total USD") 			+ ":Currency/currency:120",
		_("Trs. Type") 			+ ":Data:80",
		_(mop_1)				+ ":Currency/currency:120",
		_(mop_2)				+ ":Currency/currency:120",
		_(mop_3)				+ ":Currency/currency:120",
		_("CASH CAD") 			+ ":Currency/currency:120",
		_(mop_5)				+ ":Currency/currency:120",
		_("Total Paid") 		+ ":Currency/currency:120",
		_("Outstanding") 		+ ":Currency/currency:120",
		_("Invoice") 			+ ":Link/Purchase Invoice:120",
	]

	return columns

def get_conditions(filters):
	# company = frappe.get_value("User Permission", {
	# 	"user":frappe.session.user,
	# 	"allow":"Company",
	# }, "for_value")
	conditions = ""
	
	if filters.get("company"):
		conditions = "`viewSupplier Age`.company = '{}'".format(filters.get("company"))
	if filters.get("supplier"):
		if conditions:
			conditions += " and "
		conditions += "`viewSupplier Age`.supplier  = '{}'".format(filters.get("supplier"))
	if filters.get("from_date"):
		if conditions:
			conditions += " and "
		conditions += "`viewSupplier Age`.posting_date >= '{}'".format(filters.get("from_date"))
	if filters.get("to_date"):
		if conditions:
			conditions += " and "
		conditions += "`viewSupplier Age`.posting_date <= '{}'".format(filters.get("to_date"))
	if filters.get("item_code"):
		if conditions:
			conditions += " and "
		conditions += "`viewSupplier Age`.item_code = '{}'".format(filters.get("item_code"))

	if filters.get('payment_status') == "Unpaid Only":
		if conditions:
			conditions += " and "
		conditions += "`viewSupplier Age`.outstanding_amount > 0"
	
	if filters.get('payment_status') == "Paid Only":
		if conditions:
			conditions += " and "
		conditions += "`viewSupplier Age`.outstanding_amount = 0"

		
	# if filters.get("limit"):
	# 	conditions += " LIMIT {}".format(filters.get("limit"))
	
	return conditions

def get_invoices(filters):

	conditions = get_conditions(filters)
	if conditions:
		conditions = "WHERE {}".format(conditions)

	return frappe.db.sql("""
		SELECT 
			`viewSupplier Age`.company,
			`viewSupplier Age`.due_date,
			`viewSupplier Age`.posting_date,
			`viewSupplier Age`.supplier,
			`viewSupplier Age`.item_code,
			`viewSupplier Age`.stock_no,
			`viewSupplier Age`.make,
			`viewSupplier Age`.part_type,
			`viewSupplier Age`.model,
			`viewSupplier Age`.booking_no,
			`viewSupplier Age`.container_no,
			`viewSupplier Age`.exterior_color,
			`viewSupplier Age`.year,
			`viewSupplier Age`.vim_number,
			`viewSupplier Age`.invoice_type,
			`viewSupplier Age`.currency,
			`viewSupplier Age`.total,
			`viewSupplier Age`.base_total,
			`viewSupplier Age`.gst_total,
			`viewSupplier Age`.pst_total,
			`viewSupplier Age`.grand_total,
			`viewSupplier Age`.base_grand_total,
			`viewSupplier Age`.name,
			`viewSupplier Age`.trans_type,
			`viewSupplier Age`.outstanding_amount,
			SUM(
				IF(
					`tabPayment Entry`.mode_of_payment = '{mop_1}',
					IFNULL(`tabPayment Entry Reference`.allocated_amount, 0), 0
				)
			) as mop_1,
			SUM(
				IF(
					`tabPayment Entry`.mode_of_payment = '{mop_2}',
					IFNULL(`tabPayment Entry Reference`.allocated_amount, 0), 0
				)
			) as mop_2,
			SUM(
				IF(
					`tabPayment Entry`.mode_of_payment = '{mop_3}',
					IFNULL(`tabPayment Entry Reference`.allocated_amount, 0), 0
				)
			) as mop_3,
			SUM(
				IF(
					`tabPayment Entry`.mode_of_payment = '{mop_4}',
					IFNULL(`tabPayment Entry Reference`.allocated_amount, 0), 0
				)
			) as mop_4,
			SUM(
				IF(
					`tabPayment Entry`.mode_of_payment = '{mop_5}',
					IFNULL(`tabPayment Entry Reference`.allocated_amount, 0), 0
				)
			) as mop_5
			
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
		{conditions}
		Group By 
			`viewSupplier Age`.name
		ORDER BY 
			`viewSupplier Age`.item_code, `viewSupplier Age`.posting_date ASC, `viewSupplier Age`.name ASC, `tabPayment Entry Reference`.parent
	""".format(conditions=conditions, mop_1=mop_1, mop_2=mop_2, mop_3=mop_3, mop_4=mop_4, mop_5=mop_5,), debug=False, as_dict=True)