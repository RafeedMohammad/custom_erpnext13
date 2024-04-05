# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import json

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class AttendanceAdjustmentTool(Document):
	pass


@frappe.whitelist()
def get_employees(date, shift = None, status=None,leave_types=None, department=None, designation=None, floor=None, facility_or_line=None, group=None, company=None, employee_id=None):
	attendance_not_marked = []
	attendance_marked = []
	# filters = {"status": "Active", "emp.date_of_joining": ["<=", date,],"sa.start_date": ["<=", date,],"sa.end_date": [">=", date,]}

	# for field, value in {"default_shift": shift, "department": department, "designation": designation, "floor": floor, "facility_or_line":facility_or_line, "section":section, "group":group, "company": company, "employee": employee_id }.items():
	# 	if value:
	# 		filters[field] = value

	conditions="" 


	
	#if company: conditions += " and emp.company= '%s'" %company
	if employee_id: conditions += " and emp.employee= '%s'" % employee_id
	if department: conditions += " and emp.department= '%s'" % department
	if designation: conditions += " and emp.designation='%s'" % designation
	if shift: conditions += " and att.shift='%s'" % shift
	if status: conditions += " and att.status='%s'" % status
	if leave_types: conditions += " and att.leave_type='%s'" % leave_types
	# if section: conditions += " and emp.section='%s'" % section
	if floor: conditions += " and emp.floor='%s'" % floor
	if facility_or_line: conditions += " and emp.facility_or_line='%s'" % facility_or_line
	
	join_condition=""
	if date: join_condition += "att.attendance_date='"+date+"'"
	# if group_name: conditions += " and emp.group='%s'" % group_name
	# if status: conditions += " and .status='%s'" % status


	employee_list = frappe.db.sql(
	"""
	select DISTINCT emp.name as employee,  emp.employee_name as employee_name,att.attendance_date,att.status,att.leave_type,att.shift

	FROM tabEmployee emp
	LEFT JOIN `tabAttendance` att ON emp.name = att.employee and %s
	WHERE emp.status = "Active"
	 %s	
	""" 
		%(join_condition,conditions),
		as_list=1)
	
	return {"marked":employee_list, "unmarked": employee_list}
@frappe.whitelist()
def mark_employee_attendance(employee_list, status, date, leave_type=None, company=None):

	employee_list = json.loads(employee_list)
	for employee in employee_list:

		if status == "On Leave" and leave_type:
			leave_type = leave_type
		else:
			leave_type = None

		duplicate = frappe.db.exists(
			"Attendance",
			{"employee": employee[0], "attendance_date": date, "docstatus": ("!=", "2")},
		)
		if not duplicate:
			attendance = frappe.get_doc(
				dict(
					doctype="Attendance",
					employee = employee[0],#.get("employee"),
					employee_name=employee[1],#.get("employee_name")
					attendance_date=date,#getdate(date),
					status=status,
					leave_type=leave_type,
					company=company,
					late_entry_duration=0,
					overtime=0,
				)
			)
			attendance.insert()
			attendance.submit()
		else:		
			previous_attendance_name=frappe.db.get_value("Attendance",{"attendance_date":date,"employee":employee[0]},'name')

			attendance=frappe.db.set_value('Attendance', previous_attendance_name,{'leave_type':leave_type,'status':status}, update_modified=True)
			# attendance = frappe.get_doc('Attendance',previous_attendance_name).save()

