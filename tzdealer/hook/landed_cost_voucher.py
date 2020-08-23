import frappe
from erpnext.controllers.accounts_controller import get_taxes_and_charges
from frappe.utils import add_days, today

def on_submit(doc, event):
	if not doc.taxes:
		return

	for tax in doc.taxes:
		if tax.create_invoice:
			tax = tax.update({"company": doc.company})
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
			tax.invoice = ''

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
@frappe.whitelist()
def create_purchase_invoice(row):
	import json

	if type(row) == unicode:
		_row = frappe._dict(json.loads(row))
		row = frappe.get_doc("Landed Cost Taxes and Charges", _row.name)

	if row.invoice:
		return "This LCV already has an invoice"

	total  = abs(row.total)
	amount = abs(row.amount)
	p_inv = frappe.new_doc("Purchase Invoice")
	
	account = frappe.db.get_value(
		"Transaction Group", 
		row.transaction_group,
		"account"
	)

	credit_to = frappe.get_value("Company", row.company, "default_payable_account")

	if not account:
		frappe.throw(
			"Please set account for Transaction Group {}".format(
				row.transaction_group
			)
		)

	inv_date = row.date or today()

	p_inv.update({
		"invoice_type": "Services",
		"supplier": row.vendor,
		"posting_date": inv_date,
		"date": inv_date,
		"company": frappe.db.get_value("Landed Cost Voucher", row.parent, "company"),
		"due_date": add_days(inv_date, 30),
		"update_stock": 0,
		"credit_to": credit_to,
		"set_posting_time": 1,
		"bill_no": row.supplier_invoice or "",
		"taxes_and_charges": row.tax or "",
		"currency": row.currency or "CAD",
		"exchange_rate": row.tax or "1",
		"account": account,
		"transaction_group": row.transaction_group,
		"trans_type": row.transaction_type,
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
		"expense_account": account,
		"rate": total if total else amount,
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
		"date": p_inv.posting_date, 
		"create_invoice": 1 
		#if created using the button this needs to be set to 1
	})
	row.db_update()

	if row.amount < 0:
		pay_and_return(p_inv)

	return "Purchase Invoice {} Created".format(p_inv.name)

@frappe.whitelist()
def create_purchase_invoice_test(row):
	return "PINV-00938"

def pay_and_return(p_inv):
	from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import make_debit_note
	from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
	# Let's pay the invoice
	paid_from = frappe.get_value(
		"Mode of Payment Account",
		{"parent":"Cash", "company":p_inv.company},
		"default_account"
	)
	pe = get_payment_entry(p_inv.doctype, p_inv.name)

	pe.update({
		"mode_of_payment": "Cash",
		"paid_from": paid_from
	})
	pe.save()
	pe.submit()

	# Now let's make the credit note

	dn = make_debit_note(p_inv.name)
	dn.save()
	dn.submit()




