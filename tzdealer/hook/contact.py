import frappe
import json

@frappe.whitelist()
def create_user(doc):

	if isinstance(doc, basestring):
		doc = json.loads(doc)

	doc = frappe._dict(doc)

	doc = frappe.get_doc("Contact", doc.name)

	if not doc.first_name:
		frappe.throw("Please fill first name")
	if not doc.email_id:
		frappe.throw("Please fill email")

	if not frappe.db.exists("User", doc.email_id):

		usr = frappe.new_doc("User")

		usr.update({
			"first_name": doc.first_name, 
			"last_name": doc.last_name, 
			"email": doc.email_id, 
			"username": doc.email_id, 
			"send_welcome_email": 0L, 
		})

		usr.add_roles(doc.contact_type)
		
		usr.save(ignore_permissions=True)
	else: 
		usr = frappe.get_doc("User", email_id)

	doc.user = usr.email

	doc.db_update()
