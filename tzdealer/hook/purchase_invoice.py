import frappe

def validate(doc, event):
	update_expense_account(doc)
	validate_expense_account(doc)

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

def update_expense_account(doc):
	filters = {"company": doc.company, "default": 1}
	
	warehouse = frappe.db.get_value("Warehouse", filters, "name")
	
	for item in doc.items:
		item.expense_account = doc.account
		item.warehouse = warehouse

def validate_expense_account(doc):
	for item in doc.items:
		if item.expense_account != doc.account:
			frappe.throw("Invalid Transaction Group on row {}".format(item.idx))	