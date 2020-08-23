# -*- coding: utf-8 -*-
# Copyright (c) 2020, TZCODE SRL and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests 
import json

class WebsiteConnector(Document):
	def validate(self):
		self.check_token()

	def check_token(self):
		if not self.token:
			self.get_token()
		else:
			headers = self.headers({'Authorization': "Bearer {}".format(self.token)})
			
			r = self.send("index.php/wp-json/jwt-auth/v1/token/validate", headers)

			if r.code != "jwt_auth_valid_token":
				self.get_token()
			
	def get_token(self):
		data = json.dumps({
			"username": self.username,
			"password": self.get_password()
		})

		r = self.send("index.php/wp-json/jwt-auth/v1/token", self.headers(), data)
		self.token = r.token
	
	def send(self, sufix, headers, data=None):
		url = "{}/{}".format(self.website_url, sufix)

		# frappe.errprint("POST {}\ndata:{}\nheaders:{}".format(url, data, headers))
		r = requests.request("POST", url, data=data, headers=headers)
		
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
	
	def sync(self, data, item_code, website_id=None):
		url = "index.php/wp-json/wp/v2/vehicles"
		self.check_token()
		
		if website_id:
			# looks like exists let's update
			url +="/{}".format(website_id)

		r = self.send(url, self.headers({'Authorization': "Bearer {}".format(self.token)}), data)
		
		item = frappe.get_doc("Item", item_code)
		item.website_id = r.id
		item.db_update()
	
	def update_vehicle(self, doc):
		url = "index.php/wp-json/wp/v2/vehicles/{}".format()
		self.check_token()
