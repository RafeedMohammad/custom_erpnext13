// Copyright (c) 2022, Lithe-Tech Limited and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Salary Sheet"] = {
    "filters": [
        {
            "fieldname": "currency",
            "fieldtype": "Link",
            "options": "Currency",
            "label": __("Currency"),
            "default": erpnext.get_currency(frappe.defaults.get_default("Company")),
            "width": "50px"
        },
        {
            "fieldname":"employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee",
            "width": "100px"
        },
        {
            "fieldname":"company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "width": "100px",
            "reqd": 1
        },
        {
            "fieldname":"docstatus",
            "label":__("Document Status"),
            "fieldtype":"Select",
            "options":["Draft", "Submitted", "Cancelled"],
            "default": "Submitted",
            "width": "100px"
        },
        {
            "fieldname": "month",
            "label": __("Month"),
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
			"fieldtype": "Select",
			"reqd": 1
		}
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
}