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
from datetime import datetime

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

	employee_list = frappe.get_list(
		"Employee", fields=["employee", "employee_name"], filters=filters, order_by="employee_name"
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
def mark_employee_attendance2(employee_list,checkin_time=None):
	checkin_time1=datetime.strptime(str(checkin_time), "%Y-%m-%d %H:%M:%S") 
	
	employee_list = json.loads(employee_list)
	for employee in employee_list:

		company = frappe.db.get_value("Employee", employee["employee"], "Company", cache=True)
		

		bulk_checkin_tool_doc = frappe.get_doc(
			dict(
				doctype = "Employee Checkin",
				employee = employee.get("employee"),
				employee_name=employee.get("employee_name"),
				company = company,
				time=random_date(checkin_time1-timedelta(minutes=10),checkin_time1+timedelta(minutes=10))
			)
		)
		
		bulk_checkin_tool_doc.insert()
		bulk_checkin_tool_doc.save()

	


def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)

