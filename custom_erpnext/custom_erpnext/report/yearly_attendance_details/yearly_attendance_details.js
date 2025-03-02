// Copyright (c) 2025, Lithe-Tech Limited and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Yearly Attendance Details"] = {
	"filters": [
        {
			"fieldname":"from_date",
			"label": __("From"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(),-12),
			"reqd": 1,
			"width": "100px"
		},
		{
			"fieldname":"to_date",
			"label": __("To"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "100px"
		},
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
				"fieldtype": "Link",
				"label": "Employee",
				"mandatory": 0,
				"options": "Employee",
				"wildcard_filter": 0
			},


			{
			 "fieldname": "department",
			 "fieldtype": "Link",
			 "label": "Department",
			 "mandatory": 0,
			 "options": "Department",
			 "wildcard_filter": 0
			},
			{
			 "fieldname": "designation",
			 "fieldtype": "Link",
			 "label": "Designation",
			 "mandatory": 0,
			 "options": "Designation",
			 "wildcard_filter": 0
			},
			{
				"fieldname": "section",
				"fieldtype": "Link",
				"label": "Section",
				"mandatory": 0,
				"options": "Section",
				"wildcard_filter": 0
			   },	
			   {
				"fieldname": "group_name",
				"fieldtype": "Link",
				"label": "Employee Group",
				"mandatory": 0,
				"options": "Group",
				"wildcard_filter": 0
			   },
			   
			   {
				"fieldname": "facility_or_line",
				"fieldtype": "Link",
				"label": "Facility/Line",
				"mandatory": 0,
				"options": "Facility or Line",
				"wildcard_filter": 0

			   },

			   {
				"fieldname": "floor",
				"fieldtype": "Link",
				"label": "Floor",
				"mandatory": 0,
				"options": "Floor",
				"wildcard_filter": 0

			   },
			   

	]
};
