
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
		_("Current Manpower") + ":Data/:90",
		_("Shift") + ":Data/:90",
		_("Start Time") + ":Data/:90",
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
	total_manpower_count,
    shift,
    start_time,
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
		COUNT(*) AS total_manpower_count, 
        att.shift AS shift,
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
	total_row = ["Total"]
	for i in range(1,13):
		if i==12 or i==13 or i==2 or i==3:
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