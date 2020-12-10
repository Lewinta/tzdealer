import frappe
from frappe.utils.background_jobs import enqueue

def on_update(doc, event):
	enqueue(
        update_customer_name,
        queue="short",
        job_name="update_customer_name",
        doc=doc
    )

def update_customer_name(doc):
	filters = {
		"customer": doc.name,
		"customer_name": [ "!=", doc.customer_name]
	}
	for name in frappe.get_list("Sales Invoice", filters, as_list=True):
		sinv =  frappe.get_doc("Sales Invoice", name)
		sinv.customer_name = doc.customer_name
		sinv.db_update()
	frappe.db.commit()
