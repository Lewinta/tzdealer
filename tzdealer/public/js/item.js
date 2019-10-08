frappe.ui.form.on("Item", {
	refresh: frm => {
		if (frm.is_new()) {
			frm.trigger("item_type");
		}

		frm.fields_dict._form_dashboard.collapse();
		$.map([
			"set_queries",
			"add_custom_buttons",
			"set_mandatory_fields",
		], event => {
			frm.trigger(event);
		});
		frm.trigger("set_df_fields");

	},
	onload_post_render: frm => {
		if (frm.is_new()) {
			frm.trigger("item_type");
		}
	},
	validate: frm => {
		frm.trigger("item_type");
		frm.trigger("validate_suppliers");
		frm.trigger("create_item_name");
	},
	validate_suppliers: frm => {
		const {item_type, trucking_supplier_price, loading_supplier_price} = frm.doc;
		
		if(item_type != "Containers")
			return
		if(trucking_supplier_price <= 0.00){
			frappe.msgprint(__("Please set Trucking Supplier Price"))
			validated = false;
		}
		if(loading_supplier_price <= 0.00){
			frappe.msgprint(__("Please set Loading Supplier Price"))
			validated = false;
		}

	},
	set_mandatory_fields: frm => {
		let reqd = frm.doc.item_type == "Containers"
		if (reqd){
			let fields = [
			"booking_supplier",
			"booking_supplier_price",
			"trucking_supplier",
			"trucking_supplier_price",
			"loading_supplier",
			"loading_supplier_price",
			"destination",
			"shipping_line",
			]
			$.map(fields, field => {
				frm.toggle_reqd(field, reqd)
			});
		}

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

		frm.set_query("model", "item_description", (frm, cdt, cdn) => {
			const doc = frappe.get_doc(cdt, cdn);
			return {
				filters: {
					"make": doc.make,
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
		frm.set_query("shipper", function () {
			return {
				filters: {
					"party_type": "Exporter",
				}
			}
		});
		frm.set_query("consignee", function () {
			return {
				filters: {
					"party_type": "Consignee",
				}
			}
		});
		frm.set_query("notified_party", function () {
			return {
				filters: {
					"party_type": "Notified Party",
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

		let maintain = [
			"Vehicles",
			"Vehicle Parts",
			"Containers"
		].includes(item_type) ? true : false;

		frm.set_value("item_group", item_type);
		frm.set_value("is_stock_item", maintain);
		frm.trigger("set_df_fields");
		frm.trigger("set_mandatory_fields");
	},
	_default_supplier: frm => {
		frm.set_value("default_supplier", frm.doc._default_supplier)
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
		let name = "";
		
		if (frm.doc.item_type == "Vehicles"){
			let {make, model, year, exterior_color, part} = frm.doc;
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
		}

		if (frm.doc.item_type == "Containers"){
			let {booking_no, container_no} = frm.doc;
			if (booking_no)
				name = name.concat(" ", booking_no);
			if (container_no)
				name = name.concat("-", container_no);
		}

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
		frm.trigger("create_item_name");
	},
	booking_no: frm => {
		if (!frm.doc.booking_no)
			return
		frm.set_value("booking_no", frm.doc.booking_no.toUpperCase());
		frm.trigger("create_item_name");
	},
	seal_no: frm => {
		if (!frm.doc.seal_no)
			return
		frm.set_value("seal_no", frm.doc.seal_no.toUpperCase());
	},
	consignee: frm => {
		if (!frm.doc.consignee)
			return
		$.map(frm.doc.item_description, row => {
			row.consignee_name = frm.doc.consignee; 
		});
	},
	set_df_fields: frm => {
		let selection = frm.doc.item_type.replace(" ","_").toLowerCase();
		let clear_req = [];
		let clear_enabled = [];
		let reqd = {
			"vehicles" : ["make", "model", "year", "vim_number", "exterior_color"],
			"containers" : ["booking_no"],
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

frappe.ui.form.on("Item Description", {
	item_code: (frm, cdt, cdn) => {
		const { script_manager, doc } = frm;
		const { consignee } = doc;
		script_manager
			.trigger("update_description",
			    cdt, cdn);
		if (consignee)
			frappe.model.set_value(cdt, cdn, "consignee_name", consignee);
	},
	item_description_add: (frm, cdt, cdn) => {
		// pass
	},
	item_description_remove: (frm, cdt, cdn) => {
		const { script_manager } = frm;

		script_manager
			.trigger("update_description",
			    cdt, cdn);
	},
	update_description: (frm, cdt, cdn) => {
		const { doc } = frm;

		let value = $.map(doc.item_description, d => {
			return d.item_code;
		}).join("<br>");

		frm.set_value("description", value);
	}
});
