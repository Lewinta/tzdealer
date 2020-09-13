# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from erpnext.controllers.accounts_controller import get_taxes_and_charges
from frappe.utils import add_days

def validate(doc, event):
	if doc.customer != doc.title:
		doc.title = doc.customer

	expense_account = frappe.db.get_value(
		"Company",
		doc.company,
		"expenses_included_in_valuation"
	)

	for item in doc.items:
		if not item.expense_account:
			item.expense_account = expense_account

def on_submit(doc, event):
	# When submitting an invoice we need to update the last sold price
	# to each Item.

	for sinv_item in doc.items:
		if not sinv_item.item_code or not frappe.db.exists("Item", sinv_item.item_code):
			continue
		
		item = frappe.get_doc("Item", sinv_item.item_code)
		item.last_sold_price = sinv_item.rate
		item.db_update()

	create_comission_invoice(doc)

def on_cancel(doc, event):
	if frappe.db.exists("Purchase Invoice", {"bill_no": doc.name}):
		pinv = frappe.get_doc("Purchase Invoice", {"bill_no": doc.name})
		if pinv.docstatus == 1 and pinv.paid_amount == 0:
			pinv.cancel()
			
		else:
			frappe.throw("""
				You cannot cancel this invoice because it has a commission invoice associated <b>
				<a href='/desk#Form/Purchase Invoice/{name}'>{name}</a></b>.<br>
				and has payments, 
			""".format(**pinv.as_dict()))


def create_or_update_item_price(doc):
	from frappe import db, new_doc, get_doc

	cwdoc = "Item Price"

	selling_gprice_list = db.get_single_value("Selling Settings",
			"selling_gprice_list")
	
	if doc and not doc.item_code:
		return 
		
	filters = {
		 "item_code": doc.item_code,
		 "selling": True,
		 "price_list": selling_gprice_list,
	}

	item_price = get_doc(cwdoc, filters) \
		if db.exists(cwdoc, filters) \
		else new_doc(cwdoc)

	item_price.update({
		"item_name": doc.item_name,
		"item_description": doc.description,
		"price_list_rate": doc.gprice,
		"price_list": selling_gprice_list,
	})

	item_price.save(ignore_permissions=True)

def create_comission_invoice(doc):
	if doc.total_commission <= .000:
		return
	pinv = frappe.new_doc("Purchase Invoice")
	abbr = frappe.get_value("Company", doc.company, "abbr")
	trans_group = "Commissions - {}".format(abbr)
	credit_account = frappe.get_value("Company", doc.company, "default_payable_account")
	account = frappe.get_value("Transaction Group", trans_group, "account")
	pinv.update({
		"company": doc.company,
		"invoice_type": "Services",
		"supplier": doc.sales_partner,
		"date": doc.posting_date,
		"posting_date": doc.posting_date,
		"transaction_group": trans_group,
		"account": account,
		"due_date": add_days(doc.posting_date, 30),
		"trans_type": "G",
		"bill_no": doc.name,
		"credit_to": credit_account,
	})
	pinv.append("items", {
		"item_code": "COMMISSIONS",
		"rate": doc.total_commission,
		"expense_account": account,
	})
	pinv.set_missing_values()
	if doc.commission_tax:
		for r in get_taxes_and_charges(
			master_doctype="Purchase Taxes and Charges Template",
			master_name=doc.commission_tax
		):
			pinv.append("taxes", r)

	pinv.calculate_taxes_and_totals()
	pinv.save()
	pinv.submit()

	frappe.msgprint("""
		A Commission invoice has been created for Sales Partner <b>{}</b><br>
		<b><a href='/desk#Form/Purchase Invoice/{}'>{}</a></b>
	""".format(doc.sales_partner, pinv.name, pinv.name))





