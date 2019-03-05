frappe.ui.form.on("Item", {
	refresh: frm => {
		if (frm.is_new())
			frm.trigger("item_type");

		frm.set_query("model", function () {
			return {
				filters: {
					"make": frm.doc.make	
				}
			}
		});
	}, 
	item_name: frm => {
		frm.set_value("item_name", frm.doc.item_name.toUpperCase());
	}, 
	item_type: frm => {
		if (!frm.doc.item_type)
			return
		frm.set_value("item_group", frm.doc.item_type);
		frm.trigger("set_df_fields");
	},
	vim_number: frm => {
		frm.set_value("item_code", frm.doc.vim_number);
	},
	make: frm => {
		frm.trigger("create_item_name");
	},
	model: frm => {
		frm.set_value("model", frm.doc.model.toUpperCase());
		frm.trigger("create_item_name");
	},
	year: frm => {
		frm.trigger("create_item_name");
	},
	exterior_color: frm => {
		frm.set_value("exterior_color", frm.doc.exterior_color.toUpperCase());
		frm.trigger("create_item_name");
	},
	create_item_name: frm => {
		let {make, model, year, exterior_color} = frm.doc;
		let name = "";
		if (make)
			name = make;
		if (model)
			name = name.concat(" ", model);		
		if (exterior_color)
			name = name.concat(" ", exterior_color);		
		if (year)
			name = name.concat(" ", year);

		name = name.trim();

		frm.set_value("item_name", name);
	},
	set_df_fields: frm => {
		let selection = frm.doc.item_type.replace(" ","_").toLowerCase();
		let clear_req = [];
		let clear_enabled = [];
		let reqd = {
			"vehicles" : ["make", "model", "year", "vim_number"],
			"vehicle_parts" : ["part_type"],
			"services" : [],
		}
		let disable = {
			"vehicles" : ["item_name", "item_code"],
			"vehicle_parts" : ["item_code", "barcode", ],
			"services" : [],
		}
		//Let's combine all custom mandatory fields
		$.each(reqd, (key, val) => {
			clear_req = clear_req.concat(val);
		});
		//Let's combine all custom enabled fields
		$.each(disable, (key, val) => {
			clear_enabled = clear_enabled.concat(val);
		});
		
		//Let's clear all custom mandatory fields
		frm.toggle_reqd(clear_req, false);	

		//Let's add all custom mandatory fields
		frm.toggle_reqd(reqd[selection], true);	

		//Let's clear all custom enabled fields
		frm.toggle_enable(clear_enabled, true);

		//Let's add all custom enabled fields
		frm.toggle_enable(disable[selection], false);

	}
});
