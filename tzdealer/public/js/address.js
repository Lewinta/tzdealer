frappe.ui.form.on("Address", {
	refresh: frm => {
		console.log("refreshed")
	},
	address_line1: frm => {
		frm.trigger("get_full_address");
	},
	address_line2: frm => {
		frm.trigger("get_full_address");
	},
	city: frm => {
		frm.trigger("get_full_address");
	},
	country: frm => {
		frm.trigger("get_full_address");
	},
	pincode: frm => {
		frm.trigger("get_full_address");
	},
	get_full_address: frm => {
		const {
			address_line1,
			address_line2,
			city,
			country,
			pincode,
		} = frm.doc;

		let full_address = ""

		if (address_line1)
			full_address = full_address.concat(" ", address_line1);

		if (address_line2)
			full_address = full_address.concat(" ", address_line2); 

		if (city)
			full_address = full_address.concat(", ", city);
		
		if (pincode)
			full_address = full_address.concat(" ", pincode);

		if (country)
			full_address = full_address.concat(" ", country);

		frm.set_value("full_address", full_address); 
	}
});