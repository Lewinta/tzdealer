import frappe

def after_insert(doc, event):
	if not frappe.db.exists("Supplier", doc.partner_name):
		create_supplier(doc)

def on_trash(doc, event):
	if frappe.db.exists("Supplier", doc.partner_name):
		supplier = frappe.get_doc("Supplier", doc.partner_name)
		supplier.delete()

def create_supplier(doc):
	supplier = frappe.new_doc("Supplier")
	supplier.update({
		"company": doc.company,
		"supplier_name": doc.partner_name,
		"supplier_type": "Distributor",
		"tax_id": doc.tax_id,
		"phone_number": doc.phone_number,
	})
	supplier.save()