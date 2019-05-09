# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

def validate(doc, event):
	pass
	# for d in doc.items:
	# 	create_or_update_item_price(d)
def on_submit(doc, event):
	# When submitting an invoice we need to update the last sold price
	# to each Item.

	for item in doc.items:
		if not item.item_code or not frappe.db.exists("Item", item.item_code):
			continue
		
		doc = frappe.get_doc("Item", item.item_code)
		doc.last_sold_price = item.rate
		doc.db_update()

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
