// Copyright (c) 2025, Lithe-Tech Limited and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Salary Details"] = {
	"filters": [
        
		{
			"fieldname": "company",
			"fieldtype": "Link",
			"label": "Company",
			"mandatory": 0,
			"default": frappe.defaults.get_user_default("Company"),
			"options": "Company",
			"wildcard_filter": 0
		},
		{
			"fieldname": "employee",
			// "fieldtype": "Link",
			"label": "Employee",
			"mandatory": 0,
			"fieldtype": "MultiSelectList",
			// "default":"Tah 120",
			"options": "Employee",
			"wildcard_filter": 0,
			"get_data": function(txt) {
				return frappe.db.get_link_options("Employee", txt);
			 }
		},
		{
			"fieldname": "department",
			"fieldtype": "Link",
			"label": "Department",
			"mandatory": 0,
			// "default":"Admin (GSD) - QSTML",
			"options": "Department",
			"wildcard_filter": 0,
		},
		
			
	]
};
