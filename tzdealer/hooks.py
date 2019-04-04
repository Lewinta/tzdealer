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
	"Payment Entry" : "public/js/payment_entry.js",
	"Purchase Invoice" : "public/js/purchase_invoice.js",
	"Sales Invoice" : "public/js/sales_invoice.js",
	"Contact" : "public/js/contact.js",
	"Landed Cost Voucher" : "public/js/landed_cost_voucher.js",
	"Address" : "public/js/address.js",
}
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
	},
	"Sales Invoice": {
		"validate": "tzdealer.hook.sales_invoice.validate",
	},
	"Sales Order": {
		"validate": "tzdealer.hook.sales_order.validate",
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
