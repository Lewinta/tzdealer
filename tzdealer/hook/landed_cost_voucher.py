import frappe
from erpnext.controllers.accounts_controller import get_taxes_and_charges
def on_submit(doc, event):
	if not doc.taxes:
		return

	for tax in doc.taxes:
		if tax.create_invoice:
			create_purchase_invoice(tax)

def on_cancel(doc, event):
	if not doc.taxes:
		return

	for tax in doc.taxes:
		if not tax.invoice or not frappe.db.exists("Purchase Invoice", tax.invoice):
			return
		
		inv = frappe.get_doc("Purchase Invoice", tax.invoice)
		if inv.docstatus == 1:
			inv.cancel()

def on_trash(doc, event):
	if not doc.taxes:
		return

	for tax in doc.taxes:
		if not tax.invoice or not frappe.db.exists("Purchase Invoice", tax.invoice):
			return
		
		inv = frappe.get_doc("Purchase Invoice", tax.invoice)
		
		if inv.docstatus == 1:
			on_cancel(doc, event)
		
		inv.delete()

def create_purchase_invoice(row):
	p_inv = frappe.new_doc("Purchase Invoice")
	p_inv.update({
		"invoice_type": "Services",
		"supplier": row.vendor,
		"update_stock": 0,
		"bill_no": row.supplier_invoice or "",
		"taxes_and_charges": row.tax or "",
		"account": "5330 - Transport Charges CAD - EZ",
		"transaction_group": "5330 - Transport Charges CAD",
	})
	# Let's create the item if doesn't exists
	item_name = "Voucher Expenses" 

	p_inv.append("items", {
		"item_name": item_name,
		"qty": 1,
		"uom": "Unit",
		"conversion_factor": 1,
		"stock_uom": "Unit",
		"stock_qty": 1,
		"expense_account": "5330 - Transport Charges CAD - EZ",
		"rate": row.total if row.total else row.amount,
	})

	p_inv.set_missing_values()
	if row.tax:
		for r in get_taxes_and_charges(
			master_doctype="Purchase Taxes and Charges Template",
			master_name=row.tax
		):
			p_inv.append("taxes", r)

	p_inv.calculate_taxes_and_totals()
	p_inv.save()
	p_inv.submit()
	row.update({
		"invoice": p_inv.name,
		"date": p_inv.posting_date 
	})
	row.db_update()