import frappe

@frappe.whitelist()
def get_container_vims(item_code, company):
	result = frappe.db.sql("""
		SELECT
			CONCAT(
				`tabItem Description`.vim_number,     '-',
				`tabItem Description`.make,          ' ',
				`tabItem Description`.model,         ' ',
				`tabItem Description`.exterior_color,' ',
				`tabItem Description`.year
			) as item_code
		FROM 
			`tabItem Description`
		JOIN 
		 	`tabItem`
		ON
			`tabItem Description`.parent = `tabItem`.item_code
		WHERE 
			`tabItem`.item_code = '{parent}'
		AND
			`tabItem`.company = '{company}'

	""".format(parent=item_code, company=company), as_dict=True)

	if not result:
		return ""

	return "\n".join([v.item_code for v in result])

@frappe.whitelist()
def post_image(item_code):
	wc = frappe.get_single("Website Connector")
	wc.sync_images(item_code)

@frappe.whitelist()
def post_media(web_img):
	wc = frappe.get_single("Website Connector")
	return wc.sync_single_image(web_img)
