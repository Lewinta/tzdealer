import frappe

def validate(doc, event):
	if not doc.cheque_date:
		doc.cheque_date = doc.posting_date

