import frappe
from frappe import _
from frappe.utils import add_days, cstr, date_diff, get_first_day, get_last_day, getdate


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data

def get_columns():
    return [
        _("Department") + ":Data:90",

        _("Employee") + ":Data:90",
        _("Employee Name") + ":Data:90",
        
        # _("Department") + ":Data:90",
        _("Designation") + ":Data:90",
        _("Joining_Date") + ":Date:90",
        
        _("Gross") + ":Data:90",
        _("Total Present Days") + ":Int:120",

		_("Per Day Payment for EL")+ ":Data:90",
        {"label": _("EL Entitled Days"), "fieldtype": "Float", "width": 120, "precision": 2},
        _("Gross EL Payment")+ ":Data:90",
        _("EL Availed")+":Int:120",
        {"label": _("EL Balance"), "fieldtype": "Float", "width": 120, "precision": 2},
		_("Net EL Payment")+ ":Int:90",
        
        
        _("EL Payment Saved by Availed") + ":Int:120",
        _("Late") + ":Int:120",
        
    ]

def get_data(filters):
    data = []
    departments = frappe.db.get_list("Department", pluck="name", order_by="name")
    for department in departments:
        el_data = get_result(filters,department)
        if len(el_data)==None:
            continue

        if len(el_data) >= 1:
            data.append({"department": department})
        for eldata in el_data:
            data.append(eldata)
    return data

def get_result(filters,department):
    conditions, filters = get_conditions(filters,department)

    result = frappe.db.sql(
    """
    SELECT 
            NULL AS department,
            emp.name AS Employee,
            emp.employee_name AS Employee_name,
            emp.designation AS Designation,
            emp.date_of_joining AS Joining_Date,
            ssa.base AS Gross_Salary,
            COUNT(CASE WHEN att.status IN ('Present','Late') THEN 1 END) AS total_present_days,
            ROUND(ssa.base/30, 0) AS per_day_payment_for_el,
            ROUND(COUNT(CASE WHEN att.status IN ('Present', 'Late') THEN 1 END) / 18, 2) AS el_entitled_days,
            ROUND(ROUND(COUNT(CASE WHEN att.status IN ('Present', 'Late') THEN 1 END) / 18, 2) * (ssa.base/30), 0) AS gross_el_payment,
            COUNT(CASE WHEN att.status = 'On Leave' AND att.leave_type = 'EL' THEN 1 END) AS EL_availed,
            ROUND(COUNT(CASE WHEN att.status IN ('Present', 'Late') THEN 1 END) / 18, 2) - COUNT(CASE WHEN att.status = 'On Leave' AND att.leave_type = 'EL' THEN 1 END) AS EL_Balance,
            ROUND((ROUND(COUNT(CASE WHEN att.status IN ('Present', 'Late') THEN 1 END) / 18, 2) - COUNT(CASE WHEN att.status = 'On Leave' AND att.leave_type = 'EL' THEN 1 END)) * ROUND(ssa.base/30, 0)) AS Net_EL_Payment,
            ROUND(ROUND(ssa.base/30, 0) * COUNT(CASE WHEN att.status = 'On Leave' AND att.leave_type = 'EL' THEN 1 END), 0) AS EL_Payment_Saved_by_Availed,
            COUNT(CASE WHEN att.status = 'Late' THEN 1 END) AS Late
        FROM tabEmployee emp
        LEFT JOIN tabAttendance att ON emp.name = att.employee
        LEFT JOIN `tabSalary Structure Assignment` ssa 
            ON emp.name = ssa.employee 
            AND ssa.from_date = (SELECT MAX(from_date) FROM `tabSalary Structure Assignment` WHERE employee = emp.name)
        WHERE %s
        GROUP BY emp.name, emp.department, emp.designation, emp.date_of_joining, emp.status, ssa.base
        ORDER BY emp.name
""" % (conditions), as_list=1)




    return result

def get_conditions(filters,department):
    conditions="" 
    from_date = get_first_day( "01"+ "-" + filters["year"])
    to_date = get_last_day( "12"+ "-" + filters["year"])
    # if filters.get("from_date"): conditions += " att.attendance_date>= '%s'" % filters["from_date"]
    if filters.get("year"): conditions += " att.attendance_date between '%s' and '%s' and emp.date_of_joining<='%s'" % (from_date,to_date,to_date)
    if department: conditions += " and emp.department= '%s'" % department
    if filters.get("employee"): conditions += " and att.employee= '%s'" % filters["employee"]
    if filters.get("company"): conditions += " and att.company= '%s'" % filters["company"]
    if filters.get("department"): conditions += " and att.department= '%s'" % filters["department"]
    if filters.get("designation"): conditions += " and tabEmployee.designation='%s'" % filters["designation"]
    if filters.get("shift"): conditions += " and att.shift='%s'" % filters["shift"]
    if filters.get("section"): conditions += " and emp.section='%s'" % filters["section"]
    if filters.get("floor"): conditions += " and emp.floor='%s'" % filters["floor"]
    if filters.get("facility_or_line"): conditions += " and emp.facility_or_line='%s'" % filters["facility_or_line"]
    if filters.get("group_name"): conditions += " and emp.group='%s'" % filters["group_name"]
    if filters.get("employee_status"): conditions += " and emp.status='%s'" % filters["employee_status"]

    return conditions, filters