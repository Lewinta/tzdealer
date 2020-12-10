# -*- coding: utf-8 -*-
# Copyright (c) 2020, TZCODE SRL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class DeliveryChecklist(Document):
	def validate(self):
		self.validate_items()

	def validate_items(self):
		self.status = "Complete"
		for row in self.checklist:
			if not row.notes:
				self.status = "Incomplete"

	def get_items(self):
		self.checklist = []
		if not self.type:
			frappe.throw("Please select a Checklist Type!")

		items = frappe.db.sql("""
			SELECT 
				`tabChecklist Item`.name as description,
				`tabChecklist Item`.category 
			FROM
				`tabChecklist Item`
			JOIN
				`tabChecklist Type Item`
			ON
				`tabChecklist Item`.name = `tabChecklist Type Item`.parent
			AND
				`tabChecklist Type Item`.type = %s
			ORDER BY 
				`tabChecklist Item`.category, `tabChecklist Item`.name
		""", self.type, as_dict=True)

		filters = {"type": self.type}
		for row in items:
			self.append("checklist", row)
