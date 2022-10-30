# Copyright (c) 2022, Lithe-Tech Limited and contributors
# For license information, please see license.txt

# import frappe

import frappe
from frappe import _

def execute(filters=None):
	
	if not filters:
		filters = {}
	columns = get_columns()
	data = get_missing_entry(filters)
	
	return columns, data
def get_columns():
	return [
		_("Department") + ":Data/:120",
		_("ID") + ":Data/:120",
		_("Employee") + ":Link/Employee:120",
		_("Designation") + ":Data/:120",
		_("Shift") + ":Data/:120",
		_("Line") + ":Data/:120",
		_("In Time") + ":Data/Attendance:120"
	]

def get_missing_entry(filters):
	conditions, filters = get_conditions(filters)
	result= frappe.db.sql("""select att.department,att.employee,att.employee_name, 
		emp.designation,att.shift,emp.facility_or_line,
		 TIME(att.in_time),TIME(att.out_time)
		FROM tabAttendance as att
		LEFT JOIN tabEmployee as emp ON emp.name = att.employee 
		where 
		att.docstatus<2  and
		(TIMESTAMPDIFF(minute,  att.in_time, att.out_time)<10 or out_time IS NULL) and (att.status= "Late" or  att.status= "Present" )%s
		""" 
			% conditions, 
			as_list=1)
	return result

def get_conditions(filters):
	conditions="" 
	if filters.get("from_date"): conditions += " and att.attendance_date>= '%s'" % filters["from_date"]
	if filters.get("to_date"): conditions += " and att.attendance_date<= '%s'" % filters["to_date"]	
	if filters.get("company"): conditions += " and att.company = '%s'" % filters["company"]	
	#if filters.get("employee"): conditions += " and att.employee= '%s'" % filters["employee"]
	if filters.get("department"): conditions += " and att.department= '%s'" % filters["department"]
	if filters.get("designation"): conditions += " and emp.designation='%s'" % filters["designation"]
	if filters.get("shift"): conditions += " and att.shift='%s'" % filters["shift"]
	if filters.get("section"): conditions += " and emp.section='%s'" % filters["section"]
	if filters.get("floor"): conditions += " and emp.floor='%s'" % filters["floor"]
	if filters.get("facility_or_line"): conditions += " and emp.facility_or_line='%s'" % filters["facility_or_line"]
	if filters.get("group_name"): conditions += " and emp.group='%s'" % filters["group_name"]


	return conditions, filters
