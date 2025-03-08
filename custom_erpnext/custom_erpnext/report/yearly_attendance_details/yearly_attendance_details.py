import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns()
    data = get_data(filters)

    leave_types = frappe.get_all("Leave Type", pluck="name")
    columns.extend([
        {"label": _(leave_type), "fieldtype": "Float", "width": 120, "precision": 2}
        for leave_type in leave_types
    ])

    return columns, data

def get_columns():
    return [
        _("Employee") + ":Data:90",
        _("Employee Name") + ":Data:90",
        
        _("Department") + ":Data:90",
        _("Designation") + ":Data:90",
        _("Joining") + ":Date:90",
        _("Duration (Days)") + ":Data:90",
        # _("Status") + ":Data:90",
        _("Present") + ":Int:120",
        _("Absent") + ":Int:90",
    ]

def get_data(filters):
    conditions, filters = get_conditions(filters)

    # Main attendance data query
    result = frappe.db.sql("""
        SELECT emp.name AS Employee,
                emp.employee_name AS Employee_Name,
               emp.department AS Department,
               emp.designation AS Designation,
               emp.date_of_joining AS Joining,
               DATEDIFF('%s', emp.date_of_joining) AS Duration1,
               COUNT(CASE WHEN att.status = 'Present' THEN 1 END) AS Present,
               COUNT(CASE WHEN att.status = 'Absent' THEN 1 END) AS Absent
        FROM tabEmployee emp
        LEFT JOIN tabAttendance att ON emp.name = att.employee where
        %s
        GROUP BY emp.name, emp.department, emp.designation, emp.date_of_joining, emp.status
        ORDER BY emp.name
    """% (filters["to_date"],conditions), as_list=1)

    # Fetch all leave types dynamically
    leave_types = frappe.get_all("Leave Type", pluck="name")

    # Leave details aggregation
    leave_details = frappe.db.sql("""
        SELECT att.employee, att.leave_type, att.status, COUNT(*) as count
        FROM tabAttendance att
        WHERE att.leave_type IS NOT NULL
          AND att.attendance_date BETWEEN %s AND %s
        GROUP BY att.employee, att.leave_type, att.status
    """%(filters["from_date"],filters["to_date"]), as_list=True)

    # Map leave details to each employee
    leave_map = {}
    for ld in leave_details:
        if ld['status'] == "Half Day":
            ld['count'] = ld['count'] * 0.5
        if ld['employee'] not in leave_map:
            leave_map[ld['employee']] = {}
        leave_map[ld['employee']][ld['leave_type']] = ld['count']

    # Construct the final result set
    final_data = []
    for row in result:
        employee = row[0]
        data_row = [
            row[0], row[1], row[2], row[3], 
            row[4], row[5], row[6]
        ]

        # Append leave counts
        for leave_type in leave_types:
            data_row.append(leave_map.get(employee, {}).get(leave_type, 0.0))

        final_data.append(data_row)

    return final_data

def get_conditions(filters):
    conditions="" 
    if filters.get("from_date"): conditions += " att.attendance_date>= '%s'" % filters["from_date"]
    if filters.get("to_date"): conditions += " and att.attendance_date<= '%s'" % filters["to_date"]
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