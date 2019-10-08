# -*- coding: utf-8 -*-
# Copyright (c) 2018, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe.model.document import Document
from frappe.utils import flt, cint, cstr
from frappe import get_doc, get_value, throw

class CreditNoteMappingTool(Document):
	def validate(self):
		if self.flags.ignore_validations:
			return

		self.validate_credit_note_balance()
		self.validate_invoice_balance()
		self.validate_mandatory_fields()
		self.validate_credit_note_against_invoice()
		self.validate_applied_amount()

	def apply_outstanding_amount_to_invoice(self):
		doctype = "Sales Invoice"

		credit_note_balance = get_value(doctype,
			self.credit_note, "outstanding_amount")

		invoice_balance = get_value(doctype,
			self.sales_invoice, "outstanding_amount")


		self.validate_mandatory_fields()

		self.validate_credit_note_against_invoice()

		self.validate_credit_note_balance(credit_note_balance)
		self.validate_invoice_balance(invoice_balance)

		self.validate_applied_amount(invoice_outstanding_amount=invoice_balance,
			unallocated_amount=credit_note_balance)

		self.flags.can_proceed = True
		self._apply_outstanding_amount_to_invoice(self.amount_to_apply)

	def _apply_outstanding_amount_to_invoice(self, credit_note_balance):
		if not self.flags.can_proceed:
			return

		invoice = get_doc(self.meta.get_field("sales_invoice").options,
			self.sales_invoice)

		credit_note = get_doc(self.meta.get_field("credit_note").options,
			self.credit_note)


		invoice.outstanding_amount -= credit_note_balance
		credit_note.outstanding_amount += credit_note_balance

		if invoice.outstanding_amount < .000:
			throw("""Ooops... Somehow the outstanding amount for invoice {invoice} is negative.
				<br>The credit was not applied. Please contact your System Manager!"""\
				.format(invoice=self.sales_invoice))

		if flt(invoice.outstanding_amount, 3) == .000:
			invoice.status = "Paid"

		invoice.db_update()

		if credit_note.outstanding_amount > .000:
			throw("""Ooops... Somehow the outstanding amount for the credit note {credit_note}
				is positive. <br>The credit was not applied. Please contact your System Manager!"""\
				.format(credit_note=self.sales_invoice))

		credit_note.db_update()

		invoice.add_comment("Update", "Credit for {amount} was applied"\
			.format(amount=abs(credit_note_balance)))

	def validate_credit_note_balance(self, credit_note_balance=.000):
		if not credit_note_balance:
			credit_note_balance = self.unallocated_amount

		if credit_note_balance >= .000:
			throw("The Credit Note {credit_note} has no balance anymore!"\
				.format(credit_note=self.credit_note))

	def validate_invoice_balance(self, invoice_balance=.000):
		if not invoice_balance:
			invoice_balance = self.invoice_outstanding_amount

		if invoice_balance <= .000:
			throw("The Sales Invoice {sales_invoice} has not any Outstanding Amount!"\
				.format(sales_invoice=self.sales_invoice))

	def validate_mandatory_fields(self):
		for fieldname in ("customer", "credit_note", "sales_invoice", "amount_to_apply"):
			label = self.meta.get_field(fieldname).label
			message = "Required: {label} is a mandatory field!".format(label=label)

			if not self.get(fieldname):
				throw(message)

	def validate_credit_note_against_invoice(self):
		doctype = "Sales Invoice"

		if self.credit_note == self.sales_invoice:
			throw("Sales Invoice and Credit Note should be not be linked!")

		credit_note_customer = get_value(doctype, self.credit_note, "customer")
		sales_invoice_customer = get_value(doctype, self.sales_invoice, "customer")

		if not credit_note_customer == sales_invoice_customer:
			throw("Sales Invoice and Credit Note should have the same customer!")

	def validate_applied_amount(self, amount_to_apply=.000, invoice_outstanding_amount=.000, unallocated_amount=.000):
		if not amount_to_apply:
			amount_to_apply = self.amount_to_apply

		if not invoice_outstanding_amount:
			invoice_outstanding_amount = self.invoice_outstanding_amount

		if not unallocated_amount:
			unallocated_amount = self.unallocated_amount

		if amount_to_apply > invoice_outstanding_amount:
			throw("Amount to Apply cannot be greater than the Invoice Outstanding Amount")

		if amount_to_apply > abs(unallocated_amount):
			throw("Amount to Apply cannot be greater than the Unallocated Amount")
