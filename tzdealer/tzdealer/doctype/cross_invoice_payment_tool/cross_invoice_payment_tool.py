# -*- coding: utf-8 -*-
# Copyright (c) 2020, TZCODE SRL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate

class CrossInvoicePaymentTool(Document):
	def apply_payment(self):
		jv = frappe.new_doc("Journal Entry");
		amount = min(self.total_sales, self.total_purchases)
		max_debit = max_credit = amount
		jv.update({
			"entry_type": "Journal Entry",
			"posting_date": self.posting_date,
			"company": self.company,
			"transaction_type": "G",
			"cheque_date": self.posting_date,
			"cheque_no": str(nowdate()),
			"user_remark": "Cross Invoice Payment",
		})
		for row in self.supplier_invoices + self.customer_invoices:
			debit = credit = .000
			
			if not max_credit and not max_debit:
				continue

			if row.invoice_type == "Purchase Invoice":
				if row.amount > max_debit:
					debit = max_debit
				else:
					debit = row.amount
			
			if row.invoice_type == "Sales Invoice":
				if row.amount > max_credit:
					credit = max_credit
				else:
					credit = row.amount

		
			jv.append("accounts", {
				"account": row.account,
				"party_type": "Supplier" if row.invoice_type == "Purchase Invoice" else "Customer",
				"party": row.party,
				"debit": debit,
				"debit_in_account_currency": debit,
				"credit": credit,
				"credit_in_account_currency": credit,
				"reference_type": row.invoice_type,
				"reference_name": row.invoice,
			})
			
			max_debit  -= debit
			max_credit -= credit
			
		jv.save()
		jv.submit()
