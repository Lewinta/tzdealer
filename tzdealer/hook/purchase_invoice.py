import frappe

def on_cancel(doc, event):
	cancel_sle(doc, event)

def cancel_sle(doc, event):
	filters = {
		"voucher_type": "Purchase Invoice",
		"voucher_no": doc.name,
		"docstatus": 1
	}

	for name, in frappe.get_list("Stock Ledger Entry", filters, as_list=True):
		sle = frappe.get_doc("Stock Ledger Entry", name)
		sle.docstatus = 2
		sle.db_update()