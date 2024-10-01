# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class ShiftAssignmentTool(Document):
	pass





@frappe.whitelist()
def get_employees(date, shift = None , department=None, designation=None, floor=None, facility_or_line=None, section=None, group=None, company=None, employee_id=None):
	attendance_not_marked = []
	attendance_marked = []
	# filters = {"status": "Active", "emp.date_of_joining": ["<=", date,],"sa.start_date": ["<=", date,],"sa.end_date": [">=", date,]}

	# for field, value in {"default_shift": shift, "department": department, "designation": designation, "floor": floor, "facility_or_line":facility_or_line, "section":section, "group":group, "company": company, "employee": employee_id }.items():
	# 	if value:
	# 		filters[field] = value

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


	employee_list = frappe.db.sql(
	"""
	select DISTINCT emp.name as employee,  emp.employee_name as employee_name, ifnull(sa.shift_type,emp.default_shift) as shift,sa.start_date as start_date, sa.end_date as end_date

	FROM tabEmployee emp
	LEFT JOIN `tabShift Assignment` sa ON emp.name = sa.employee and %s

	 %s	
	""" 
		%(join_condition,conditions),
		as_list=1)
	
	# employee_list = frappe.db.sql(
	# """
	# select emp.name as employee,  emp.employee_name as employee_name

	# FROM emp emp
	# """ 
	# 	,
	# 	as_list=1)
	# marked_employee = {}
	#frappe.publish_realtime('msgprint', employee_list)


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
def mark_employee_new_shift_assignment(employee_list, shift, from_date, to_date, company=None):

	employee_list = json.loads(employee_list)
	frappe.publish_realtime('msgprint',str(employee_list))
	for employee in employee_list:

		#company = frappe.db.get_value("Employee", employee["employee"], "Company", cache=True)
		

		shift_assignemt_doc = frappe.get_doc(
			dict(
				doctype = "Shift Assignment",
				employee = employee[0],#.get("employee"),
				employee_name=employee[1],#.get("employee_name"),
				shift_type = shift,
				start_date = from_date,
				end_date = to_date,
				#company = company,
			)
		)
		
		shift_assignemt_doc.insert()
		shift_assignemt_doc.submit()
