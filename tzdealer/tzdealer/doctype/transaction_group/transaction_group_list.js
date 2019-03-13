$.extend(frappe.listview_settings['Transaction Group'], {

	"get_indicator": doc => {

		if(doc.transaction_type === "Sales") {
			return [__("Sales"), "orange", "transaction_type,=,Sales"];
		}  else if(doc.transaction_type === "Purchases") {
			return [__("Purchases"), "green", "transaction_type,=,Purchases"];
		}
	}
});
