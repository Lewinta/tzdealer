import frappe
import json

@frappe.whitelist(allow_guest=True)
def get_items(filters=None, fields=None):
	if type(filters) == unicode:
		filters = json.loads(filters)

	if type(fields) == unicode:
		fields = json.loads(fields)
		
	return frappe.get_all("Item", filters, fields)