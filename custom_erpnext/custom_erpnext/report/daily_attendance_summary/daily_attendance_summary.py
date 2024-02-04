# Copyright (c) 2024, Lithe-Tech Limited and contributors
# For license information, please see license.txt

import frappe
#import datetime
from datetime import datetime, timedelta
from frappe import _


def execute(filters= None):
	if not filters:
		filters = {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		_("Department") + ":Data/:120",
		_("Current Manpower") + ":Data/:120",
		_("Day") + ":Data/:120",
		_("Night") + ":Data/:120",
		_("Person") + ":Data/:120",
		_("Parcentage") + ":Data/:120",
		_("Person") + ":Data/:120",
		_("Parcentage") + ":Data/:120",
		_("Person") + ":Data/:120",
		_("Parcentage") + ":Data/:120",
		_("Person") + ":Data/:120",
		_("Parcentage") + ":Data/:120",
		#_("Remarks") + ":Data/:120",
		
	]

def get_data(filters):
	conditions, filters = get_conditions(filters)
	result= frappe.db.sql("""select DISTINCT emp.department, count(*),
	SUM(CASE WHEN att.is_night = 'No' THEN 1 ELSE 0 END), SUM(CASE WHEN att.is_night = 'Yes' THEN 1 ELSE 0 END), 
	SUM(CASE WHEN att.status in ('Present','Late','Half Day') THEN 1 ELSE 0 END),
	CAST((SUM(CASE WHEN att.status in ('Present','Late','Half Day') THEN 1 ELSE 0 END)/count(*)*100) as int),
	SUM(CASE WHEN att.status='Absent' THEN 1 ELSE 0 END),
	CAST((SUM(CASE WHEN att.status in ('Absent') THEN 1 ELSE 0 END)/count(*)*100) as int),
	SUM(CASE WHEN att.status in ('On Leave') THEN 1 ELSE 0 END),
	CAST((SUM(CASE WHEN att.status in ('On Leave') THEN 1 ELSE 0 END)/count(*)*100) as int),
	count(*)-SUM(CASE WHEN att.status in ('Absent','On Leave','Present','Late','Half Day') THEN 1 ELSE 0 END),
	SUM(CASE WHEN emp.status in ('Inactive') THEN 1 ELSE 0 END)			   
		
	FROM tabAttendance as att
	JOIN tabEmployee as emp ON emp.name=att.employee
	where %s
					
	Group BY emp.department""" 
		% conditions,
		as_list=1)				   	
	return result



def get_conditions(filters):
	conditions="" 
	if filters.get("date"): conditions += " att.attendance_date = '%s'" % filters["date"]
	if filters.get("company"): conditions += " and att.company= '%s'" % filters["company"]
	# if filters.get("date"): conditions += " and emp.relieving_date>='01-01-2024'"

	return conditions, filters
