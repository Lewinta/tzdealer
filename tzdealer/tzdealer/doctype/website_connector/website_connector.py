# -*- coding: utf-8 -*-
# Copyright (c) 2020, TZCODE SRL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests 
import json
import traceback
from tzdealer.hook.item import cast_to_post, cast_image
from frappe.utils import nowdate

class WebsiteConnector(Document):
	def validate(self):
		self.check_token()

	def check_token(self):
		if not self.token:
			self.get_token()
		else:
			url = "{}/{}".format(self.website_url, "wp-json/jwt-auth/v1/token/validate") 
			headers = self.headers({'Authorization': "Bearer {}".format(self.token)})
			r = requests.request("POST", url, headers=headers)
			text = frappe._dict(json.loads(r.text))
			frappe.errprint("Text: {}\n\n".format(text))
			if r.status_code == 200:
				if text.code == "jwt_auth_valid_token":
					frappe.errprint("Valid Token")
					return
				else:
					frappe.errprint("# Token Invalid, Lets get a new one")
					self.get_token()
			elif r.status_code == 403:
				# Token Expired, Let's get a new one
				frappe.errprint("# Token Expired, Lets get a new one")
				self.get_token()
			else:
				frappe.throw("<b>Error {}</b> {} <br>{}<br>{}".format(r.status_code, url, headers, r.text))	
			
	def get_token(self):
		data = json.dumps({
			"username": self.username,
			"password": self.get_password()
		})
		headers = {
			'Content-Type': "application/json",
			'cache-control': "no-cache"
		}
		url = "{}/{}".format(self.website_url, "wp-json/jwt-auth/v1/token")
		r = requests.request("POST", url, data=data, headers=headers)
		text = frappe._dict(json.loads(r.text))
		if r.status_code == 200 :
			self.token = text.token
			frappe.errprint("# New Token Generated")
			self.last_update = nowdate()
		else:
			frappe.throw("<b>Error {}</b> {} <br>{}<br>{}".format(r.status_code, url, headers, r.text))	
	def send(self, sufix, headers, data=None):
		self.check_token()
		url = "{}/{}".format(self.website_url, sufix)

		frappe.errprint("POST {}\ndata:{}\nheaders:{}".format(url, data, headers))
		r = requests.request("POST", url, data=data, headers=headers)
		
		# Expired Token
		frappe.errprint(r.status_code)
		if r.status_code == 403:
			self.get_token()
		if r.status_code in [200, 201]:
			return frappe._dict(json.loads(r.text))
		else:
			frappe.throw("<b>Error {}</b> {} <br>{}<br>{}<br> {}".format(r.status_code, url, self.headers(), data, r.text))	
	
	def headers(self, args=None):
		h = {
			'Content-Type': "application/json",
			'cache-control': "no-cache"
		}
		if args:
			h.update(args)
		return h
	
	def sync(self, item_code):
		url = "/wp-json/wp/v2/vehicles"
		doc = frappe.get_doc("Item", item_code)
		# self.sync_images(doc)
		if not self.last_update or self.last_update < nowdate():
			self.get_token()
		
		if doc.website_id:
			# looks like exists let's update
			url +="/{}".format(doc.website_id)

		try:
			r = self.send(url, self.headers({'Authorization': "Bearer {}".format(self.token)}), cast_to_post(doc))
			if not doc.website_id:
				doc.website_id = r.id
			doc.db_update()
			frappe.db.commit()

		except Exception as e:
			error = frappe.new_doc("Error Log")
			error.update({
				'error': "msg:{}\n\nTraceback:{}".format(
					e.args[0],
					traceback.format_exc()
				),
				'method': "sync",
			})
			error.save(ignore_permissions=True)

	def sync_images(self, item):
		url = "/wp-json/wp/v2/media"
		
		if type(item) == unicode and frappe.db.exists("Item", item):
			item = frappe.get_doc("Item", item)

		for img in item.website_images:
			if img.post_id:
				# looks like exists let's update
				url +="/{}".format(img.post_id)

			try:
				r = self.send(url, self.headers({'Authorization': "Bearer {}".format(self.token)}), cast_to_post(doc))
				img.post_id = r.id
				img.db_update()

			except Exception as e:
				error = frappe.new_doc("Error Log")
				error.update({
					'error': "msg:{}\n\nTraceback:{}".format(
						e.args[0],
						traceback.format_exc()
					),
					'method': "sync",
				})
				error.save(ignore_permissions=True)

	def sync_single_image(self, img_name):
		url = "/wp-json/wp/v2/media"
		
		if not frappe.db.exists("Website Image", img_name):
			frappe.throw("Website Image {} not found".format(img_name))

		web_img = frappe.get_doc("Website Image", img_name)

		if web_img.post_id:
			# looks like exists let's update
			url +="/{}".format(web_img.post_id)

		frappe.errprint("Now let's send it")

		try:
			r = self.send(url, self.headers({'Authorization': "Bearer {}".format(self.token)}), cast_image(web_img))
			web_img.post_id = r.id
			web_img.db_update()

		except Exception as e:
			error = frappe.new_doc("Error Log")
			error.update({
				'error': "msg:{}\n\nTraceback:{}".format(
					e.args[0],
					traceback.format_exc()
				),
				'method': "sync",
			})
			error.save(ignore_permissions=True)
	
	def update_vehicle(self, doc):
		url = "/wp-json/wp/v2/vehicles/{}".format()
		self.check_token()

