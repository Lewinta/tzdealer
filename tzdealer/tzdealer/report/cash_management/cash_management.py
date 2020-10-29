# Copyright (c) 2013, TZCODE SRL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _

def execute(filters=None):
	return get_columns(), get_data(filters)

def get_columns():
	return [
		_("Company") 		+ ":Data:100",
		_("G Sale") 		+ ":Currency/currency:120",
		_("Total Sale") 	+ ":Currency/currency:100",
		_("Cash Received") 	+ ":Currency/currency:100",
		_("Cash Paid") 		+ ":Currency/currency:100",
		_("Cash Balance") 	+ ":Currency/currency:120",
		_("Short/Over") 	+ ":Currency/currency:100",
		_("Shall be Deposited") 	+ ":Currency/currency:150",
	]
def get_conditions(filters):
	conditions = ["t.docstatus = 1"]

	if filters.get("company"):
		conditions.append("t.company = '{}'".format(filters.get("company")))

	return " AND ".join(conditions)

def get_data(filters=None):
	conditions = get_conditions(filters)

	sinv = frappe.db.sql("""
		SELECT
			t.company,
			SUM(t.grand_g_total) as grand_g_total,
			SUM(t.grand_total) as grand_total
		FROM 
			`tabSales Invoice` as t
		WHERE 
			{conditions}
	""".format(conditions=conditions), debug=True, as_dict=True)

	paymts = frappe.db.sql("""
		SELECT
			t.Company,
			SUM(IF(
				t.payment_type = 'Receive',
				t.paid_amount,
				0
			)) as received_amount,
			SUM(IF(
				t.payment_type = 'Pay',
				t.paid_amount,
				0
			)) as paid_amount
		
		FROM 
			`tabPayment Entry` as t
		WHERE 
			{conditions}
		AND 
			t.mode_of_payment in ('CASH COMPANY - CAD', 'Uzair Cash-CAD')
		GROUP BY 
			t.Company
	""".format(conditions=conditions), debug=True, as_dict=True)
	
	cash_balance = paymts[0].received_amount -  paymts[0].paid_amount
	short_over = sinv[0].grand_g_total - sinv[0].grand_total
	
	return [
		(
			sinv[0].company or "-",
			sinv[0].grand_g_total or 0,
			sinv[0].grand_total or 0,
			paymts[0].received_amount or 0,
			paymts[0].paid_amount or 0,
			cash_balance, # Cash Balance
			short_over,
			cash_balance - abs(short_over),
		)
	]
