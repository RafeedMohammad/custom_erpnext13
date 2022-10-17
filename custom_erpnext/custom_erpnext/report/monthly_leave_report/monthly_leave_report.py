# Copyright (c) 2022, Lithe-Tech Limited and contributors
# For license information, please see license.txt

# import frappe

from calendar import monthrange
from datetime import datetime
import frappe
from frappe import _, msgprint
from frappe.utils import cint, cstr, getdate

def execute(filters=None):
	
	if not filters:
		filters = {}
	columns = get_columns()
	data = get_missing_entry(filters)
	
	return columns, data
def get_columns():
	return [
		_("Emp Id") + ":Link/Employee:120",
		_("Designation") + ":Data/:120",
		# _("Section") + ":Data/:120",
		_("Approved date") + ":Data/:120",
		_("From Date") + ":Data/:120",
		_("To Date") + ":Data/:120",
		_("Leave Type") + ":Data/:120",
		_("Leave Days") + ":Data/:120",
		_("Remarks") + ":Data/:120"
    ]

def get_missing_entry(filters):
	conditions, filters = get_conditions(filters)
	result= frappe.db.sql("""select la.employee, emp.designation, la.posting_date, la.from_date, la.to_date, la.leave_type,
		la.total_leave_days, la.description
		FROM `tabLeave Application` la
		LEFT JOIN tabEmployee emp ON la.employee = emp.name  
		where 
		la.docstatus<2 %s
		""" 
		%conditions, 
		as_list=1)
	return result

def get_conditions(filters):
	conditions="" 
	if not (filters.get("to_month") and filters.get("year")):
		msgprint(_("Please select month and year"), raise_exception=1)

	total_days_in_to_month = monthrange(cint(filters.year), cint(filters.to_month))[1]
	to_date=filters.get("year")+"-"+str(filters.get("to_month")).zfill(2)+"-"+str(total_days_in_to_month)
     
	from_date=filters.get("year")+"-"+str(filters.get("from_month")).zfill(2)+"-"+"01"
	#from_date1=datetime.strptime(from_date,'%y-%m-%d')

	# if filters.get("from_date"): conditions += " and att.attendance_date>= '%s'" % filters["from_date"]
	# if filters.get("to_date"): conditions += " and att.attendance_date<= '%s'" % filters["to_date"]

	if filters.get("company"): conditions += " and la.company = '%s'" % filters["company"]	
	#if filters.get("employee"): conditions += " and att.employee= '%s'" % filters["employee"]
	if filters.get("department"): conditions += " and la.department= '%s'" % filters["department"]
	if filters.get("designation"): conditions += " and emp.designation='%s'" % filters["designation"]
	# if filters.get("section"): conditions += " and emp.section='%s'" % filters["section"]
	# if filters.get("floor"): conditions += " and emp.floor='%s'" % filters["floor"]
	# if filters.get("facility_or_line"): conditions += " and emp.facility_or_line='%s'" % filters["facility_or_line"]
	# if filters.get("group_name"): conditions += " and emp.group='%s'" % filters["group_name"]
	conditions += " and la.from_date > '%s' and la.to_date< '%s'" %(from_date,to_date)    ##It works


	return conditions, filters
