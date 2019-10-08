import frappe
from frappe.model.naming import make_autoname

def before_insert(doc, event):
	if doc.item_type == "Vehicle Parts" and  not doc.item_code:
		doc.item_code = make_autoname("PART-") 

	if doc.item_type == "Containers" and  not doc.item_code:
		doc.item_code = make_autoname("CONT-") 

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

