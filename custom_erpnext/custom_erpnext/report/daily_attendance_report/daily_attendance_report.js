// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Attendance Report"] = {
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
        },
        {
            "fieldname": "status",
            "fieldtype": "Select",
            "label": "Status",
            "options": ["","Present","Absent","Late","On Leave","Weekly Off","Holiday"]
           
        },
    
    ]
};