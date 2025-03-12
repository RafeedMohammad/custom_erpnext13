# Copyright (c) 2024, Lithe-Tech Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	# columns, data = [], []
	if not filters:
		filters = {}
	columns = get_columns()
	data = get_attendance(filters)
	return columns, data

def get_columns():
	return [
		_("Employee") + ":Data/:120",
		_("Department") + ":Data/:120",
		_("From Date") + ":Date/:120",
		_("To Date") + ":Date/:120",
		# _("Shift") + ":Data/Attendance:120",
		# _("Status") + ":Data/:120",	
		_("Total Absent") + ":Data/:120",
		# _("View") + ":Link/Report"

	]

def get_attendance(filters):
	conditions, filters = get_conditions(filters)
	# result= frappe.db.sql("""select DISTINCT att.attendance_date, att.employee, att.shift, att.status, att.department, count(att.status)
	# FROM tabAttendance as att
	# INNER JOIN tabEmployee as emp ON emp.name = att.employee  	
	# where %s and att.status='Absent'
	# group by att.employee ORDER BY att.attendance_date desc  """ 
	# % conditions, as_list=1)

	result=frappe.db.sql("""
	SELECT 
    employee,
	department,
    MIN(attendance_date) AS start_date,
    MAX(attendance_date) AS end_date,
	COUNT(*) AS absence_days
	FROM (
    SELECT
        att.employee,
		att.department,
        att.attendance_date,
					  
        DATE_SUB(att.attendance_date, INTERVAL ROW_NUMBER() OVER (PARTITION BY att.employee ORDER BY att.attendance_date) DAY) AS grp
    FROM
        tabAttendance att
		INNER JOIN tabEmployee as emp ON emp.name = att.employee 
    WHERE
        %s and att.status in ('Absent','Weekly Off','Holiday') 
) AS absent_days
GROUP BY
    employee,
    grp
HAVING
    COUNT(*) >= %s;


	"""% (conditions,filters["minimum_days"]), as_list=1)

	return result

def get_conditions(filters):
    conditions="" 
    if filters.get("from_date"): conditions += " att.attendance_date>= '%s'" % filters["from_date"]
    if filters.get("to_date"): conditions += " and att.attendance_date<= '%s'" % filters["to_date"]
    if filters.get("employee"): conditions += " and att.employee= '%s'" % filters["employee"]
    if filters.get("company"): conditions += " and att.company= '%s'" % filters["company"]
    if filters.get("department"): conditions += " and att.department= '%s'" % filters["department"]
    if filters.get("designation"): conditions += " and emp.designation='%s'" % filters["designation"]
    if filters.get("shift"): conditions += " and att.shift='%s'" % filters["shift"]
    if filters.get("section"): conditions += " and emp.section='%s'" % filters["section"]
    if filters.get("floor"): conditions += " and emp.floor='%s'" % filters["floor"]
    if filters.get("facility_or_line"): conditions += " and emp.facility_or_line='%s'" % filters["facility_or_line"]
    if filters.get("group_name"): conditions += " and emp.group='%s'" % filters["group_name"]


    return conditions, filters