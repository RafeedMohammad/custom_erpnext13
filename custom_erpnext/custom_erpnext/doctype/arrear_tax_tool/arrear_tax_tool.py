# Copyright (c) 2024, Lithe-Tech Limited and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document
import json

import frappe
from frappe.model.document import Document
# from frappe.utils import getdate
import frappe.realtime
from frappe.utils import add_days, cstr, date_diff, get_first_day, get_last_day, getdate


class ArrearTaxTool(Document):
	pass

@frappe.whitelist()
def get_employees(month=None,year=None, department=None, designation=None, floor=None, facility_or_line=None, section=None, group=None, company=None, employee_id=None):
	attendance_not_marked = []
	attendance_marked = []
	# filters = {"status": "Active", "emp.date_of_joining": ["<=", date,],"sa.start_date": ["<=", date,],"sa.end_date": [">=", date,]}

	# for field, value in {"default_shift": shift, "department": department, "designation": designation, "floor": floor, "facility_or_line":facility_or_line, "section":section, "group":group, "company": company, "employee": employee_id }.items():
	# 	if value:
	# 		filters[field] = value

	conditions="" 
	data = json.loads(employee_id)
	

	from_date = get_first_day(month + "-" + year)
	to_date = get_last_day(month + "-" + year)
	# frappe.publish_realtime('msgprint', str(to_date))

	# # Extract just the "employee" values
	employees = [item["employee"] for item in data]

	if len(employees)>0: conditions += " where ss.employee in %s and " % employees
	else:conditions +=" where "
	if from_date: conditions += " ss.start_date>= '%s'" % from_date
	if to_date: conditions += " and ss.end_date<= '%s'" % to_date
	if company: conditions += " and ss.company= '%s'" %company
	if department: conditions += " and ss.department= '%s'" %department
	if designation: conditions += " and ss.designation='%s'" %designation
	if section: conditions += " and ss.section='%s'" %section
	if floor: conditions += " and ss.floor='%s'" %floor
	if facility_or_line: conditions += " and ss.facility_or_line='%s'" %facility_or_line
	if group: conditions += " and ss.group='%s'" %group

	if len(employees)>0:
		conditions=conditions.replace("]", ")")
		conditions=conditions.replace("[", "(")

	employee_list = frappe.db.sql(
	"""
	select ss.employee, ss.employee_name, ss.income_tax ,ss.arear,ss.other_deduction,ss.posting_date,ss.name

	FROM `tabSalary Slip` ss  %s

		
	""" 
		
		%conditions,as_list=1)
	
	return {"marked":employee_list, "unmarked": employee_list}

@frappe.whitelist()
def update_salary_slip(employee_list):

	employee_list = json.loads(employee_list)
	# frappe.publish_realtime('msgprint',str(employee_list))


	for employee in employee_list:

		doc_dict = {
                'arear':employee['arear'].strip(' ') or 0,
				'income_tax':employee['tax']or 0,
				'other_deduction':employee['other_deduction']or 0,
            }

		#company = frappe.db.get_value("Employee", employee["employee"], "Company", cache=True)
		salary_slip	=	frappe.db.set_value('Salary Slip', employee['employee'][6], {
			'arear':doc_dict['arear'], "income_tax":doc_dict['income_tax'],"other_deduction":doc_dict['other_deduction']}, update_modified=True)
			#Changed Code - End

			#Attendance document with updated values will be saved
		salary_slip = frappe.get_doc('Salary Slip',employee['employee'][6]).save()

