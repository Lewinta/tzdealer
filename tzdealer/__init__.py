# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
__version__ = '0.0.1'


def get_payments(doc):
   filters = {
      "reference_doctype": doc.get("doctype") or doc.get("parenttype"),
      "reference_name": doc.get("name") or doc.get("parent")
   }
   return frappe.get_all("Payment Entry Reference", filters, ["parenttype", "parent"], group_by="parent")

def get_lcv(doc):
   filters = {
      "receipt_document_type": doc.get("doctype"),
      "receipt_document": doc.get("name")
   }
   return frappe.get_all("Landed Cost Purchase Receipt", filters, ["parenttype", "parent"], group_by="parent")


def delete_doc(d, parent=True):
   dt = "parenttype" if parent else "doctype"
   dn = "parent" if parent else "name"

   if not frappe.db.exists(d.get(dt), d.get(dn)):
      # print("\tNot Found {} {}".format(d.get(dt), d.get(dn)))
      return

   doc = frappe.get_doc(d.get(dt), d.get(dn))
   print("\tDeleting {} {}".format(d.get(dt), d.get(dn)))
   
   if doc.docstatus == 1:
      doc.cancel()

   doc.delete()

def get_sold_vehicles(doc):
   # Let's get the vehicles sold
   items = [r.item_code for r in filter( lambda x: x.item_code != 'fee', doc.items)]
   return frappe.get_list(
      "Sales Invoice Item",
      {"item_code":["in", ",".join(items)]},
      ["parenttype", "parent"],
      group_by="parent" 
   )

def check_linked(doc, method="Delete"):
   from frappe.model.dynamic_links import get_dynamic_link_map
   '''Raise `frappe.LinkExistsError` if the document is dynamically linked'''
   for df in get_dynamic_link_map().get(doc.doctype, []):
      if df.parent in ("Communication", "ToDo", "DocShare", "Email Unsubscribe", "Activity Log", 'File', 'Version'):
         # don't check for communication and todo!
         continue

      meta = frappe.get_meta(df.parent)
      if meta.issingle:
         # dynamic link in single doc
         refdoc = frappe.db.get_singles_dict(df.parent)
         if (refdoc.get(df.options)==doc.doctype
            and refdoc.get(df.fieldname)==doc.name
            and ((method=="Delete" and refdoc.docstatus < 2)
               or (method=="Cancel" and refdoc.docstatus==1))
            ):
            # raise exception only if
            # linked to an non-cancelled doc when deleting
            # or linked to a submitted doc when cancelling
            raise_link_exists_exception(doc, df.parent, df.parent)
      else:
         # dynamic link in table
         df["table"] = ", parent, parenttype, idx" if meta.istable else ""
         for refdoc in frappe.db.sql("""select name, docstatus{table} from `tab{parent}` where
            {options}=%s and {fieldname}=%s""".format(**df), (doc.doctype, doc.name), as_dict=True):

            if ((method=="Delete" and refdoc.docstatus < 2) or (method=="Cancel" and refdoc.docstatus==1)):
               # raise exception only if
               # linked to an non-cancelled doc when deleting
               # or linked to a submitted doc when cancelling

               reference_doctype = refdoc.parenttype if meta.istable else df.parent
               reference_docname = refdoc.parent if meta.istable else refdoc.name
               at_position = "at Row: {0}".format(refdoc.idx) if meta.istable else ""

               return {"dt":reference_doctype, "dn":reference_docname}

documents = [
   {"doctype": "Sales Invoice", "name":"SINV-00592"},
   {"doctype": "Sales Invoice", "name":"SINV-01233"},
   {"doctype": "Sales Invoice", "name":"SINV-00969"},
   {"doctype": "Sales Invoice", "name":"SINV-01085"},
   {"doctype": "Sales Invoice", "name":"SINV-00859-2"},
   {"doctype": "Sales Invoice", "name":"SINV-00858-2"},
   {"doctype": "Sales Invoice", "name":"SINV-00857-2"},
   {"doctype": "Sales Invoice", "name":"SINV-00856-2"},
   {"doctype": "Sales Invoice", "name":"SINV-00855-2"},
   {"doctype": "Sales Invoice", "name":"SINV-00854-4"},
   {"doctype": "Sales Invoice", "name":"SINV-00853-2"},
   {"doctype": "Sales Invoice", "name":"SINV-00852-3"},
   {"doctype": "Sales Invoice", "name":"SINV-00851-2"},
   {"doctype": "Sales Invoice", "name":"SINV-00850-2"},
   {"doctype": "Sales Invoice", "name":"SINV-00849-2"},
   {"doctype": "Sales Invoice", "name":"SINV-00848-2"},
   {"doctype": "Sales Invoice", "name":"SINV-00847-2"},
   {"doctype": "Sales Invoice", "name":"SINV-00846-2"},
   {"doctype": "Sales Invoice", "name":"SINV-00845-4"},
   {"doctype": "Sales Invoice", "name":"SINV-01002-1"},
   {"doctype": "Sales Invoice", "name":"SINV-00997"},
   {"doctype": "Sales Invoice", "name":"SINV-00890"},
   {"doctype": "Sales Invoice", "name":"SINV-00951-1"},
   {"doctype": "Sales Invoice", "name":"SINV-00956"},
   {"doctype": "Sales Invoice", "name":"SINV-00955"},
   {"doctype": "Sales Invoice", "name":"SINV-00954"},
   {"doctype": "Sales Invoice", "name":"SINV-00953"},
   {"doctype": "Sales Invoice", "name":"SINV-00952"},
   {"doctype": "Sales Invoice", "name":"SINV-00662-1"},
   {"doctype": "Sales Invoice", "name":"SINV-00844"},
   {"doctype": "Sales Invoice", "name":"SINV-00136"},
   {"doctype": "Sales Invoice", "name":"SINV-00744"},
   {"doctype": "Sales Invoice", "name":"SINV-00743"},
   {"doctype": "Sales Invoice", "name":"SINV-00579"},
   {"doctype": "Sales Invoice", "name":"SINV-00562"},
   {"doctype": "Sales Invoice", "name":"SINV-00603"},
   {"doctype": "Sales Invoice", "name":"SINV-00602"},
   {"doctype": "Sales Invoice", "name":"SINV-00601"},
   {"doctype": "Sales Invoice", "name":"SINV-00600"},
   {"doctype": "Sales Invoice", "name":"SINV-00006-2"},
   {"doctype": "Sales Invoice", "name":"SINV-00046-1"},
   {"doctype": "Sales Invoice", "name":"SINV-00060-1"},
   {"doctype": "Sales Invoice", "name":"SINV-00138-1"},
   {"doctype": "Sales Invoice", "name":"SINV-00160-1"},
   {"doctype": "Sales Invoice", "name":"SINV-00599"},
   {"doctype": "Sales Invoice", "name":"SINV-00598"},
   {"doctype": "Sales Invoice", "name":"SINV-00596"},
   {"doctype": "Sales Invoice", "name":"SINV-00595"},
   {"doctype": "Sales Invoice", "name":"SINV-00594"},
   {"doctype": "Sales Invoice", "name":"SINV-00588"},
   {"doctype": "Sales Invoice", "name":"SINV-00580"},
   {"doctype": "Sales Invoice", "name":"SINV-00573"},
   {"doctype": "Sales Invoice", "name":"SINV-00565"},
   {"doctype": "Sales Invoice", "name":"SINV-00558"},
   {"doctype": "Sales Invoice", "name":"SINV-00590"},
   {"doctype": "Sales Invoice", "name":"SINV-00302-1"},
   {"doctype": "Sales Invoice", "name":"SINV-00442-1"},
   {"doctype": "Sales Invoice", "name":"SINV-00744"},
   {"doctype": "Sales Invoice", "name":"SINV-00743"},
   {"doctype": "Sales Invoice", "name":"SINV-00603"},
   {"doctype": "Sales Invoice", "name":"SINV-00602"},
   {"doctype": "Sales Invoice", "name":"SINV-00601"},
   {"doctype": "Sales Invoice", "name":"SINV-00600"},
   {"doctype": "Sales Invoice", "name":"SINV-00006-2"},
   {"doctype": "Sales Invoice", "name":"SINV-00046-1"},
   {"doctype": "Sales Invoice", "name":"SINV-00060-1"},
   {"doctype": "Sales Invoice", "name":"SINV-00138-1"},
   {"doctype": "Sales Invoice", "name":"SINV-00160-1"},
   {"doctype": "Sales Invoice", "name":"SINV-00599"},
   {"doctype": "Sales Invoice", "name":"SINV-00598"},
   {"doctype": "Sales Invoice", "name":"SINV-00596"},
   {"doctype": "Sales Invoice", "name":"SINV-00595"},
   {"doctype": "Sales Invoice", "name":"SINV-00594"},
   {"doctype": "Sales Invoice", "name":"SINV-00302-1"},
   {"doctype": "Sales Invoice", "name":"SINV-00442-1"},
   {"doctype": "Sales Invoice", "name":"SINV-01029"},
   {"doctype": "Sales Invoice", "name":"SINV-00420"},
   {"doctype": "Sales Invoice", "name":"SINV-00418"},
   {"doctype": "Sales Invoice", "name":"SINV-00889-2"},
   {"doctype": "Sales Invoice", "name":"SINV-00604"},
   {"doctype": "Sales Invoice", "name":"SINV-00006-1"},
   {"doctype": "Sales Invoice", "name":"SINV-00046"},
   {"doctype": "Sales Invoice", "name":"SINV-00060"},
   {"doctype": "Sales Invoice", "name":"SINV-00138"},
   {"doctype": "Sales Invoice", "name":"SINV-00160"},
   {"doctype": "Sales Invoice", "name":"SINV-00302"},
   {"doctype": "Sales Invoice", "name":"SINV-00442"},
   {"doctype": "Purchase Invoice", "name":"PINV-00670"},
   {"doctype": "Purchase Invoice", "name":"PINV-00672"},
   {"doctype": "Purchase Invoice", "name":"PINV-00674"},
   {"doctype": "Purchase Invoice", "name":"PINV-00676"},
   {"doctype": "Purchase Invoice", "name":"PINV-00678"},
   {"doctype": "Purchase Invoice", "name":"PINV-00680"},
   {"doctype": "Purchase Invoice", "name":"PINV-00682"},
   {"doctype": "Purchase Invoice", "name":"PINV-00684"},
   {"doctype": "Purchase Invoice", "name":"PINV-00686"},
   {"doctype": "Purchase Invoice", "name":"PINV-00688"},
   {"doctype": "Purchase Invoice", "name":"PINV-00690"},
   {"doctype": "Purchase Invoice", "name":"PINV-00692"},
   {"doctype": "Purchase Invoice", "name":"PINV-00694"},
   {"doctype": "Purchase Invoice", "name":"PINV-00698"},
   {"doctype": "Purchase Invoice", "name":"PINV-00700"},
   {"doctype": "Purchase Invoice", "name":"PINV-00702"},
   {"doctype": "Purchase Invoice", "name":"PINV-00704"},
   {"doctype": "Purchase Invoice", "name":"PINV-00706"},
   {"doctype": "Purchase Invoice", "name":"PINV-00708"},
   {"doctype": "Purchase Invoice", "name":"PINV-00710"},
   {"doctype": "Purchase Invoice", "name":"PINV-00712"},
   {"doctype": "Purchase Invoice", "name":"PINV-00714"},
   {"doctype": "Purchase Invoice", "name":"PINV-00716"},
   {"doctype": "Purchase Invoice", "name":"PINV-00718"},
   {"doctype": "Purchase Invoice", "name":"PINV-00720"},
   {"doctype": "Purchase Invoice", "name":"PINV-00722"},
   {"doctype": "Purchase Invoice", "name":"PINV-00724"},
   {"doctype": "Purchase Invoice", "name":"PINV-00726"},
   {"doctype": "Purchase Invoice", "name":"PINV-00728"},
   {"doctype": "Purchase Invoice", "name":"PINV-00730"},
   {"doctype": "Purchase Invoice", "name":"PINV-00732"},
   {"doctype": "Purchase Invoice", "name":"PINV-00734"},
   {"doctype": "Purchase Invoice", "name":"PINV-00736"},
   {"doctype": "Purchase Invoice", "name":"PINV-00738"},
   {"doctype": "Purchase Invoice", "name":"PINV-00740"},
   {"doctype": "Purchase Invoice", "name":"PINV-00742"},
   {"doctype": "Purchase Invoice", "name":"PINV-00744"},
   {"doctype": "Purchase Invoice", "name":"PINV-00746"},
   {"doctype": "Purchase Invoice", "name":"PINV-00748"},
   {"doctype": "Purchase Invoice", "name":"PINV-00750"},
   {"doctype": "Purchase Invoice", "name":"PINV-00752"},
   {"doctype": "Purchase Invoice", "name":"PINV-00754"},
   {"doctype": "Purchase Invoice", "name":"PINV-00950"},
   {"doctype": "Purchase Invoice", "name":"PINV-01074"},
   {"doctype": "Purchase Invoice", "name":"PINV-01075"},
   {"doctype": "Purchase Invoice", "name":"PINV-01076"},
   {"doctype": "Purchase Invoice", "name":"PINV-01264"},
   {"doctype": "Purchase Invoice", "name":"PINV-01265"},
   {"doctype": "Purchase Invoice", "name":"PINV-01266"},
   {"doctype": "Purchase Invoice", "name":"PINV-01424"},
   {"doctype": "Purchase Invoice", "name":"PINV-01449"},
   {"doctype": "Purchase Invoice", "name":"PINV-01452"},
   {"doctype": "Purchase Invoice", "name":"PINV-01453"},
   {"doctype": "Purchase Invoice", "name":"PINV-01495"},
   {"doctype": "Purchase Invoice", "name":"PINV-01496"},
   {"doctype": "Purchase Invoice", "name":"PINV-01497"},
   {"doctype": "Purchase Invoice", "name":"PINV-01498"},
   {"doctype": "Purchase Invoice", "name":"PINV-01499"},
   {"doctype": "Purchase Invoice", "name":"PINV-01827"},
   {"doctype": "Purchase Invoice", "name":"PINV-02110"},
   {"doctype": "Purchase Invoice", "name":"PINV-02111"},
   {"doctype": "Purchase Invoice", "name":"PINV-02112"},
   {"doctype": "Purchase Invoice", "name":"PINV-02158"},
   {"doctype": "Purchase Invoice", "name":"PINV-02485"},
   {"doctype": "Purchase Invoice", "name":"PINV-02486"},
   {"doctype": "Purchase Invoice", "name":"PINV-02524"},
   {"doctype": "Purchase Invoice", "name":"PINV-02525"},
   {"doctype": "Purchase Invoice", "name":"PINV-02572"},
   {"doctype": "Purchase Invoice", "name":"PINV-02585"},
   {"doctype": "Purchase Invoice", "name":"PINV-02586"},
   {"doctype": "Purchase Invoice", "name":"PINV-02592"},
   {"doctype": "Purchase Invoice", "name":"PINV-02647"},
   {"doctype": "Purchase Invoice", "name":"PINV-02648"},
   {"doctype": "Purchase Invoice", "name":"PINV-02649"},
   {"doctype": "Purchase Invoice", "name":"PINV-02650"},
   {"doctype": "Purchase Invoice", "name":"PINV-00696-1"},
   {"doctype": "Purchase Invoice", "name":"PINV-00757-1"},
   {"doctype": "Purchase Invoice", "name":"PINV-00802-1"},
   {"doctype": "Purchase Invoice", "name":"PINV-00949-1"},
   {"doctype": "Purchase Invoice", "name":"PINV-00951-1"},
   {"doctype": "Purchase Invoice", "name":"PINV-01073-1"},
   {"doctype": "Purchase Invoice", "name":"PINV-01420-1"},
   {"doctype": "Purchase Invoice", "name":"PINV-02108-1"},
   {"doctype": "Purchase Invoice", "name":"PINV-02109-1"},
   {"doctype": "Purchase Invoice", "name":"PINV-02527-2"},
   {"doctype": "Purchase Invoice", "name":"PINV-02528-2"},
   {"doctype": "Purchase Invoice", "name":"PINV-02529-1"},
   {"doctype": "Purchase Invoice", "name":"PINV-02530-2"},
   {"doctype": "Purchase Invoice", "name":"PINV-02531-1"},
   {"doctype": "Purchase Invoice", "name":"PINV-02640"},
   {"doctype": "Purchase Invoice", "name":"PINV-00966"},
   {"doctype": "Purchase Invoice", "name":"PINV-00970"},
   {"doctype": "Purchase Invoice", "name":"PINV-00973"},
   {"doctype": "Purchase Invoice", "name":"PINV-00974"},
   {"doctype": "Purchase Invoice", "name":"PINV-00989"},
   {"doctype": "Purchase Invoice", "name":"PINV-01415"},
   {"doctype": "Purchase Invoice", "name":"PINV-01416"},
   {"doctype": "Purchase Invoice", "name":"PINV-01417"},
   {"doctype": "Purchase Invoice", "name":"PINV-01418"},
   {"doctype": "Purchase Invoice", "name":"PINV-01421"},
   {"doctype": "Purchase Invoice", "name":"PINV-01543"},
   {"doctype": "Purchase Invoice", "name":"PINV-01807"},
   {"doctype": "Purchase Invoice", "name":"PINV-01808"},
   {"doctype": "Purchase Invoice", "name":"PINV-02463"},
   {"doctype": "Purchase Invoice", "name":"PINV-02508"},
   {"doctype": "Purchase Invoice", "name":"PINV-02517"},
   {"doctype": "Purchase Invoice", "name":"PINV-02518"},
   {"doctype": "Purchase Invoice", "name":"PINV-02536"},
   {"doctype": "Purchase Invoice", "name":"PINV-02537"},
   {"doctype": "Purchase Invoice", "name":"PINV-02538"},
   {"doctype": "Purchase Invoice", "name":"PINV-02539"},
   {"doctype": "Purchase Invoice", "name":"PINV-02540"},
   {"doctype": "Purchase Invoice", "name":"PINV-02541"},
   {"doctype": "Purchase Invoice", "name":"PINV-02543"},
   {"doctype": "Purchase Invoice", "name":"PINV-02544"},
   {"doctype": "Purchase Invoice", "name":"PINV-02545"},
   {"doctype": "Purchase Invoice", "name":"PINV-00962-1"},
   {"doctype": "Purchase Invoice", "name":"PINV-00963-2"},
   {"doctype": "Purchase Invoice", "name":"PINV-00964-1"},
   {"doctype": "Purchase Invoice", "name":"PINV-00965-1"},
   {"doctype": "Purchase Invoice", "name":"PINV-00967-1"},
   {"doctype": "Purchase Invoice", "name":"PINV-00968-1"},
   {"doctype": "Purchase Invoice", "name":"PINV-00969-1"},
   {"doctype": "Purchase Invoice", "name":"PINV-00971-3"},
   {"doctype": "Purchase Invoice", "name":"PINV-00972-1"},
   {"doctype": "Purchase Invoice", "name":"PINV-00975-1"},
   {"doctype": "Purchase Invoice", "name":"PINV-02204-1"},
   {"doctype": "Purchase Invoice", "name":"PINV-02212-1"},
]