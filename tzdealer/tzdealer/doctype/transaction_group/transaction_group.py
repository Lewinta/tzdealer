# -*- coding: utf-8 -*-
# Copyright (c) 2019, TZCODE SRL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class TransactionGroup(Document):
	def validate(self):
		acc_comp = frappe.db.get_value("Account", self.account, "company")
		if acc_comp != self.company:
			frappe.throw(
				"The account <b>{account}</b> doesn't belong to <b>{company}</b>".format(
					**self.as_dict()
				)
			)