# -*- coding: utf-8 -*-
# Copyright (c) 2020, TZCODE SRL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class VehicleRelease(Document):
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

		filters = {"type": self.type}
		for desc,  in frappe.get_list("Checklist Item", filters, as_list=True):
			self.append("checklist", {
				"description": desc
			})
