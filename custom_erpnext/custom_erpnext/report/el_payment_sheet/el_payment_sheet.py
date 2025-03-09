import frappe
from frappe import _
from frappe.utils import add_days, cstr, date_diff, get_first_day, get_last_day, getdate


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns(filters)
    data = get_data(filters)

    return columns, data

def get_columns(filters):
    return [
        _("Employee") + ":Data:90",
        _("Employee Name") + ":Data:90",
        
        _("Designation") + ":Data:90",
        _("Department") + ":Data:90",
        _("Joining_Date") + ":Date:90",
        
        _("Gross") + ":Data:90",
        _("Total Present Days") + ":Int:120",

		_("Per Day Payment for EL")+ ":Data:90",
        {"label": _("EL Entitled Days"), "fieldtype": "Float", "width": 120, "precision": 2},
        _("Gross EL Payment")+ ":Data:90",
        _("EL Availed")+":Data:120",
        {"label": _("EL Balance"), "fieldtype": "Float", "width": 120, "precision": 2},
		_("Net EL Payment")+ ":Int:90",
        
        
        _("EL Payment Saved by Availed") + ":Int:120",

        _("CL")+":Data:120",
        _("SL")+":Data:120",

        _("Jan-"+str(filters["year"])[2:])+":Data:120",
        _("Feb-"+str(filters["year"])[2:])+":Data:120",
        _("Mar-"+str(filters["year"])[2:])+":Data:120",
        _("Apr-"+str(filters["year"])[2:])+":Data:120",
        _("May-"+str(filters["year"])[2:])+":Data:120",
        _("Jun-"+str(filters["year"])[2:])+":Data:120",
        _("Jul-"+str(filters["year"])[2:])+":Data:120",
        _("Aug-"+str(filters["year"])[2:])+":Data:120",
        _("Sep-"+str(filters["year"])[2:])+":Data:120",
        _("Oct-"+str(filters["year"])[2:])+":Data:120",
        _("Nov-"+str(filters["year"])[2:])+":Data:120",
        _("Dec-"+str(filters["year"])[2:])+":Data:120",

        _("Late") + ":Int:120",
        
    ]

def get_data(filters):
    conditions, filters = get_conditions(filters)

    result = frappe.db.sql(
    """
    SELECT 
            emp.name AS Employee,
            emp.employee_name AS Employee_name,
            emp.designation AS Designation,
            emp.department As Department,
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
            COUNT(CASE WHEN att.status = 'On Leave' AND att.leave_type = 'CL' THEN 1 END) AS cl,
            COUNT(CASE WHEN att.status = 'On Leave' AND att.leave_type = 'SL' THEN 1 END) AS sl,

            SUM(CASE WHEN MONTH(att.attendance_date) = 1 and att.status = 'Present' THEN 1 ELSE 0 END) AS Jan,
            SUM(CASE WHEN MONTH(att.attendance_date) = 2 and att.status = 'Present' THEN 1 ELSE 0 END) AS Feb,
            SUM(CASE WHEN MONTH(att.attendance_date) = 3 and att.status = 'Present' THEN 1 ELSE 0 END) AS Mar,
            SUM(CASE WHEN MONTH(att.attendance_date) = 4 and att.status = 'Present' THEN 1 ELSE 0 END) AS Apr,
            SUM(CASE WHEN MONTH(att.attendance_date) = 5 and att.status = 'Present' THEN 1 ELSE 0 END) AS May,
            SUM(CASE WHEN MONTH(att.attendance_date) = 6 and att.status = 'Present' THEN 1 ELSE 0 END) AS Jun,
            SUM(CASE WHEN MONTH(att.attendance_date) = 7 and att.status = 'Present' THEN 1 ELSE 0 END) AS Jul,
            SUM(CASE WHEN MONTH(att.attendance_date) = 8 and att.status = 'Present' THEN 1 ELSE 0 END) AS Aug,
            SUM(CASE WHEN MONTH(att.attendance_date) = 9 and att.status = 'Present' THEN 1 ELSE 0 END) AS Sep,
            SUM(CASE WHEN MONTH(att.attendance_date) = 10 and att.status = 'Present' THEN 1 ELSE 0 END) AS Oct,
            SUM(CASE WHEN MONTH(att.attendance_date) = 11 and att.status = 'Present' THEN 1 ELSE 0 END) AS Nov,
            SUM(CASE WHEN MONTH(att.attendance_date) = 12 and att.status = 'Present' THEN 1 ELSE 0 END),

            COUNT(CASE WHEN att.status = 'Late' THEN 1 END) AS Late
        FROM tabEmployee emp
        LEFT JOIN tabAttendance att ON emp.name = att.employee
        LEFT JOIN `tabSalary Structure Assignment` ssa 
            ON emp.name = ssa.employee 
            AND ssa.from_date = (SELECT MAX(from_date) FROM `tabSalary Structure Assignment` WHERE employee = emp.name)
        WHERE %s and att.docstatus=1
        GROUP BY emp.name, emp.department, emp.designation, emp.date_of_joining, emp.status, ssa.base
        ORDER BY emp.name
""" % (conditions), as_list=1)




    return result

def get_conditions(filters):
    conditions="" 
    from_date = get_first_day( "01"+ "-" + filters["year"])
    to_date = get_last_day( "12"+ "-" + filters["year"])
    # if filters.get("from_date"): conditions += " att.attendance_date>= '%s'" % filters["from_date"]
    if filters.get("year"): conditions += " att.attendance_date between '%s' and '%s' and emp.date_of_joining<='%s'" % (from_date,to_date,to_date)
    if filters.get("employee"): conditions += " and att.employee= '%s'" % filters["employee"]
    if filters.get("company"): conditions += " and att.company= '%s'" % filters["company"]
    if filters.get("department"): conditions += " and att.department= '%s'" % filters["department"]
    if filters.get("designation"): conditions += " and emp.designation='%s'" % filters["designation"]
    if filters.get("shift"): conditions += " and att.shift='%s'" % filters["shift"]
    if filters.get("section"): conditions += " and emp.section='%s'" % filters["section"]
    if filters.get("floor"): conditions += " and emp.floor='%s'" % filters["floor"]
    if filters.get("facility_or_line"): conditions += " and emp.facility_or_line='%s'" % filters["facility_or_line"]
    if filters.get("group_name"): conditions += " and emp.group='%s'" % filters["group_name"]
    if filters.get("employee_status"): conditions += " and emp.status='%s'" % filters["employee_status"]

    return conditions, filters