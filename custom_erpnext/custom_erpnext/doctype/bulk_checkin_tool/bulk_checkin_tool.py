# Copyright (c) 2023, Lithe-Tech Limited and contributors
# For license information, please see license.txt

# import frappe
# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
import json

import datetime
import frappe
from frappe.model.document import Document
from frappe.utils import getdate
from datetime import datetime,date, time

from random import randrange
from datetime import timedelta

class BulkCheckinTool(Document):
	pass


@frappe.whitelist()
def get_employees(date, shift = None , department=None, designation=None, floor=None, facility_or_line=None, section=None, group=None, company=None, employee_id=None):
	attendance_not_marked = []
	attendance_marked = []
	filters = {"status": "Active", "date_of_joining": ["<=", date]}

	for field, value in {"default_shift": shift, "department": department, "designation": designation, "floor": floor, "facility_or_line":facility_or_line, "section":section, "group":group, "company": company, "employee": employee_id }.items():
		if value:
			filters[field] = value

	
	conditions="" 
	data = json.loads(employee_id)

	# Extract just the "employee" values
	employees = [item["employee"] for item in data]


	
	#if company: conditions += " and emp.company= '%s'" %company
	if len(employees)>0: conditions += " where emp.employee in %s and emp.status='Active'" % employees
	else:conditions +=" where emp.status = 'Active'"
	if department: conditions += " and emp.department= '%s'" % department
	if designation: conditions += " and emp.designation='%s'" % designation
	if shift: conditions += " and ifnull(sa.shift_type,emp.default_shift)='%s'" % shift
	if section: conditions += " and emp.section='%s'" % section
	if floor: conditions += " and emp.floor='%s'" % floor
	if facility_or_line: conditions += " and emp.facility_or_line='%s'" % facility_or_line
	
	if len(employees)>0:
		conditions=conditions.replace("]", ")")
		conditions=conditions.replace("[", "(")
	
	join_condition=""
	if date: join_condition += "'"+date+"' between sa.start_date and sa.end_date and sa.docstatus=1 and sa.status='Active'"
	# if group_name: conditions += " and emp.group='%s'" % group_name
	# if status: conditions += " and .status='%s'" % status

	# employee_list = frappe.get_list(
	# 	"Employee", fields=["employee", "employee_name"], filters=filters, order_by="employee asc"
	# )
	employee_list = frappe.db.sql(
	"""
	select emp.name as employee,  emp.employee_name as employee_name, ifnull(sa.shift_type,emp.default_shift) as shift

	FROM tabEmployee emp
	LEFT JOIN `tabShift Assignment` sa ON emp.name = sa.employee and %s

		 %s	
	""" 
		%(join_condition,conditions),
		as_list=1)
	# marked_employee = {}

	# for emp in frappe.get_list(
	# 	"Attendance", fields=["employee", "status"], filters={"attendance_date": date}
	# ):
	# 	marked_employee[emp["employee"]] = emp["status"]

	# for employee in employee_list:
	# 	employee["status"] = marked_employee.get(employee["employee"])
	# 	if employee["employee"] not in marked_employee:
	# 		attendance_not_marked.append(employee)
	# 	else:
	# 		attendance_marked.append(employee)
	#return {"marked": attendance_marked, "unmarked": attendance_not_marked}
	return {"marked":employee_list, "unmarked": employee_list}


@frappe.whitelist()
def mark_employee_attendance2(employee_list,start_date=None,end_date=None,in_time=None,out_time=None):
	# checkin_time1=datetime.strptime(str(checkin_time), "%Y-%m-%d %H:%M:%S") 
	#checkin_time1=datetime.strptime(str(checkin_time), "%Y-%m-%d") 
	# checkin_time1= datetime.strptime(str(start_date), "%Y-%m-%d" )+datetime.strptime(str(in_time), "%H:%M:%S")
	
	if end_date is None:
		end_date = start_date
	employee_list = json.loads(employee_list)


    # Ensure start_date and end_date are in the correct format
	start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
	end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Iterate through each date in the range
	while start_date_obj <= end_date_obj:
		if in_time is not None:
			checkin_time_in = datetime.combine(
				start_date_obj, datetime.strptime(in_time, "%H:%M:%S").time()
			)
		if out_time is not None:
			checkin_time_out = datetime.combine(
				start_date_obj, datetime.strptime(out_time, "%H:%M:%S").time()
			)

		
		for employee in employee_list:

			#company = frappe.db.get_value("Employee", employee["employee"], "Company", cache=True)
			if in_time is not None:

				bulk_checkin_tool_doc = frappe.get_doc(
					dict(
						doctype = "Employee Checkin",
						employee = employee[0],
						employee_name=employee[1],
						#company = company,
						time=random_date(checkin_time_in-timedelta(minutes=10),checkin_time_in+timedelta(minutes=10))
					)
				)
				
				bulk_checkin_tool_doc.insert()
				bulk_checkin_tool_doc.save()

			if out_time is not None:
				bulk_checkin_tool_doc = frappe.get_doc(  # for out time
					dict(
						doctype = "Employee Checkin",
						employee = employee[0],
						employee_name=employee[1],
						#company = company,
						time=random_date(checkin_time_out-timedelta(minutes=10),checkin_time_out+timedelta(minutes=10))
					)
				)
			
				bulk_checkin_tool_doc.insert()
				bulk_checkin_tool_doc.save()

		# datetime.strptime(start_date, "%Y-%m-%d").date() += timedelta(days=1)
		start_date_obj += timedelta(days=1)
		


def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)

