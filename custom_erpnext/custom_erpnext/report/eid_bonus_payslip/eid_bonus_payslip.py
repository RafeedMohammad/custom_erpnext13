from datetime import datetime,date
import frappe
from frappe import _
from frappe.utils import getdate


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_result(filters)

    return columns, data

def get_columns():
    return [
        _("Employee") + ":Data:200",
        _("Employee Name") + ":Data:200",
		        
        _("Designation") + ":Data:90",
		_("Department") + ":Data:90",
        _("Joining_Date") + ":Data:200",
        # _("Service Length") + ":Data:200",
        _("Gross Salary") + ":Currency:100",# named base in my system
        _("Stamp") + ":Currency:100",
        _("Payable (Basic)") + ":Currency:100",
        # _("Signature_&_Stamp") + ":Text:10",

    ]

# def get_data(filters):
#     data = []
#     departments = frappe.db.get_list("Department", pluck="name", order_by="name")

#     for department in departments:
#         bonus_data = get_result(filters, department)

#         if not bonus_data:  # Skip if no data is found
#             continue

#         # Add department name as a separate row
#         # data.append({"department": department})

#         # total_base = 0
#         # total_stamp = 0
#         # total_basic = 0

#         # for row in bonus_data:
#         #     data.append(row)
#         #     total_base += row[5] or 0  # Sum Base column
#         #     total_stamp += row[6] or 0  # Sum Stamp column
#         #     total_basic += row[7] or 0  # Sum Basic column

#         # # Summarizing the department-level totals
#         # total_row = ["Total", "Total", len(bonus_data), None,None, total_base, total_stamp, total_basic]
#         # data.append(total_row)

#     return data

def get_result(filters):
	conditions, filters = get_conditions(filters)
	result = frappe.db.sql("""
   SELECT 
    ssa.employee,
    ssa.employee_name,
	emp.designation,
    emp.department,
	emp.date_of_joining,
    ssa.base,
	(CASE WHEN emp.salary_mode='Cash' THEN SUM(CASE WHEN sd.abbr = 'ST' THEN sd.amount ELSE 0 END) ELSE 0 END) as stamp,				
    round(((ssa.base - SUM(CASE WHEN sd.abbr = 'DM' THEN sd.amount ELSE 0 END)) / 1.5)-(CASE WHEN emp.salary_mode='Cash' THEN SUM(CASE WHEN sd.abbr = 'ST' THEN sd.amount ELSE 0 END) ELSE 0 END),0) AS basic
	FROM
    `tabSalary Structure Assignment` ssa
JOIN
    `tabSalary Detail` sd ON sd.parent = ssa.salary_structure
JOIN 
    `tabEmployee` emp ON emp.name=ssa.employee
WHERE
    ssa.salary_structure IS NOT NULL 
    AND ssa.from_date = (
        SELECT MAX(from_date) 
        FROM `tabSalary Structure Assignment` 
        WHERE employee = ssa.employee
		 
    )
    AND  %s
	and ssa.docstatus = 1				
GROUP BY
    ssa.employee, ssa.employee_name, emp.status, ssa.base
ORDER BY 
    ssa.employee;

"""% (conditions), as_list=True)

	return result


def get_conditions(filters):
	conditions="" 
	if filters.get("company"): conditions += " emp.company= '%s'" % filters["company"]
	if filters.get("employee"): conditions += " and emp.employee= '%s'" % filters["employee"]
	if filters.get("from_date"): conditions += " and TIMESTAMPDIFF(MONTH, emp.date_of_joining, '%s')>=6 " % filters["from_date"]

	if filters.get("department"): conditions += " and emp.department= '%s'" % filters["department"]
	if filters.get("designation"): conditions += " and emp.designation='%s'" % filters["designation"]
	# if filters.get("shift"): conditions += " and att.shift='%s'" % filters["shift"]
	if filters.get("section"): conditions += " and emp.section='%s'" % filters["section"]
	if filters.get("floor"): conditions += " and emp.floor='%s'" % filters["floor"]
	if filters.get("facility_or_line"): conditions += " and emp.facility_or_line='%s'" % filters["facility_or_line"]
	if filters.get("group_name"): conditions += " and emp.group='%s'" % filters["group_name"]
	if filters.get("grade"): conditions += " and emp.grade='%s'" % filters["grade"]
	if filters.get("employment_type"): conditions += " and emp.employment_type='%s'" % filters["employment_type"]

	if filters.get("mode_of_payment"): conditions += " and emp.salary_mode='%s'" % filters["mode_of_payment"]
	if filters.get("bank"): conditions += " and emp.bank='%s'" % filters["bank"]
	if filters.get("employee_type"):
		if (filters["employee_type"]=="Inactive"):
			conditions += "and emp.status='Inactive'"
		if (filters["employee_type"]=="Active"):
			conditions += " and emp.status='Active' "
		if (filters["employee_type"]=="Left"):
			conditions += " and emp.status='Left'"

	# if filters.get("employee"): conditions += " and ssa.employee in %s'" % filters["employee"]


	# if filters.get("department"): conditions += " and ssa.department= '%s'" % filters["department"]

	# #frappe.publish_realtime('msgprint', 'condition = '+conditions)		
	# conditions=conditions.replace("]'", ")")
	# conditions=conditions.replace("[", "(")
	
	return conditions, filters