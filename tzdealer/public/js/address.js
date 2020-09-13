frappe.ui.form.on("Address", {
	refresh: frm => {
		// console.log(frappe.route_history[frappe.route_history.length -2][3])
	},
	validate: frm => {
		frm.trigger("make_custom_title");
	},
	onload_post_render: frm => {
		if (frappe.route_history.length > 1){
			last_page = frappe.route_history[frappe.route_history.length -2];
			if (last_page[0] == "Form" && last_page[1] == "Item" && last_page[3]){
				frm.add_child("links", last_page[3]);
				frm.refresh_field("links");
			}
		}
	},
	address_title: frm => {
		parts = frm.doc.address_title.split(",");
		
		if (!frm.doc.address_line1)
			frm.set_value("address_line1", "-");
		
		if (parts.length >= 2){
			frm.set_value("city", parts[0]);
			frm.set_value("state", parts[1]);
		}

	},
	make_custom_title: frm => {
		entity = "";
		city = "";
		state = "";

		if (frm.doc.links)
			entity = `${frm.doc.links[0].link_name} -`;

		if (frm.doc.city)
			city = frm.doc.city;

		if (frm.doc.state)
			state = frm.doc.state;

		frm.set_value("custom_title", `${entity} ${city}, ${state}`);
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