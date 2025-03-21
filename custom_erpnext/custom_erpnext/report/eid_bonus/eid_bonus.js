// Copyright (c) 2025, Lithe-Tech Limited and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Eid Bonus"] = {
	"filters": [
        {
			"fieldname":"from_date",
			"label": __("From"),
			"fieldtype": "Date",
			// "default": frm.doc.start_date,
			"reqd": 0,
			"width": "100px"
		},

		{
			"fieldname":"occasion",
			"label":__("Occasion"),
			"fieldtype":"Select",
			"options":["EID-UL-FITR","EID-UL-AZHA","Advance Salary (Basic)"],
			"default": "Active",
			"width": "100px"
		},

		// {
		// 	"fieldname":"to_date",
		// 	"label": __("To"),
		// 	"fieldtype": "Date",
		// 	// "default": filters.get(from_date),
		// 	"reqd": 0,
		// 	"width": "100px"
		// },
		// {
		// 	"fieldname": "month",
		// 	"label": __("Month"),
		// 	"fieldtype": "Select",
		// 	"options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
		// 	"default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
		// 		"Dec"
		// 	][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
		// },
		// {
		// 	"fieldname":"year",
		// 	"label": __("Year"),
		// 	"fieldtype": "Select",
		// 	"reqd": 1
		// },
		{
            "fieldname": "year",
            "label": __("Year"),
            "fieldtype": "Date",
            "default": new Date().getFullYear(),
            "hidden": 1  // Hide the year filter
        },
		
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"reqd": 0,
			"options": "Employee",
			"width": "100px"
		},

		// {
        //     "fieldname":"docstatus",
        //     "label":__("Document Status"),
        //     "fieldtype":"Select",
        //     "options":["Draft", "Submitted", "Cancelled"],
        //     "default": "Draft",
        //     "width": "100px"
        // },
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
			// {
			// 	"fieldname": "Sub-Department",
			// 	"fieldtype": "Data",
			// 	"label": "Sub-Department",
			// 	"mandatory": 0,
			// 	// "options": "Designation",
			// 	"wildcard_filter": 0
			//    },
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
			   {
				"fieldname": "grade",
				"fieldtype": "Link",
				"label": "Grade",
				"mandatory": 0,
				"options": "Employee Grade",
				"wildcard_filter": 0

			   },
			   {
				"fieldname": "employment_type",
				"fieldtype": "Link",
				"label": "Employment Type",
				"mandatory": 0,
				"options": "Employment Type",
				"wildcard_filter": 0

			   },
			   {
				"fieldname":"mode_of_payment",
				"label":__("Bank/Cash"),
				"fieldtype":"Select",
				"options":["Bank","Cash",""],
				"default": "",
				"width": "100px"
			},
			{
				"fieldname": "bank",
				"fieldtype": "Link",
				"label": "Bank Name",
				"mandatory": 0,
				"options": "Bank",
				"wildcard_filter": 0,
				"depends_on": "eval:doc.mode_of_payment == 'Bank'"
			   },
			{
				"fieldname":"employee_type",
				"label":__("Employee Type"),
				"fieldtype":"Select",
				"options":["Active","New Join","Left",""],
				"default": "Active",
				"width": "100px"
			},
			{
				"fieldname": "month",
				"label": __("Month"),
				"fieldtype": "Select",
				"options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec\n",
				"default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
					"Dec"
				][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
				"hidden":1
			},
			   

			// {
			// 	"fieldname": "shift",
			// 	"fieldtype": "Link",
			// 	"label": "Shift",
			// 	"mandatory": 0,
			// 	"options": "Shift Type",
			// 	"wildcard_filter": 0
			// },

	]
};
