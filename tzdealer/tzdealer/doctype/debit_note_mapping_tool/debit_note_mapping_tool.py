# -*- coding: utf-8 -*-
# Copyright (c) 2018, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe.model.document import Document
from frappe.utils import flt, cint, cstr
from frappe import get_doc, get_value, throw

class DebitNoteMappingTool(Document):
	def validate(self):
		if self.flags.ignore_validations:
			return

		self.validate_debit_note_balance()
		self.validate_invoice_balance()
		self.validate_mandatory_fields()
		self.validate_debit_note_against_invoice()
		self.validate_applied_amount()

	def apply_outstanding_amount_to_invoice(self):
		doctype = "Purchase Invoice"

		debit_note_balance = get_value(doctype,
			self.debit_note, "outstanding_amount")

		invoice_balance = get_value(doctype,
			self.purchase_invoice, "outstanding_amount")


		self.validate_mandatory_fields()

		self.validate_debit_note_against_invoice()

		self.validate_debit_note_balance(debit_note_balance)
		self.validate_invoice_balance(invoice_balance)

		self.validate_applied_amount(invoice_outstanding_amount=invoice_balance,
			unallocated_amount=debit_note_balance)

		self.flags.can_proceed = True
		self._apply_outstanding_amount_to_invoice(self.amount_to_apply)

	def _apply_outstanding_amount_to_invoice(self, debit_note_balance):
		if not self.flags.can_proceed:
			return

		invoice = get_doc(self.meta.get_field("purchase_invoice").options,
			self.purchase_invoice)

		debit_note = get_doc(self.meta.get_field("debit_note").options,
			self.debit_note)


		invoice.outstanding_amount -= debit_note_balance
		debit_note.outstanding_amount += debit_note_balance

		if invoice.outstanding_amount < .000:
			throw("""Ooops... Somehow the outstanding amount for invoice {invoice} is negative.
				<br>The debit was not applied. Please contact your System Manager!"""\
				.format(invoice=self.purchase_invoice))

		if flt(invoice.outstanding_amount, 3) == .000:
			invoice.status = "Paid"

		invoice.db_update()

		if debit_note.outstanding_amount > .000:
			throw("""Ooops... Somehow the outstanding amount for the Debit Note {debit_note}
				is positive. <br>The debit was not applied. Please contact your System Manager!"""\
				.format(debit_note=self.purchase_invoice))

		debit_note.db_update()

		invoice.add_comment("Update", "debit for {amount} was applied"\
			.format(amount=abs(debit_note_balance)))

	def validate_debit_note_balance(self, debit_note_balance=.000):
		if not debit_note_balance:
			debit_note_balance = self.unallocated_amount

		if debit_note_balance >= .000:
			throw("The Debit Note {debit_note} has no balance anymore!"\
				.format(debit_note=self.debit_note))

	def validate_invoice_balance(self, invoice_balance=.000):
		if not invoice_balance:
			invoice_balance = self.invoice_outstanding_amount

		if invoice_balance <= .000:
			throw("The purchase Invoice {purchase_invoice} has not any Outstanding Amount!"\
				.format(purchase_invoice=self.purchase_invoice))

	def validate_mandatory_fields(self):
		for fieldname in ("supplier", "debit_note", "purchase_invoice", "amount_to_apply"):
			label = self.meta.get_field(fieldname).label
			message = "Required: {label} is a mandatory field!".format(label=label)

			if not self.get(fieldname):
				throw(message)

	def validate_debit_note_against_invoice(self):
		doctype = "Purchase Invoice"

		if self.debit_note == self.purchase_invoice:
			throw("Purchase Invoice and Debit Note should be not be linked!")

		debit_note_supplier = get_value(doctype, self.debit_note, "supplier")
		purchase_invoice_supplier = get_value(doctype, self.purchase_invoice, "supplier")

		if not debit_note_supplier == purchase_invoice_supplier:
			throw("Purchase Invoice and Debit Note should have the same supplier!")

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
