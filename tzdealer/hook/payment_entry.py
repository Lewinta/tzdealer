import frappe
import json

@frappe.whitelist()
def render_items(dt, dn):
	tbl = "{} Item".format(dt)
	options = {"tbl":tbl, "parent":dn}
	data = frappe.db.sql("""
		SELECT
			`tab{tbl}`.item_code,
			`tab{tbl}`.item_name,
			`tab{tbl}`.rate,
			COALESCE(`tabItem`.vim_number, '-') as vim_number
		FROM 
			`tab{tbl}`
		LEFT JOIN
			`tabItem`
		ON
			`tab{tbl}`.item_code = `tabItem`.item_code
		WHERE
			`tab{tbl}`.parent = '{parent}'
	""".format(**options), debug=False, as_dict=True)
	_items = {"items" : data}
		
	return frappe.render_template("tzdealer/hook/purchase_invoice_items.html", _items)

