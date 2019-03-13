import frappe
from frappe.model.naming import make_autoname

def before_insert(doc, event):
	if doc.item_type == "Vehicle Parts" and  not doc.item_code:
		doc.item_code = make_autoname("PART-") 

	if doc.item_type == "Containers" and  not doc.item_code:
		doc.item_code = make_autoname("CONT-") 
		