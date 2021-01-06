# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.naming import make_autoname
from erpnext.controllers.accounts_controller import get_taxes_and_charges
from frappe.utils import add_days, flt
import json

def autoname(doc, event):
	abbr = frappe.get_value("Company", doc.company, "abbr")
	new_name = make_autoname("_{}-.########".format(abbr))
	doc.contract_no = new_name[1:]
	
def validate(doc, event):
	if doc.customer != doc.title:
		doc.title = doc.customer

	expense_account = frappe.db.get_value(
		"Company",
		doc.company,
		"expenses_included_in_valuation"
	)

	cost_center = frappe.db.get_value("Company", doc.company, "cost_center")
	doc.taxes = []
	abbr = frappe.get_value("Company", doc.company, "abbr")
	taxes_obj = {
		'GST receivable - 5% - {}'.format(abbr): {'amount': .000, 'g_amount': .00},
		'H2 receivable - 14% - {}'.format(abbr): {'amount': .000, 'g_amount': .00},
		'HE receivable - 5% - {}'.format(abbr): {'amount': .000, 'g_amount': .00},
		'HST receivable - 13% - {}'.format(abbr): {'amount': .000, 'g_amount': .00},
		'HST receivable - 15% - {}'.format(abbr): {'amount': .000, 'g_amount': .00},
		'PST/QST receivable - 9.975% - {}'.format(abbr): {'amount': .000, 'g_amount': .00},
	}
	for item in doc.items:
		if not item.expense_account:
			item.expense_account = expense_account

		if item.cost_center != cost_center:
			item.cost_center = cost_center

		if item.tax:
			filters = {"parent": item.tax}
			fields  = ["charge_type", "account_head", "rate", "tax_type"]
			for tc in frappe.get_list("Sales Taxes and Charges", filters, fields):
				taxes_obj[tc.account_head].update({
					"amount": (flt(item.amount) * flt(tc.rate) / 100.0) + flt(taxes_obj[tc.account_head]["amount"]),
					"g_amount": (flt(item.gprice) * flt(tc.rate) / 100.0) + flt(taxes_obj[tc.account_head]["g_amount"]),
					"tax_type": tc.tax_type
				})

	for account_head, v in taxes_obj.items():
		if not v["amount"]:
			continue
		doc.append("taxes", {
			"charge_type": "Actual",
			"account_head": account_head,
			"tax_type": v["tax_type"],
			"description": account_head,
			"tax_amount": v["amount"],
			"g_tax": v["g_amount"]
		})
	doc.calculate_taxes_and_totals()
	calculate_g_taxes_and_totals(doc)
	doc.total_g_taxes_and_charges = sum([x.g_tax for x in doc.taxes])


def on_update_after_submit(doc, event):
	if has_commission_invoice(doc.name):
		inv = frappe.get_doc("Purchase Invoice", {"bill_no": doc.name})
		frappe.msgprint("""This invoice already has commision invoice 
			<b><a href='/Form/Purchase Invoice/{0}'>{0}</a></b>""".format(inv)
		)
	else:
		create_comission_invoice(doc)

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
	create_delivery_checklist(doc)

def on_cancel(doc, event):
	if has_commission_invoice(doc.name):
		pinv = frappe.get_doc("Purchase Invoice", {"bill_no": doc.name})
		if pinv.docstatus == 1 and pinv.paid_amount == 0:
			pinv.cancel()
			
		else:
			frappe.throw("""
				You cannot cancel this invoice because it has a commission invoice associated <b>
				<a href='/desk#Form/Purchase Invoice/{name}'>{name}</a></b>.<br>
				and has payments, 
			""".format(**pinv.as_dict()))

@frappe.whitelist()
def has_commission_invoice(sinv_name):
	return frappe.db.exists("Purchase Invoice", {"bill_no": sinv_name})

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
	# For some reason ERPNext decides to clear in_words and base_in_words field
	# and not setting them back, let's do it manually
	doc.set_total_in_words()
	doc.commission_invoice = pinv.name
	doc.db_update()

	frappe.msgprint("""
		A Commission invoice has been created for Sales Partner <b>{}</b><br>
		<b><a href='/desk#Form/Purchase Invoice/{}'>{}</a></b>
	""".format(doc.sales_partner, pinv.name, pinv.name))

def create_delivery_checklist(doc):
	if doc.invoice_type != "Vehicles":
		return
	for row in doc.items:
		if row.item_group != "Vehicles":
			continue
		if frappe.db.exists("Delivery Checklist", row.item_code):
			vehicle_release = frappe.get_doc("Delivery Checklist", row.item_code)
			vehicle_release.type = doc.sale_type
		else:
			vehicle_release = frappe.new_doc("Delivery Checklist")
			vehicle_release.update({
				"type": doc.sale_type,
				"vehicle": row.item_code,
			})
		
		vehicle_release.get_items()
		vehicle_release.save(ignore_permissions=True)

def calculate_g_taxes_and_totals(doc):
	last_g_amount = .000
	for row in doc.taxes:
		if row.idx == 1:
			row.g_amount = doc.total_g + row.g_tax
		else:
			row.g_amount = last_g_amount + row.g_tax
		last_g_amount = row.g_amount






