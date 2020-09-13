import frappe
from frappe.model.naming import make_autoname

def validate(doc, event):
	entity = city = state = ""

	if doc.links:
		entity = "{} -".format(doc.links[0].link_name)

	if doc.city:
		city = doc.city

	if doc.state:
		state = doc.state

	doc.custom_title = "{} {}, {}".format(entity, city, state)

def autoname(doc, event):
	doc.name = make_autoname("A-.")