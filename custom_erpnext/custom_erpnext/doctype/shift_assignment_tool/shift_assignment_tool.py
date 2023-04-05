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
	filters = {"status": "Active", "date_of_joining": ["<=", date]}

	for field, value in {"default_shift": shift, "department": department, "designation": designation, "floor": floor, "facility_or_line":facility_or_line, "section":section, "group":group, "company": company, "employee": employee_id }.items():
		if value:
			filters[field] = value

	employee_list = frappe.get_list(
		"Employee", fields=["employee", "employee_name"], filters=filters, order_by="employee asc"
	)
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
def mark_employee_attendance1(employee_list, shift, from_date, to_date, company=None):

	employee_list = json.loads(employee_list)
	for employee in employee_list:

		company = frappe.db.get_value("Employee", employee["employee"], "Company", cache=True)
		

		shift_assignemt_doc = frappe.get_doc(
			dict(
				doctype = "Shift Assignment",
				employee = employee.get("employee"),
				employee_name=employee.get("employee_name"),
				shift_type = shift,
				start_date = from_date,
				end_date = to_date,
				company = company,
			)
		)
		
		shift_assignemt_doc.insert()
		shift_assignemt_doc.submit()
