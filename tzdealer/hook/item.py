import frappe
from frappe.model.naming import make_autoname
import json 
import requests
from frappe.utils import flt
from datetime import datetime
from frappe.utils.background_jobs import enqueue

def before_insert(doc, event):
	if doc.item_type == "Vehicle Parts" and  not doc.item_code:
		doc.item_code = make_autoname("PART-.########") 

	if doc.item_type == "Containers" and  not doc.item_code:
		doc.item_code = make_autoname("CONT-.########") 

	if doc.item_type == "Vehicles":
		doc.item_code = make_autoname("VEH-.########") 

	if doc.item_type == "Services" and  not doc.item_code:
		doc.item_code = make_autoname("SER-.########")
	
	if doc.item_type == "Third Party Services" and  not doc.item_code:
		doc.item_code = make_autoname("SER-.########") 

	if doc.item_type == "Vehicles":
		doc.item_number = frappe.db.sql("""
			SELECT 
				MAX(item_number)
			FROM 
				`tabItem`
		""")[0][0]
def validate(doc, event):
	generate_description(doc, event)
	update_exterior_color(doc)

@frappe.whitelist()
def post_to_website(docname):
	doc = frappe.get_doc("Item", docname)
	if doc.item_type != "Vehicles" or not doc.website_post:
		return
	wc = frappe.get_single("Website Connector")
	wc.sync(doc.item_code)
	# enqueue(post_to_website, docname=doc.name)



def generate_description(doc, event):
	desc = """<b>MAKE:&nbsp;</b>{make}<br>
			  <b>MODEL:&nbsp;</b>{model}<br>
			  <b>YEAR:&nbsp;</b>{year}<br>
			  <b>COLOR:&nbsp;</b>{exterior_color}<br>"""
	if doc.item_type == "Vehicles":
		doc.description = desc.format(**doc.as_dict())

def update_exterior_color(doc):
	# This will make sure Item Description has it's exterior color
	if doc.item_type != "Vehicles" or not doc.exterior_color:
		return
	
	vehicles_without_color = frappe.get_list(
		"Item Description",
		{
			"item_code": doc.item_code,
			"exterior_color":''
		},
		as_list=True
	)
	for name, in vehicles_without_color:
		item = frappe.get_doc("Item Description", name)
		item.exterior_color = doc.exterior_color
		item.db_update()

def get_sales_price(item_code):
	revenue_rate   = frappe.db.get_single_value("Configuration", "default_revenue_rate") or .000
	valuation_rate = frappe.db.get_value("Bin", {"item_code":item_code}, "valuation_rate") or .000
	return flt(valuation_rate) * ((flt(revenue_rate) / 100) + 1)


def cast_to_post(doc):
	return json.dumps({
	# _auto_color_int
	"title": "{}-{}".format(doc.item_name.split("-")[0], int(doc.name.split("-")[1])),
	"content": doc.item_name.split("-")[0],
	"status": "draft",
	"type": "pixad-autos",
	"_auto_condition": "Used",
	"_custom_1": int(doc.name.split("-")[1]),
	"_auto_doors": doc.doors,
	"_auto_color": doc.exterior_color,
	"_auto_engine": doc.engine,
	"_auto_fuel": doc.fuel_type.lower(),
	"_auto_make": doc.make,
	"_auto_mileage": doc.odometer_value,
	"_auto_price": get_sales_price(doc.item_code),
	"_auto_sale_price": get_sales_price(doc.item_code),
	"_auto_seats": doc.seat_no,
	"_auto_transmission": doc.gear,
	"_auto_vin": doc.vim_number,
	"_auto_year": doc.year,
	"terms": {
		"model": [ doc.make, doc.model ]
	},
})

def cast_image(web_img):
	if not web_img.get("doctype") or web_img.get("doctype") != "Website Image":
		frappe.throw("You must send a Website Image Doctype, received {}".format(type(web_img)))

	dt = str(datetime.now())[:19]

	return json.dumps({
	"date": dt,
    "date_gmt": dt,
    "status": "future",
    "title": web_img.parent.split("-")[0],
    "description": web_img.parent.split("-")[0],
    "media_type": "image",
    "source_url": web_img.image,
    "source_url": web_img.image,
    "Content-Disposition": {"filename":web_img.image},

})
	
@frappe.whitelist()
def address_by_supplier(doctype, txt, searchfield, start, page_len, filters):

	if not filters.get("supplier"): 
		return []

	result = frappe.db.sql("""
		SELECT
			`tabAddress`.name,
			`tabAddress`.address_title,
			`tabDynamic Link`.link_name
		FROM
			`tabDynamic Link`
		JOIN
			`tabAddress`
		ON
			`tabAddress`.name =	`tabDynamic Link`.parent
		WHERE
			`tabDynamic Link`.link_doctype = 'Supplier'
		AND
			`tabDynamic Link`.link_name = '{1}'
		AND
			`tabAddress`.address_title LIKE '%{0}%'
		ORDER BY 
			`tabAddress`.address_title LIMIT 20
	""".format("%".join(txt.split()), filters.get("supplier")), as_dict=True)
	
	return [[row.name, "{1} - {0}".format(row.address_title, row.link_name)] for row in result]
