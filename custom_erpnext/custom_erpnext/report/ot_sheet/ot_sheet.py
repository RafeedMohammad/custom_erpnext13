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


def get_columns(filters):
    columns = []

    if filters.group_by:
        columns = [_(filters.group_by) + ":Link/Branch:120"]

    # Add department as the first column
    columns += [_("Department") + ":Link/Department:120", _("Employee") + ":Data:120", _("Employee Name") + ":Data/:120"]

    # Get all days in the month, check for valid number of days
    try:
        days = []
        for day in range(filters["total_days_in_month"]):
            date = str(filters.year) + "-" + str(filters.month) + "-" + str(day + 1)
            day_name = day_abbr[getdate(date).weekday()]
            days.append(cstr(day + 1) + " " + day_name + "::65")

        if not filters.summarized_view:
            columns += days
        
        # Add Total OT column at the end
        columns += [_("Total") + "::65"]
    except KeyError:
        frappe.throw(_("Missing required filter parameters (month/year)"))
    
    return columns, days



def add_data(employee_map, att_map, filters, conditions):
    record = []
    emp_att_map = {}

    # Create a map for departments
    department_map = {}

    # Group employees by department
    for emp in employee_map:
        emp_det = employee_map.get(emp)
        if not emp_det or emp not in att_map:
            continue

        # Group employees by department
        department = emp_det.department
        if department not in department_map:
            department_map[department] = []

        row = []
        if filters.group_by:
            row += [" "]

        # Add employee details
        row += [emp, emp_det.employee_name]

        emp_status_map = []
        total_ot = 0
        for day in range(filters["total_days_in_month"]):
            ot = att_map.get(emp).get(day + 1)
            if ot == None:
                ot = 0
            total_ot += ot
            emp_status_map.append(ot)

        # For non-summarized view, add the attendance for each day
        if not filters.summarized_view:
            row += emp_status_map

        # Add total OT for the employee
        row += [total_ot,""]

        # Ensure the row length matches the expected number of columns
        if len(row) != len(get_columns(filters)[0]):
            frappe.throw(_("Mismatch between row data and columns. Row length: {} vs Columns length: {}.".format(len(row), len(get_columns(filters)[0]))))

        # Add employee row to the corresponding department
        department_map[department].append(row)
        emp_att_map[emp] = emp_status_map

    # Now construct the final record list where each department's employees are grouped together
    header_row = [_("Department")] + [_("Employee"), _("Employee Name")] + [f"{day+1} {day_abbr[day % 7]}" for day in range(filters["total_days_in_month"])] + [_("Total")]
    
    # record.append(header_row)  # Add the header row

    # Add each department and its employees
    for department in department_map:
        # First, add a department row with no employee data
        record.append([department] + [""] * (len(header_row) - 1))  # Add department name only, with placeholders for employees

        # Add employees under this department
        for emp_row in department_map[department]:
            record.append([""] + emp_row[0:])  # Add department and employee data

    return record, emp_att_map


def get_attendance_list(conditions, filters):
	type = frappe.db.get_value('User', frappe.session.user, 'type')
	if type is None or float(type)>11:
		hours_for_ot=34
	else:
		hours_for_ot=float(type)
		conditions += " and status not in ('Holiday','Weekly Off')"
	departments = frappe.db.get_list("Department", pluck="name", order_by="name")
	# for department in departments:
	attendance_list = frappe.db.sql(
		"""select employee, day(attendance_date) as day_of_month,
	CASE when rounded_ot>%s then %s else rounded_ot end as ot,
	status from tabAttendance where docstatus = 1 %s order by employee, attendance_date
	"""
		% (hours_for_ot, hours_for_ot, conditions),
		filters,
		as_dict=1,
	)

	if not attendance_list:
		msgprint(_("No attendance record found"), alert=True, indicator="orange")

	att_map = {}
	for d in attendance_list:
		att_map.setdefault(d.employee, frappe._dict()).setdefault(d.day_of_month, "")
		att_map[d.employee][d.day_of_month] = d.ot

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
		holiday_list from `tabEmployee` where company = %s and ot_enable = 'Yes' """ % frappe.db.escape(
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
