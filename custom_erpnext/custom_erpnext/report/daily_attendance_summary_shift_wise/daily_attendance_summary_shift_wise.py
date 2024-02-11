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
		_("Shift") + ":Data/:90",
		_("Start Time") + ":Data/:90",
		_("Current Manpower") + ":Data/:90",
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
	result= frappe.db.sql("""SELECT 
    CASE WHEN dep = 1 THEN department ELSE NULL END AS department,
    shift,
    start_time,
	total_manpower_count,
    present_count,
    present_percentage,
    on_leave_count,
    on_leave_percentage,
    adjusted_absent_count,
    adjusted_absent_percentage,
    discharge_count,
    discharge_percentage,
    NULL
FROM (
    SELECT 
        emp.department AS department,
        att.shift AS shift,
        COUNT(*) AS total_manpower_count, 
		CAST(CAST(st.start_time AS Time(0)) AS VARCHAR(5)) As start_time,
        SUM(CASE WHEN att.status IN ('Present', 'Late', 'Half Day') THEN 1 ELSE 0 END) AS present_count,
        CAST((SUM(CASE WHEN att.status IN ('Present', 'Late', 'Half Day') THEN 1 ELSE 0 END) / COUNT(*) * 100) AS INT) AS present_percentage,
        SUM(CASE WHEN att.status = 'On Leave' THEN 1 ELSE 0 END) AS on_leave_count,
        CAST((SUM(CASE WHEN att.status = 'On Leave' THEN 1 ELSE 0 END) / COUNT(*) * 100) AS INT) AS on_leave_percentage,
        SUM(CASE WHEN att.status = 'Absent' THEN 1 ELSE 0 END) - SUM(CASE WHEN emp.status_condition IN ('Discharge', 'Discontinue', 'Resign') THEN 1 ELSE 0 END) AS adjusted_absent_count,
        CAST(((SUM(CASE WHEN att.status = 'Absent' THEN 1 ELSE 0 END) - SUM(CASE WHEN emp.status_condition IN ('Discharge', 'Discontinue', 'Resign') THEN 1 ELSE 0 END)) / COUNT(*) * 100) AS INT) AS adjusted_absent_percentage,
        SUM(CASE WHEN emp.status_condition IN ('Discharge', 'Discontinue', 'Resign') THEN 1 ELSE 0 END) AS discharge_count,
        CAST((SUM(CASE WHEN emp.status_condition IN ('Discharge', 'Discontinue', 'Resign') THEN 1 ELSE 0 END) / COUNT(*) * 100) AS INT) AS discharge_percentage,
        ROW_NUMBER() OVER (PARTITION BY emp.department ORDER BY emp.department) AS dep
    FROM 
        tabEmployee emp
    LEFT JOIN 
        tabAttendance att ON emp.name = att.employee
	JOIN 
		`tabShift Type` st ON att.shift=st.name
	where %s
    GROUP BY 
        emp.department,
        att.shift
) AS sub;

	
	""" 
	% conditions,
	as_list=1) 

	total_column=len(result) or 1
	total_row = ["Total","",""]
	for i in range(3,13):
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
	if filters.get("date"): conditions += " att.attendance_date = '%s' or null" % filters["date"]
	if filters.get("company"): conditions += " and att.company= '%s'" % filters["company"]
	# if filters.get("date"): conditions += " and emp.relieving_date>='01-01-2024'"

	return conditions, filters



 #py file of sample report given by Ideal
# # Copyright (c) 2024, Lithe-Tech Limited and contributors
# # For license information, please see license.txt

# import frappe
# #import datetime
# from datetime import datetime, timedelta
# from frappe import _


# def execute(filters= None):
# 	if not filters:
# 		filters = {}
# 	columns = get_columns()
# 	data = get_data(filters)
# 	return columns, data

# def get_columns():
# 	return [
# 		_("Department") + ":Data/:120",
# 		_("Shift Name") + "Data/:90",
# 		_("Current Manpower") + ":Data/:90",
# 		_("Day") + ":Data/:90",
# 		_("Night") + ":Data/:90",
# 		_("Person") + ":Data/:90",
# 		_("Parcentage") + ":Data/:90",
# 		_("Person ") + ":Data/:90",
# 		_("Parcentage ") + ":Data/:90",
# 		_(" Person") + ":Data/:90",
# 		_(" Parcentage") + ":Data/:90",
# 		_("Person.") + ":Data/:90",
# 		_("Parcentage.") + ":Data/:90",
# 		_("Remarks") + ":Data/:120",
		
# 	]

# def get_data(filters):
# 	conditions, filters = get_conditions(filters)
# 	result= frappe.db.sql("""select DISTINCT emp.department,DISTINCT att.shift,
# 	SUM(CASE WHEN att.is_night = 'No' THEN 1 ELSE 0 END), SUM(CASE WHEN att.is_night = 'Yes' THEN 1 ELSE 0 END), 
# 	SUM(CASE WHEN att.status in ('Present','Late','Half Day') THEN 1 ELSE 0 END),
# 	CAST((SUM(CASE WHEN att.status in ('Present','Late','Half Day') THEN 1 ELSE 0 END)/count(*)*100) as int),
# 	SUM(CASE WHEN att.status in ('On Leave') THEN 1 ELSE 0 END),
# 	CAST((SUM(CASE WHEN att.status in ('On Leave') THEN 1 ELSE 0 END)/count(*)*100) as int),
# 	SUM(CASE WHEN att.status= 'Absent' THEN 1 ELSE 0 END)-SUM(CASE WHEN emp.status_condition in ('Discharge','Discontinue','Resign') THEN 1 ELSE 0 END),
# 	CAST(((SUM(CASE WHEN att.status in ('Absent') THEN 1 ELSE 0 END)-SUM(CASE WHEN emp.status_condition in ('Discharge','Discontinue','Resign') THEN 1 ELSE 0 END))/count(*)*100) as int),
# 	SUM(CASE WHEN emp.status_condition in ('Discharge','Discontinue','Resign') THEN 1 ELSE 0 END),	
# 	CAST((SUM(CASE WHEN emp.status_condition in ('Discharge','Discontinue','Resign') THEN 1 ELSE 0 END)/count(*)*100) as int),
# 	null
# 	FROM tabEmployee emp
# 	left JOIN tabAttendance att ON emp.name=att.employee
# 	where %s
					
# 	Group BY emp.department,att.shift""" 
# 	% conditions,
# 	as_list=1) 

# 	total_column=len(result) or 1
# 	total_row = ["Total",""]
# 	for i in range(2,13):
# 		if i==12 or i==13:
# 			total_row.append(None)
# 		elif i in (5,7,9,11):
# 			column_total = str(round(sum(row[i] for row in result) / total_column, 1)) + '%'
# 			total_row.append(column_total)		
# 		else:
# 			column_total = sum(row[i] for row in result)
# 			total_row.append(column_total)
# 	result.append(total_row)

# 	return result



# def get_conditions(filters):
# 	conditions="" 
# 	if filters.get("date"): conditions += " att.attendance_date = '%s'" % filters["date"]
# 	if filters.get("company"): conditions += " and att.company= '%s'" % filters["company"]
# 	# if filters.get("date"): conditions += " and emp.relieving_date>='01-01-2024'"

# 	return conditions, filters
