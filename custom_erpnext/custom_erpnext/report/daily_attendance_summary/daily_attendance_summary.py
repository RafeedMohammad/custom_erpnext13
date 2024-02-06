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
		_("Section") + ":Data/:120",
		_("Current Manpower") + ":Data/:90",
		_("Day") + ":Data/:90",
		_("Night") + ":Data/:90",
		_("Person") + ":Data/:90",
		_("Parcentage") + ":Data/:90",
		_("Person ") + ":Data/:90",
		_("Parcentage ") + ":Data/:90",
		_(" Person") + ":Data/:90",
		_(" Parcentage") + ":Data/:90",
		_("Person.") + ":Data/:90",
		_("Parcentage.") + ":Data/:90",
		_("Remarks") + ":Data/:120",
		
	]

def get_data(filters):
	conditions, filters = get_conditions(filters)
	result= frappe.db.sql("""select DISTINCT emp.section, count(*),
	SUM(CASE WHEN att.is_night = 'No' THEN 1 ELSE 0 END), SUM(CASE WHEN att.is_night = 'Yes' THEN 1 ELSE 0 END), 
	SUM(CASE WHEN att.status in ('Present','Late','Half Day') THEN 1 ELSE 0 END),
	CAST((SUM(CASE WHEN att.status in ('Present','Late','Half Day') THEN 1 ELSE 0 END)/count(*)*100) as int),
	SUM(CASE WHEN att.status in ('On Leave') THEN 1 ELSE 0 END),
	CAST((SUM(CASE WHEN att.status in ('On Leave') THEN 1 ELSE 0 END)/count(*)*100) as int),
	SUM(CASE WHEN att.status= 'Absent' THEN 1 ELSE 0 END)-SUM(CASE WHEN emp.status_condition in ('Discharge','Discontinue','Resign') THEN 1 ELSE 0 END),
	CAST(((SUM(CASE WHEN att.status in ('Absent') THEN 1 ELSE 0 END)-SUM(CASE WHEN emp.status_condition in ('Discharge','Discontinue','Resign') THEN 1 ELSE 0 END))/count(*)*100) as int),
	SUM(CASE WHEN emp.status_condition in ('Discharge','Discontinue','Resign') THEN 1 ELSE 0 END),	
	CAST((SUM(CASE WHEN emp.status_condition in ('Discharge','Discontinue','Resign') THEN 1 ELSE 0 END)/count(*)*100) as int),
	null
	FROM tabEmployee emp
	left JOIN tabAttendance att ON emp.name=att.employee
	where %s
					
	Group BY emp.section""" 
	% conditions,
	as_list=1) 

	total_column=len(result) or 1
	total_row = ["Total"]
	for i in range(1,13):
		if i==12 or i==13:
			total_row.append(None)
		elif i in (5,7,9,11):
			column_total = str(round(sum(row[i] for row in result) / total_column, 1)) + '%'
			total_row.append(column_total)		
		else:
			column_total = sum(row[i] for row in result)
			total_row.append(column_total)
	result.append(total_row)

	return result



def get_conditions(filters):
	conditions="" 
	if filters.get("date"): conditions += " att.attendance_date = '%s'" % filters["date"]
	if filters.get("company"): conditions += " and att.company= '%s'" % filters["company"]
	# if filters.get("date"): conditions += " and emp.relieving_date>='01-01-2024'"

	return conditions, filters
