# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "TZDEALER",
			"color": "#4aa3df",
			"icon": "fa fa-car",
			"type": "module",
			"label": _("TZDEALER")
		},{
			"module_name": "Vehicle Status",
			"_report": "Vehicle Status",
			"link": "query-report/Vehicle Status",
			"color": "#33bf19",
			"icon": "fa fa-car",
			"type": "link",
			"label": _("Vehicle Status")
		}
	]
