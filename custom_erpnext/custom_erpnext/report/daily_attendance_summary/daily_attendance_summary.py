
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
	shifts = frappe.get_all("Shift Type", fields=["name","start_time"],order_by="name")
	#frappe.publish_realtime('msgprint', shif	
	shift_columns = [shift["name"] +" "+ str(shift["start_time"])[:-3].strip().replace(":",".") +":Data/:90" for shift in shifts]
	return [
		_("Department") + ":Data/:120",
		_("Current Manpower") + ":Data/:90",	
		*shift_columns,
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
	shifts = frappe.get_all("Shift Type", fields=["name"],order_by="name")
	
	aggregate_string = ""

	for shift in shifts:
		field_string_for_shift ="SUM(CASE WHEN ifnull(sa.shift_type,emp.default_shift)='"+str(shift["name"])+"' THEN 1 ELSE 0 END),"
		aggregate_string += field_string_for_shift

	att_join_condition=""
	if filters.get("date"): att_join_condition += "AND (att.attendance_date IS NULL OR att.attendance_date ='"+filters["date"]+"')"
	
	sa_join_condition=""
	if filters.get("date"): sa_join_condition += "AND '"+filters["date"]+"' between sa.start_date and sa.end_date and sa.docstatus=1 and sa.status='Active'"


	result= frappe.db.sql("""select DISTINCT emp.department,count(*),
					   %s
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
	left JOIN tabAttendance att ON emp.name=att.employee %s
	left JOIN `tabShift Assignment` sa ON emp.name = sa.employee %s
	where %s
					
	Group BY emp.department""" 
	% (aggregate_string,att_join_condition,sa_join_condition,conditions),
	as_list=1)

	total_column=len(shifts)+11
	rows=len(result)
	# frappe.publish_realtime('msgprint', str(total_column))
	total_row = ["Total"]
	for i in range(1,total_column):
		if i==total_column-1 or i==total_column:
			total_row.append(None)
		elif i in (total_column-2,total_column-4,total_column-6,total_column-8):
			column_total = str(round(sum(row[i] for row in result) / rows, 1)) + '%'
			total_row.append(column_total)		
		else:
			column_total = sum(row[i] for row in result)
			total_row.append(column_total)
	result.append(total_row)

	return result



def get_conditions(filters):
	conditions="" 
	#if filters.get("date"): conditions += " att.attendance_date = '%s' or null" % filters["date"]
	#if filters.get("company"): conditions += "att.company= '%s'" % filters["company"]
	if filters.get("date"): conditions += " emp.status='Active' "

	return conditions, filters