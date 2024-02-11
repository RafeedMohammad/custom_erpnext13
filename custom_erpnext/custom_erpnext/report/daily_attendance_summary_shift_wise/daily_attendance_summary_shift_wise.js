// Copyright (c) 2024, Lithe-Tech Limited and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Attendance Summary Shift Wise"] = {
	"filters": [
		{
            "fieldname":"date",
            "label": __("Date"),
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
		// {
		// 	"fieldname":"group_by",
		// 	"label": __("Group By"),
		// 	"fieldtype": "Select",
		// 	"options": ["","Branch","Grade","Department","Designation"]
		// },

	]
};
