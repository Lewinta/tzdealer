frappe.ui.form.on("Item", {
	refresh: frm => {
		if (frm.is_new()) {
			frm.trigger("item_type");
		}
		frm.fields_dict._form_dashboard.collapse();
		$.map([
			"set_queries",
			"add_custom_buttons"
		], event => {
			frm.trigger(event);
		});
	},
	onload_post_render: frm => {
		if (frm.is_new()) {
			frm.trigger("item_type");
		}
	},
	validate: frm => {
		frm.trigger("item_type");
	},
	set_queries: frm => {
		frm.set_query("item_type", function () {
			return {
				filters: {
					"parent_item_group": "All Item Groups"
				}
			}
		});
		frm.set_query("model", function () {
			return {
				filters: {
					"make": frm.doc.make
				}
			}
		});
		frm.set_query("part", function () {
			return {
				filters: {
					"part_group": frm.doc.part_group,
				}
			}
		});
		frm.set_query("part_group", function () {
			return {
				filters: {
					"part_type": frm.doc.part_type,
				}
			}
		});
	},
	add_custom_buttons: frm => {
		frm.add_custom_button(__("Item Details"), event => {
			frm.trigger("view_item_details"); }, __("View"));
	},
	item_name: frm => {
		frm.set_value("item_name", frm.doc.item_name.toUpperCase());
	},
	item_type: frm => {
		let {item_type} = frm.doc;
		if (!item_type)
			return
		
		if (item_type == "Containers")
			frm.fields_dict.section_break_11.collapse();

		let maintain = [
			"Vehicles",
			"Vehicle Parts",
			"Containers"
		].includes(item_type) ? true : false;
		
		frm.set_value("item_group", item_type);
		frm.set_value("is_stock_item", maintain);
		frm.trigger("set_df_fields");
	},
	vim_number: frm => {
		frm.set_value("item_code", frm.doc.vim_number);
	},
	part: frm => {
		frm.trigger("create_item_name");
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
		let {make, model, year, exterior_color, part} = frm.doc;
		let name = "";
		if (part)
			name = name.concat(" ", part);
		if (make)
			name = name.concat(" ", make);
		if (model)
			name = name.concat(" ", model);
		if (exterior_color)
			name = name.concat(" ", exterior_color);
		if (year)
			name = name.concat(" ", year);

		name = name.trim();

		frm.set_value("item_name", name);
	},
	view_item_details: frm => {
		const { doc } = frm,
		callback = data => {
			if (data) {
				const { name } = data;

				frappe.set_route(["Form", "Item Detail", name]);

				return ;
			}

			frappe.new_doc("Item Detail", {
				"item": doc.item_code,
				"item_name": doc.item_name,
			}, event => {
				cur_frm.trigger("item");
			});
		};

		frappe.db.get_value("Item Detail", {
			"item": doc.item_code,
		}, ["name"], callback);
	},
	shipping_line: frm => {
		if (!frm.doc.shipping_line)
			return
		frm.set_value("shipping_line", frm.doc.shipping_line.toUpperCase());
	},
	container_no: frm => {
		if (!frm.doc.container_no)
			return
		frm.set_value("container_no", frm.doc.container_no.toUpperCase());
		frm.set_value("item_name", frm.doc.container_no.toUpperCase());
	},
	booking_no: frm => {
		if (!frm.doc.booking_no)
			return
		frm.set_value("booking_no", frm.doc.booking_no.toUpperCase());
	},
	seal_no: frm => {
		if (!frm.doc.seal_no)
			return
		frm.set_value("seal_no", frm.doc.seal_no.toUpperCase());
	},
	set_df_fields: frm => {
		let selection = frm.doc.item_type.replace(" ","_").toLowerCase();
		let clear_req = [];
		let clear_enabled = [];
		let reqd = {
			"vehicles" : ["make", "model", "year", "vim_number"],
			"containers" : ["container_no", "booking_no"],
			"vehicle_parts" : ["part_type"],
			"services" : ["item_code"],
		}
		let disable = {
			"vehicles" : ["item_name", "item_code"],
			"containers" : ["item_name", "item_code"],
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

		frm.toggle_display("item_code", selection == "vehicle_parts");


	}
});
