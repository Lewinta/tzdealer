# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

def check(doc, event):
	if not frappe.db.get_value("Customer", doc.customer, "phone_number"):
		frappe.throw("Please set a phone number for {}!".format(doc.customer))
 
def create_or_update_item_price(doc):
	from frappe import db, new_doc, get_doc

	cwdoc = "Item Price"

	selling_gprice_list = db.get_single_value("Selling Settings",
			"selling_gprice_list")

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
