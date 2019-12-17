frappe.ui.form.on("Payment Entry", {
	refresh: frm => {
		frm.trigger("add_custom_buttons");
	},
	add_custom_buttons: frm => {
		frm.trigger("get_items_btn")
	},
	get_items_btn: frm => {
		if (frm.doc.docstatus >= 1)
			return

		frm.add_custom_button(
			"Get Invoice Items",
			e => {
				frm.trigger("get_item_details")
				frappe.show_alert("Items Loaded Successfully");
			}
		);
	},
	_reference_no: frm => {
		let {_reference_no} = frm.doc;

		new_ref = _reference_no ? _reference_no : "";
		frm.set_value("reference_no", _reference_no);
	},
	get_item_details: frm => {
		if (!frm.doc.references || frm.doc.references.length < 1)
			return 

		$.map(cur_frm.doc.references, ref => {
		    frappe.call({
		        "method": "tzdealer.hook.payment_entry.render_items",
		        "args": {
		            "dt": ref.reference_doctype,
		            "dn": ref.reference_name,
		        },
		        "callback": ({message}) => frappe.model.set_value(
		        	ref.doctype,
		        	ref.name,
		        	"items",
		        	message
		        )
		    })
		})
	},
	party: frm =>{
		setTimeout(e=>{
			frm.trigger("get_item_details");
		}, 4000);
	},
	mode_of_payment: frm => {
		if (frm.doc.mode_of_payment == "Cash"){
			frm.set_value("reference_no", "Cash");
			return
		}
		frm.trigger("_reference_no");
		setTimeout(e=>{
			frm.trigger("get_item_details");
		}, 4000);
	},
	date: frm => {
		const {date, posting_date} = frm.doc;
		
		if (!date){
			frm.set_value("posting_date", "");
			return
		}
		frm.set_value("posting_date", date);

	},
	payment_type: frm => {
		if (frm.doc.payment_type == "Pay")
			frm.set_value("party_type", "Supplier")

		if (frm.doc.payment_type == "Receive")
			frm.set_value("party_type", "Customer")
	}
})