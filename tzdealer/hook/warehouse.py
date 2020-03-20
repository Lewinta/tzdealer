import frappe

def validate(doc, event):
	if not doc.default:
		return
	if exists_default_warehouse(doc):
		frappe.throw("""There is a already a default warehouse for <b>{}</b>!""".format(doc.company))



def exists_default_warehouse(doc):
	return frappe.db.sql("""
		SELECT 
			COUNT(1) as qty
		FROM 
			`tabWarehouse`
		WHERE
			`tabWarehouse`.company = %s
		AND
			`tabWarehouse`.default = 1
	""", doc.company)[0][0]


