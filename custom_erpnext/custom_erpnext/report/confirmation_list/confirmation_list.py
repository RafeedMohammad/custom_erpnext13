from datetime import datetime, timedelta,date
import frappe
from frappe import _
from frappe.utils import add_days, cstr, date_diff, get_first_day, get_last_day, getdate


def execute(filters= None):
	if not filters:
		filters = {}
	columns = get_columns()
	data = get_data(filters)
	#index_of_status = columns.index("Status:Data/:120")
	#report_summary = get_report_summary(data,index_of_status)
	return columns, data
	


def get_columns():
	 return [
		_("Employee") + ":Data:200",
        _("Employee Name") + ":Data:200",
		
		_("Department") + ":Data:100",
		_("Designation")+ ":Data:200",
		_("Joining Date") + ":Data:100",
		_("Confirmation Date") + ":Data:100",

		# _("Status") + ":Data:200",
        _("Gross Pay") + ":Int:100",# named base in my system
        _("Basic") + ":Int:100",
        _("Hrent") + ":Int:100",
		_("Medical") + ":Int:100"
    ]

def get_data(filters):
	conditions, filters = get_conditions(filters)	
	result = frappe.db.sql("""
  SELECT 
    emp.name AS employee,
    emp.employee_name,
	emp.department,
	emp.designation	,
    emp.date_of_joining AS joining_date,
	emp.final_confirmation_date,
    COALESCE(ssa.base, 0) AS gross_pay, 
    COALESCE((ssa.base - SUM(CASE WHEN sd.abbr = 'DM' THEN sd.amount ELSE 0 END)) / 1.5, 0) AS basic,
    COALESCE(((ssa.base - SUM(CASE WHEN sd.abbr = 'DM' THEN sd.amount ELSE 0 END)) / 1.5) / 2, 0) AS hrent,
    COALESCE(SUM(CASE WHEN sd.abbr = 'DM' THEN sd.amount ELSE 0 END), 0) AS medical
FROM
    `tabEmployee` emp
LEFT JOIN
    `tabSalary Structure Assignment` ssa 
    ON emp.name = ssa.employee 
    AND ssa.from_date = (
        SELECT MAX(from_date) 
        FROM `tabSalary Structure Assignment` 
        WHERE employee = emp.name
    )
LEFT JOIN
    `tabSalary Detail` sd 
    ON sd.parent = ssa.salary_structure
WHERE
     %s and ssa.docstatus = 1
GROUP BY
    emp.name, emp.employee_name, emp.date_of_joining, ssa.base
ORDER BY 
    emp.date_of_joining DESC;

"""% (conditions), as_list=True)

	# for i in range(0,len(result)):
	# 	if result[i][2] is None:
	# 		result[1][2]=result[i][-1]

	# data = frappe.get_all(
	# 	"Employee",
	# 	filters=conditions,
	# 	fields=["name", "employee_name", "default_shift"],
	# )

	return result
	

def get_conditions(filters,from_date=None,to_date=None):
	conditions="" 
	if filters.get("company"): conditions += "emp.company= '%s'" % filters["company"]
	if filters.get("month") and filters.get("year"):
		from_date = get_first_day(filters.get("month") + "-" + filters.get("year"))
		to_date = get_last_day(filters.get("month") + "-" + filters.get("year"))
		conditions += " AND emp.final_confirmation_date BETWEEN '%s' AND '%s'" %(from_date,to_date)
	
	if filters.get("employee"): conditions += " and emp.employee in %s'" % filters["employee"]


	if filters.get("department"): conditions += " and emp.department= '%s'" % filters["department"]

	if filters.get("mode_of_payment"): conditions += " and emp.salary_mode='%s'" % filters["mode_of_payment"]
	# if filters.get("bank"): conditions += " and ss.bank_name='%s'" % filters["bank"]
	if filters.get("employee_type"):
		if (filters["employee_type"]=="Active"):
			conditions += " and emp.status='Active' "
		if (filters["employee_type"]=="Left"):
			conditions += " and emp.status='Left' "
		if (filters["employee_type"]=="Inactive"):
			conditions += " and emp.status='Inactive' "

	#frappe.publish_realtime('msgprint', 'condition = '+conditions)		
	conditions=conditions.replace("]'", ")")
	conditions=conditions.replace("[", "(")
	
	return conditions, filters

@frappe.whitelist()
def get_year_options():
    current_year = datetime.now().year
    return "\n".join(str(year) for year in range(current_year, current_year - 5, -1))
