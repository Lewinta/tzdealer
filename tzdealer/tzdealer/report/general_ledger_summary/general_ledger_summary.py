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
		_("Account") 		+ ":Link/Account:300",
		_("Debit") 			+ ":Currency/currency:150",
		_("Credit") 		+ ":Currency/currency:150",
		_("Balance") 		+ ":Currency/currency:150",
	]

def get_data(filters=None):
	conditions = get_conditions(filters)

	frappe.errprint(conditions)
	return frappe.db.sql("""
		SELECT
			account,
			SUM(debit) AS debit,
			SUM(credit) AS credit,
			SUM(debit) - SUM(credit) AS balance
		FROM 
			`tabGL Entry`
		WHERE
			%s
		GROUP BY
			account
	""" % conditions, filters)

def get_conditions(filters):
	
	conditions = []

	if filters.get("company"):			
		conditions.append("company = %(company)s")
	
	if filters.get("from_date"):			
		conditions.append("posting_date >= %(from_date)s")

	if filters.get("to_date"):
		conditions.append("posting_date <= %(to_date)s")
	
	if filters.get("account"):
		conditions.append("account = %(account)s")

	return " AND ".join(conditions)

