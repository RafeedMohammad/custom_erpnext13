// Copyright (c) 2025, Lithe-Tech Limited and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly PF Outgoing Report"] = {
"filters": [
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec\n",
			// "default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
			// 	"Dec"
			// ][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
			"default":""
		},

		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Select",

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
		// {
		// 	"fieldname":"employee_type",
		// 	"label":__("Employee Type"),
		// 	"fieldtype":"Select",
		// 	"options":["Active","Inactive","Left",""],
		// 	"default": "Active",
		// 	"width": "100px"
		// },
		{
			"fieldname":"mode_of_payment",
			"label":__("Bank/Cash"),
			"fieldtype":"Select",
			"options":["Bank","Cash",""],
			"default": "",
			"width": "100px"
		},
		
			
	]
	,
	onload: function() {
		return  frappe.call({
			method: "custom_erpnext.custom_erpnext.report.salary_details.salary_details.get_year_options",
			callback: function(r) {
				var year_filter = frappe.query_report.get_filter('year');
				year_filter.df.options = r.message;
				year_filter.df.default = r.message[0];

				year_filter.refresh();
				year_filter.set_input(year_filter.df.default);
			}
		});
	}
};

