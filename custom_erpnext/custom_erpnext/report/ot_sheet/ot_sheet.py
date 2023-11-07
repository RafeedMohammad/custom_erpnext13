# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from calendar import monthrange

import frappe
from frappe import _, msgprint
from frappe.utils import cint, cstr, getdate


day_abbr = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def execute(filters=None):
	if not filters:
		filters = {}

	if filters.hide_year_field == 1:
		filters.year = 2020

	conditions, filters = get_conditions(filters)
	columns, days = get_columns(filters)
	att_map = get_attendance_list(conditions, filters)
	if not att_map:
		return columns, [], None, None




	data = []

	
	emp_map = get_employee_details(filters.group_by, filters.company)
	record, emp_att_map = add_data(
			emp_map,
			att_map,
			filters,
			conditions,
		)
	data += record


	return columns, data





def add_data(
	employee_map, att_map, filters, conditions
):
	record = []
	emp_att_map = {}
	for emp in employee_map:
		emp_det = employee_map.get(emp)
		if not emp_det or emp not in att_map:
			continue

		row = []
		if filters.group_by:
			row += [" "]
		row += [emp,emp_det.employee_name]

		emp_status_map = []
		total_ot=0
		for day in range(filters["total_days_in_month"]):
			ot = att_map.get(emp).get(day + 1)
			if ot==None:
				ot=0
			total_ot=total_ot+ot
			emp_status_map.append(ot)



		if not filters.summarized_view:
			row += emp_status_map

		
		if not filters.get("employee"):
			filters.update({"employee": emp})
			conditions += " and employee = %(employee)s"
		elif not filters.get("employee") == emp:
			filters.update({"employee": emp})

		

			
		row+=[total_ot]
		emp_att_map[emp] = emp_status_map
		record.append(row)
		#record.append(total_ot)

	return record, emp_att_map


def get_columns(filters):

	columns = []

	if filters.group_by:
		columns = [_(filters.group_by) + ":Link/Branch:120"]

	columns += [_("Employee") + ":Data:120",_("Employee Name") + ":Data/:120"]
	days = []
	for day in range(filters["total_days_in_month"]):
		date = str(filters.year) + "-" + str(filters.month) + "-" + str(day + 1)
		day_name = day_abbr[getdate(date).weekday()]
		days.append(cstr(day + 1) + " " + day_name + "::65")
	if not filters.summarized_view:
		columns += days
	columns += [_("Total")+"::65"]

	return columns, days


def get_attendance_list(conditions, filters):
	attendance_list = frappe.db.sql(
		"""select employee, day(attendance_date) as day_of_month,rounded_ot,
		status from tabAttendance where docstatus = 1 %s order by employee, attendance_date"""
		% conditions,
		filters,
		as_dict=1,
	)

	if not attendance_list:
		msgprint(_("No attendance record found"), alert=True, indicator="orange")

	att_map = {}
	for d in attendance_list:
		att_map.setdefault(d.employee, frappe._dict()).setdefault(d.day_of_month, "")
		att_map[d.employee][d.day_of_month] = d.rounded_ot

	return att_map


def get_conditions(filters):
	if not (filters.get("month") and filters.get("year")):
		msgprint(_("Please select month and year"), raise_exception=1)

	filters["total_days_in_month"] = monthrange(cint(filters.year), cint(filters.month))[1]

	conditions = " and month(attendance_date) = %(month)s and year(attendance_date) = %(year)s"

	if filters.get("company"):
		conditions += " and company = %(company)s"
	if filters.get("employee"):
		conditions += " and employee = %(employee)s"
	if filters.get("department"):
		conditions += " and department = %(department)s"

	return conditions, filters


def get_employee_details(group_by, company):
	emp_map = {}
	query = """select name, employee_name, designation, department, branch, company,
		holiday_list from `tabEmployee` where company = %s """ % frappe.db.escape(
		company
	)

	if group_by:
		group_by = group_by.lower()
		query += " order by " + group_by + " ASC"

	employee_details = frappe.db.sql(query, as_dict=1)

	group_by_parameters = []
	if group_by:

		group_by_parameters = list(
			set(detail.get(group_by, "") for detail in employee_details if detail.get(group_by, ""))
		)
		for parameter in group_by_parameters:
			emp_map[parameter] = {}

	for d in employee_details:
		if group_by and len(group_by_parameters):
			if d.get(group_by, None):

				emp_map[d.get(group_by)][d.name] = d
		else:
			emp_map[d.name] = d

	if not group_by:
		return emp_map
	else:
		return emp_map, group_by_parameters


@frappe.whitelist()
def get_attendance_years():
	year_list = frappe.db.sql_list(
		"""select distinct YEAR(attendance_date) from tabAttendance ORDER BY YEAR(attendance_date) DESC"""
	)
	if not year_list:
		year_list = [getdate().year]

	return "\n".join(str(year) for year in year_list)
