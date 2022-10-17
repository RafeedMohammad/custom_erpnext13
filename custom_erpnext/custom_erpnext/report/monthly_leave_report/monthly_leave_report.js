// Copyright (c) 2022, Lithe-Tech Limited and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly Leave Report"] = {
	"filters": [
		{
			"fieldname": "from_month",
			"label": __("From Month"),
			"fieldtype": "Select",
			"reqd": 1 ,
			"options": [
				{ "value": 1, "label": __("Jan") },
				{ "value": 2, "label": __("Feb") },
				{ "value": 3, "label": __("Mar") },
				{ "value": 4, "label": __("Apr") },
				{ "value": 5, "label": __("May") },
				{ "value": 6, "label": __("June") },
				{ "value": 7, "label": __("July") },
				{ "value": 8, "label": __("Aug") },
				{ "value": 9, "label": __("Sep") },
				{ "value": 10, "label": __("Oct") },
				{ "value": 11, "label": __("Nov") },
				{ "value": 12, "label": __("Dec") },
			],
			"default": frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth() + 1
		},
		{
			"fieldname": "to_month",
			"label": __("To Month"),
			"fieldtype": "Select",
			"reqd": 1 ,
			"options": [
				{ "value": 1, "label": __("Jan") },
				{ "value": 2, "label": __("Feb") },
				{ "value": 3, "label": __("Mar") },
				{ "value": 4, "label": __("Apr") },
				{ "value": 5, "label": __("May") },
				{ "value": 6, "label": __("June") },
				{ "value": 7, "label": __("July") },
				{ "value": 8, "label": __("Aug") },
				{ "value": 9, "label": __("Sep") },
				{ "value": 10, "label": __("Oct") },
				{ "value": 11, "label": __("Nov") },
				{ "value": 12, "label": __("Dec") },
			],
			"default": frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth() + 1
		},
		{
			"fieldname":"year",
			"label": __("Year"),
			// "default": frappe.datetime.get_year(),
			"fieldtype": "Select",
			"reqd": 1
		},
        {
            "fieldname": "company",
            "fieldtype": "Link",
            "label": "Company",
            "mandatory": 0,
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
           

        {
            "fieldname": "shift",
            "fieldtype": "Link",
            "label": "Shift",
            "mandatory": 0,
            "options": "Shift Type",
            "wildcard_filter": 0
        }
	],
    "onload": function() {
		return  frappe.call({
			method: "erpnext.hr.report.monthly_attendance_sheet.monthly_attendance_sheet.get_attendance_years",
			callback: function(r) {
				var year_filter = frappe.query_report.get_filter('year');
				year_filter.df.options = r.message;
				year_filter.df.default = r.message.split("\n")[0];
				year_filter.refresh();
				year_filter.set_input(year_filter.df.default);
			}
		});
	}
};

