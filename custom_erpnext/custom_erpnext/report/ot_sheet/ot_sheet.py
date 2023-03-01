# Copyright (c) 2023, Lithe-Tech Limited and contributors
# For license information, please see license.txt

# import frappe


import frappe
from frappe import _
from typing import List
from frappe.utils import cint
from calendar import monthrange
from frappe.utils import add_days, cstr, date_diff, get_first_day, get_last_day, getdate


def execute(filters=None):
	if not filters:
		filters = {}
	
	columns = get_columns()
	data = get_summary(filters)
	return columns, data

	
def get_columns():
	return [
		_("Emp No.") + ":Data/:120",
		_("Employee Name") + ":Link/Employee:120",
		_("Designation") + ":Link/Designation:120",
		_("Gross") + ":Currency/Salary Structure Assignment:120",
		_("Basic") + ":Currency/Salary Slip:120",
		_("OT. Hour") + ":Data/Salary Slip:120",
		_("OT. Rate") + ":Data/Salary Slip:120",
		_("OT. Amount") + ":Data/Salary Slip:120",
		_("Signature") + ":Data/Salary Slip:120",
	]
def get_conditions(from_date,to_date,filters):
	conditions="" 
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}
	if filters.get("docstatus"):
		conditions += "ss.docstatus = {0}".format(doc_status[filters.get("docstatus")])


	if from_date: conditions += " and ss.start_date>= '%s'" % from_date
	if to_date: conditions += " and ss.end_date<= '%s'" % to_date
	if filters.get("employee"): conditions += " and ss.employee= '%s'" % filters["employee"]
	if filters.get("company"): conditions += " and ss.company= '%s'" % filters["company"]
	if filters.get("department"): conditions += " and ss.department= '%s'" % filters["department"]
	if filters.get("designation"): conditions += " and ss.designation='%s'" % filters["designation"]
	# if filters.get("shift"): conditions += " and att.shift='%s'" % filters["shift"]
	if filters.get("section"): conditions += " and ss.section='%s'" % filters["section"]
	if filters.get("floor"): conditions += " and ss.floor='%s'" % filters["floor"]
	if filters.get("facility_or_line"): conditions += " and ss.facility_or_line='%s'" % filters["facility_or_line"]
	if filters.get("group_name"): conditions += " and ss.group='%s'" % filters["group_name"]
	if filters.get("grade"): conditions += " and ss.grade='%s'" % filters["grade"]
	# if filters.get("sub_department"): conditions += " and ss.sub_department like '%s'" % filters["sub_department"]


	return conditions, filters

def get_summary(filters):
	from_date = get_first_day(filters["month"] + "-" + filters["year"])
	to_date = get_last_day(filters["month"] + "-" + filters["year"])
	conditions,filters = get_conditions(from_date,to_date,filters)
	return frappe.db.sql("""select ss.employee, ss.employee_name, ss.designation, ss.base_pay, 
	sd.default_amount, ss.overtime_hours, ss.overtime_rate, Round(ss.total_overtime_pay,3),null
	from `tabSalary Slip` as ss join (select * from `tabSalary Detail` group by name) sd   
	on ss.name = sd.parent where %s and sd.salary_component = 'Basic' """ %conditions, filters,as_list = 1)


