// Copyright (c) 2025, Lithe-Tech Limited and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["SATTLEMENT SHEET"] = {
	"filters": [

		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
			"default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
				"Dec"
			][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
		},
		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Select",
			"reqd": 1
		},

		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"reqd": 0,
			"options": "Employee",
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
		// 	"fieldname": "shift",
		// 	"fieldtype": "Link",
		// 	"label": "Shift",
		// 	"mandatory": 0,
		// 	"options": "Shift Type",
		// 	"wildcard_filter": 0
		// },

	],
	onload: function() {
		return  frappe.call({
			method: "custom_erpnext.custom_erpnext.report.salary_summary_report.salary_summary_report.get_salary_slip_years",
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
