	# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "tzdealer"
app_title = "TZDEALER"
app_publisher = "TZCODE SRL"
app_description = "A Car Dealer Management App"
app_icon = "fa fa-car"
app_color = "#4aa3df"
app_email = "lewinvillar@tzcode.tech"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/tzdealer/css/tzdealer.css"
# app_include_js = "/assets/tzdealer/js/tzdealer.js"

# include js, css files in header of web template
# web_include_css = "/assets/tzdealer/css/tzdealer.css"
# web_include_js = "/assets/tzdealer/js/tzdealer.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_list_js = {
	"Item" : "public/js/item_list.js"
}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
doctype_js = {
	"Item" : "public/js/item.js",
	"Warehouse" : "public/js/warehouse.js",
	"Payment Entry" : "public/js/payment_entry.js",
	"Purchase Invoice" : "public/js/purchase_invoice.js",
	"Sales Invoice" : "public/js/sales_invoice.js",
	"Journal Entry" : "public/js/journal_entry.js",
	"Sales Order" : "public/js/sales_order.js",
	"Contact" : "public/js/contact.js",
	"Landed Cost Voucher" : "public/js/landed_cost_voucher.js",
	"Address" : "public/js/address.js",
}

# Fixtures
# ----------

fixtures = [
	{
		"doctype": "Custom Field",
		"filters": {
			"name": (
				"in", (
					"Warehouse-default",
					"Warehouse-cb_5",
					"Item-section_break_7",
					"Journal Entry-transaction_type",
					"Item-website_post_cb1",
					"Item-eta",
					"Item-website_post",
					"Item-website_post_2",
					"Item-auto_trader_post",
					"Item-kijiji_post",
					"Item-website_postings",
					"Payment Entry Reference-items",
					"Payment Entry Reference-items_sb",
					"Payment Entry-date",
					"Purchase Invoice-trans_type",
					"Sales Invoice-trans_type",
					"Purchase Invoice-trans_group",
					"Purchase Invoice-date",
					"Landed Cost Taxes and Charges-transaction_type",
					"Sales Invoice-date",
					"Sales Order-date",
					"Sales Invoice Item-vim_number",
					"Landed Cost Taxes and Charges-exchange_rate",
					"Landed Cost Taxes and Charges-currency",
					"Landed Cost Taxes and Charges-supplier_invoice_type",
					"Purchase Invoice-supplier_invoice_type",
					"Customer-phone_number",
					"Supplier-phone_number",
					"Item-loading_supplier_price",
					"Item-loading_supplier",
					"Item-column_break_19",
					"Item-trucking_supplier_price",
					"Item-trucking_supplier",
					"Item-column_break_16",
					"Item-booking_supplier_price",
					"Item-suppliers",
					"Landed Cost Taxes and Charges-transaction_group",
					"Landed Cost Taxes and Charges-date",
					"Supplier-company",
					"Customer-company",
					"Customer-column_break_1",
					"Item-company",
					"Item-last_sold_price",
					"Landed Cost Taxes and Charges-supplier_invoice",
					"Landed Cost Taxes and Charges-totals",
					"Landed Cost Taxes and Charges-vendor",
					"Landed Cost Taxes and Charges-invoice",
					"Landed Cost Taxes and Charges-description_sb",
					"Landed Cost Taxes and Charges-create_invoice",
					"Item-salvage_title",
					"Item-item_number",
					"Item-_default_supplier",
					"Item-purchase_date",
					"Company-tvq",
					"Company-tps",
					"Address-full_address",
					"Sales Invoice-grand_g_total",
					"Sales Invoice-total_g_taxes_and_charges",
					"Sales Invoice-column_break_78",
					"Sales Taxes and Charges-g_amount",
					"Sales Taxes and Charges-column_break_17",
					"Sales Taxes and Charges-g_tax",
					"Sales Invoice-column_break_64",
					"Sales Invoice-total_g",
					"Item-notified_party",
					"Item-consignee",
					"Item-shipper",
					"Sales Order Item-gprice",
					"Selling Settings-selling_gprice_list",
					"Sales Invoice Item-gprice",
					"Item-item_description",
					"Item-item_descriptions",
					"Item-destination",
					"Payment Entry-_reference_no",
					"Contact-contact_type",
					"Contact-create_user",
					"Item-shipping_line",
					"Item-booking_no",
					"Item-seal_no",
					"Item-container_no",
					"Sales Invoice-account",
					"Sales Invoice-transaction_group",
					"Sales Invoice-invoice_type",
					"Purchase Invoice-account",
					"Purchase Invoice-transaction_group",
					"Item-mk",
					"Item-trim",
					"Item-bl",
					"Item-column_break_43",
					"Item-column_break_31",
					"Item-column_break_25",
					"Item-seat_type",
					"Item-power_steering",
					"Item-power_seats",
					"Item-power_brakes_",
					"Item-power_mirrors",
					"Item-power_locks",
					"Item-power_window",
					"Item-column_break_46",
					"Item-gps",
					"Item-rear_window_defroster",
					"Item-child_seat_anchors",
					"Item-cruise_control",
					"Item-side_curtain_airbag",
					"Item-tinted_glass",
					"Item-telescope_wheel_",
					"Item-back_camera",
					"Item-air_conditioner",
					"Item-column_break_36",
					"Item-structural_damange",
					"Item-driveable",
					"Item-optional_details",
					"Item-wheel_type",
					"Item-seat_no",
					"Item-wheels",
					"Item-odors",
					"Item-odometer_value",
					"Item-top_style",
					"Item-doors",
					"Item-engine_size",
					"Item-engine",
					"Item-drive_train",
					"Item-gear",
					"Item-fuel_type",
					"Item-more_details",
					"Item-title_status",
					"Item-part_type",
					"Item-part",
					"Item-part_group",
					"Item-column_break_6",
					"Item-parts_detail",
					"Item-section_break_12",
					"Item-column_break_7",
					"Item-interior_color",
					"Item-body_type",
					"Purchase Invoice Item-charges",
					"Item-item_type",
					"Item-model",
					"Landed Cost Taxes and Charges-tax_rate",
					"Landed Cost Taxes and Charges-tax",
					"Landed Cost Taxes and Charges-total",
					"Landed Cost Taxes and Charges-column_break_7",
					"Item-status",
					"Item-column_break_2",
					"Purchase Invoice-seal_no",
					"Purchase Invoice-container_no",
					"Purchase Invoice-invoice_type",
					"Item-vim_number",
					"Item-exterior_color",
					"Item-year",
					"Item-make",
					"Sales Partner-company",
					"Sales Partner-tax_id",
					"Sales Partner-phone_number",
				)
			)
		}
	},{
		"doctype": "Print Format",
		"filters": {
			"name": (
				"in", (
					"Sales G Invoice",
					"Sales Invoice",
					"Container Detail",
					"Wholesale Contract",
					"Pick up Form",
					"Pickup Vehicle",
					"POS Invoice",
					"GST POS Invoice",
					"Detailed Tax Invoice",
					"Tax Invoice",
					"GST Tax Invoice",
					"Simplified Tax Invoice",
				)
			)
		}
	},
]

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "tzdealer.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "tzdealer.install.before_install"
# after_install = "tzdealer.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "tzdealer.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Item": {
		"before_insert": "tzdealer.hook.item.before_insert",
		"validate": "tzdealer.hook.item.validate",
	},
	"Sales Invoice": {
		"validate": "tzdealer.hook.sales_invoice.validate",
		"on_submit": "tzdealer.hook.sales_invoice.on_submit",
		"on_cancel": "tzdealer.hook.sales_invoice.on_cancel",
	},
	"Sales Order": {
		"validate": "tzdealer.hook.sales_order.check", 
	},
	"Landed Cost Voucher": {
		"on_submit": "tzdealer.hook.landed_cost_voucher.on_submit",
		"on_cancel": "tzdealer.hook.landed_cost_voucher.on_cancel",
		"on_trash": "tzdealer.hook.landed_cost_voucher.on_trash",
	},
	"Purchase Invoice":{
		"validate": "tzdealer.hook.purchase_invoice.validate",
		"on_cancel": "tzdealer.hook.purchase_invoice.on_cancel",
	},
	"Journal Entry":{
		"validate": "tzdealer.hook.journal_entry.validate",
	},
	"Warehouse":{
		"validate": "tzdealer.hook.warehouse.validate",
	},
	"Sales Partner":{
		"after_insert": "tzdealer.hook.sales_partner.after_insert",
	}	
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"tzdealer.tasks.all"
# 	],
# 	"daily": [
# 		"tzdealer.tasks.daily"
# 	],
# 	"hourly": [
# 		"tzdealer.tasks.hourly"
# 	],
# 	"weekly": [
# 		"tzdealer.tasks.weekly"
# 	]
# 	"monthly": [
# 		"tzdealer.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "tzdealer.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "tzdealer.event.get_events"
# }
boot_session = "tzdealer.boot.boot_session"
