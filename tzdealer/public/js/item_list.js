$.extend(frappe.listview_settings['Item'], {
	"get_indicator": (doc) => {
		if(doc.status === "Pending") {
			return [__("Pending"), "orange", "status,=,Pending"];
		}  else if(doc.status === "Received") {
			return [__("Received"), "green", "status,=,Received"];
		} else if(doc.status === "Delivered") {
			return [__("Delivered"), "purple", "status,=,Delivered"];
		} else if(doc.status === "Coming Soon") {
			return [__("Coming Soon"), "red", "status,=,Coming Soon"];
		}
	}
});
