import frappe
from frappe.utils.background_jobs import enqueue

def on_update(doc, event):
	enqueue(
        update_supplier_name,
        queue="short",
        job_name="update_supplier_name",
        doc=doc
    )

def update_supplier_name(doc):
	filters = {
		"supplier": doc.name,
		"supplier_name": [ "!=", doc.supplier_name]
	}
	for name in frappe.get_list("Sales Invoice", filters, as_list=True):
		sinv =  frappe.get_doc("Sales Invoice", name)
		sinv.supplier_name = doc.supplier_name
		sinv.db_update()
	frappe.db.commit()
