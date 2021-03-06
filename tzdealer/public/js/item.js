frappe.ui.form.on("Item", {
	refresh: frm => {
		if (frm.is_new()) {
			frm.trigger("item_type");
		}

		frm.fields_dict._form_dashboard.collapse();
		$.map([
			"set_queries",
			"add_custom_buttons",
		], event => {
			frm.trigger(event);
		});
		frm.trigger("set_df_fields");
		frm.trigger("add_supplier_to_history");

		frappe.realtime.on("reload_vehicle", () => { 
			frm.reload_doc(); 
		})
		
	},
	onload_post_render: frm => {
		if (frm.is_new()) {
			frm.trigger("item_type");
		}
	},
	validate: frm => {
		let events = ["item_type", "validate_suppliers", "create_item_name", "validate_warehouse"];
		$.map(events, event => frm.trigger(event))
		// frm.set_value("item_code", frm.doc.name)
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
	validate_warehouse: frm => {
		let filters = {
			"default": 1, 
			"company": frm.doc.company, 
		}

		frappe.db.get_value("Warehouse", filters, "name", ({name}) => {
			if(!name)
				return
			if(frm.doc.default_warehouse != name){
				frappe.throw(`Invalid default warehouse for company ${name}`)
				validated = false;
			}
		});
	},
	set_queries: frm => {
		frm.trigger("set_location_query");

		frm.set_query("income_account", function () {
			return {
				filters: {
					"company": frm.doc.company
				}
			}
		});
		frm.set_query("expense_account", function () {
			return {
				filters: {
					"company": frm.doc.company
				}
			}
		});
		frm.set_query("tax_type", "taxes", function () {
			return {
				filters: {
					"company": frm.doc.company
				}
			}
		});
		frm.set_query("tax", "items", function () {
			return {
				filters: {
					"company": frm.doc.company,
					"account_type": "Tax",
				}
			}
		});
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
	set_location_query: frm => {
		frm.set_query("location", function () {
			return {
				"query": "tzdealer.hook.item.address_by_supplier",
				"filters": {
					"supplier": frm.doc._default_supplier
				}
			};
		});
	},
	add_custom_buttons: frm => {
		frm.add_custom_button(__("Item Details"), event => {
			frm.trigger("view_item_details"); 
		}, __("View"));
		
		// if (frm.doc.item_type == "Vehicles" && frm.doc.website_post){
		// 	let btn = frm.add_custom_button(__("Post to Website"), event => {
		// 		frm.trigger("post_to_website");
		// 	});
		// 	btn.addClass("btn-primary");
		// }
	},
	post_to_website: frm => {

		let {docname} = frm;

		if(frm.is_dirty())
			frappe.run_serially([
				() => frappe.dom.freeze("please wait..."),
				() => frm.save_or_update(),
				() => frappe.call("tzdealer.hook.item.post_to_website", {docname}).then(
					() => frappe.dom.unfreeze(),
					() => frm.reload_doc(),
				).catch(
					() => frappe.msgprint("Something Went Wrong")
				),
				() => frappe.dom.unfreeze()
			])
		else
			frappe.run_serially([
				() => frappe.dom.freeze("please wait..."),
				() => frappe.call("tzdealer.hook.item.post_to_website", {docname}).then(
					() => frappe.dom.unfreeze(),
					() => frm.reload_doc(),
				).catch(
					() => frappe.msgprint("Something Went Wrong")
				),
				() => frappe.dom.unfreeze()
			])
	},
	_item_name: frm => {
		frm.set_value("_item_name", frm.doc._item_name.toUpperCase());
		frm.set_value("item_name", frm.doc._item_name.toUpperCase());
		
		if (["Services", "Third Party Services", "Vehicle Parts"].includes(frm.doc.item_type))
			frm.set_value("item_code", frm.doc._item_name.toUpperCase());
	},
	item_name: frm => {
		frm.set_value("item_name", frm.doc.item_name.toUpperCase());
		if (["Services", "Third Party Services","Vehicle Parts"].includes(frm.doc.item_type))
			frm.set_value("item_code", frm.doc.item_name.toUpperCase());
	},
	item_type: frm => {
		let {item_type} = frm.doc;
		if (!item_type)
			return

		let maintain = [
			"Vehicles",
			"Vehicle Parts",
			"Containers",
			"Third Party Services",
		].includes(item_type) ? 1 : 0;

		frm.set_value("item_group", item_type);
		frm.set_value("is_stock_item", maintain);
		frm.trigger("set_df_fields");
	},
	company: frm => {
		if(!frm.doc.company)
			return
		filters = {
			"default": 1,
			"company": frm.doc.company
		}
		frappe.db.get_value("Warehouse", filters, "name", ({name}) => {
			if(!name)
				return
			frm.set_value("default_warehouse", name);
		});
	},
	_default_supplier: frm => {
		frm.set_value("default_supplier", frm.doc._default_supplier)
		frm.trigger("set_location_query");
		frm.trigger("add_supplier_to_history");
	},
	add_supplier_to_history: frm => {
		// let's append the supplier on the history in case 
		// we need to add an address
		if (!frm.doc._default_supplier)
			return
		
		if (frappe.route_history[frappe.route_history.length - 1])
			frappe.route_history[frappe.route_history.length - 1][3] = {
				"link_doctype": "Supplier",
				"link_name": frm.doc._default_supplier
			}
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
			let {make, model, year, exterior_color, part, vim_number} = frm.doc;
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
			if (vim_number)
				name = name.concat(" - ", vim_number);
		}

		if (frm.doc.item_type == "Containers"){
			let {booking_no, container_no} = frm.doc;
			if (booking_no)
				name = name.concat(" ", booking_no);
			if (container_no)
				name = name.concat("-", container_no);
		}

		if (["Services", "Third Party Services"].includes(frm.doc.item_type)){
			name = frm.doc.item_name;
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
		let selection = frm.doc.item_type.replaceAll(" ","_").toLowerCase();
		let clear_req = [];
		let clear_enabled = [];
		let reqd = {
			"vehicles" : ["make", "model", "year", "vim_number", "exterior_color", "purchase_date", "default_supplier", "_default_supplier", "location"],
			"vehicle_parts" : ["part_type", "purchase_date"],
			"third_party_services" : ["item_code", "_item_name"],
			"services" : ["item_code", "_item_name"],
			"containers" : [
				"booking_no", "purchase_date", "eta", "booking_supplier",
				"booking_supplier_price", "trucking_supplier", "trucking_supplier_price", "loading_supplier",
				"loading_supplier_price","destination", "shipping_line",
				"_default_supplier", "location",
			],
		}
		let disable = {
			"vehicles" : ["_item_name", "item_code"],
			"containers" : ["_item_name", "item_code"],
			"vehicle_parts" : ["item_code", "barcode", ],
			"services" : [],
			"third_party_services" : [],
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
		if(clear_req)
			frm.toggle_reqd(clear_req, false);
		//Let's add all custom mandatory fields
		if(reqd[selection])
			frm.toggle_reqd(reqd[selection], true);
		//Let's clear all custom enabled fields
		if(clear_enabled)
			frm.toggle_enable(clear_enabled, true);
		//Let's add all custom enabled fields
		if(disable[selection])
			frm.toggle_enable(disable[selection], false);

		frm.toggle_display("item_code", ["vehicle_parts", "services", "third_party_services"].includes(selection));
		frm.toggle_display("purchase_date", selection != "services");
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

frappe.ui.form.on("Website Image", {
	post: (frm, cdt, cdn) => {
		let args = {"web_img": cdn}
		frappe.call("tzdealer.api.post_media", args, console.log).then( ()=> frm.reload_doc());
	}
});