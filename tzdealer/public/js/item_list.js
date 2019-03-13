$.extend(frappe.listview_settings['Item'], {

	"get_indicator": doc => {
		// Make bold name column
		$(".list-item__content.list-item__content--id")
			.css({"font-weight": "bold", "overflow": "inherit"})

		if(doc.status === "Coming Soon") {
			return [__("Coming Soon"), "orange", "status,=,Coming Soon"];
		}  else if(doc.status === "Received") {
			return [__("Received"), "green", "status,=,Received"];
		} else if(doc.status === "Delivered") {
			return [__("Delivered"), "purple", "status,=,Delivered"];
		} 
	}
});
