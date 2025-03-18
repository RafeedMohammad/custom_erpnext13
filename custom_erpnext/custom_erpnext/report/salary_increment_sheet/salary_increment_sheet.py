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
        _("Employee") + ":Data:50",
        _("Employee Name") + ":Data:150",
		_("Dept") + ":Data:100",
        _("Designation") + ":Data:100",
        _("Joining Date") + ":Data:100",
		_("Total Service Length") + ":Data:100",


		_("Previous Increment Date") + ":Date:100",
		_("Gross Salary Prev") + ":Int:100",
        _("Basic Prev") + ":Int:100",
        _("Hrent Prev") + ":Int:100",
        _("Medical Prev") + ":Int:100",

		_("Incre-ment percent") + ":Int:100",
		_("Incre-ment Taka") + ":Int:100",


        _("Curr Increment Date") + ":Date:100",
        _("Gross Salary New") + ":Int:100",
        _("Basic New") + ":Int:100",
        _("Hrent New") + ":Int:100",
        _("Medical New") + ":Int:100",
    ]

def get_data(filters,from_date=None,to_date=None):
	conditions, filters = get_conditions(filters,from_date=None,to_date=None)
	con=""
	if filters.get("month") and filters.get("year"):
		from_date = get_first_day(filters.get("month") + "-" + filters.get("year"))
		to_date = get_last_day(filters.get("month") + "-" + filters.get("year"))
		# filters.update({"from_date": filters.get("from_date"), "to_date": filters.get("to_date")})
		# conditions, filters = get_conditions(filters,from_date=None,to_date=None)
		con+="and from_date BETWEEN '"+str(from_date)+"' and '"+str(to_date)+"'"
	
	result = frappe.db.sql("""
  WITH LatestSalary AS (
    SELECT 
        employee,
        MAX(from_date) AS latest_from_date
    FROM `tabSalary Structure Assignment`
    where docstatus = 1 %s
    GROUP BY employee
),
PreviousSalary AS (
    SELECT 
        ssa.employee,
        MAX(ssa.from_date) AS prev_from_date
    FROM `tabSalary Structure Assignment` ssa
    WHERE ssa.from_date < (
        SELECT latest_from_date 
        FROM LatestSalary ls 
        WHERE ls.employee = ssa.employee
    ) and docstatus = 1
    GROUP BY ssa.employee
),
LatestDM AS (
    SELECT parent, SUM(amount) AS dm_amount
    FROM `tabSalary Detail`
    WHERE abbr = 'DM'
    GROUP BY parent
),
PreviousDM AS (
    SELECT parent, SUM(amount) AS dm_amount
    FROM `tabSalary Detail`
    WHERE abbr = 'DM'
    GROUP BY parent
)
SELECT 
    emp.name AS employee,
    emp.employee_name,
    emp.department as dept,
    emp.designation,
    emp.date_of_joining as joining_date,
    CONCAT( FLOOR(TIMESTAMPDIFF(YEAR, emp.date_of_joining, '%s'))," Years ", MOD(TIMESTAMPDIFF(MONTH, emp.date_of_joining, '%s'),12)," Month") AS total_service_length,

    prev_ssa.from_date AS previous_increment_date,
    prev_ssa.base AS gross_salary_prev,
    ((prev_ssa.base - COALESCE(prev_dm.dm_amount, 0)) / 1.5) AS basic_prev,
    (((prev_ssa.base - COALESCE(prev_dm.dm_amount, 0)) / 1.5) / 2) AS hrent_prev,
    COALESCE(prev_dm.dm_amount, 0) AS medical_prev,

    ((((latest_ssa.base - COALESCE(latest_dm.dm_amount, 0)) / 1.5) - 
      ((prev_ssa.base - COALESCE(prev_dm.dm_amount, 0)) / 1.5)) /
      ((prev_ssa.base - COALESCE(prev_dm.dm_amount, 0)) / 1.5)) * 100 AS incre_ment_percent,

    (((latest_ssa.base - COALESCE(latest_dm.dm_amount, 0)) / 1.5) - 
     ((prev_ssa.base - COALESCE(prev_dm.dm_amount, 0)) / 1.5)) AS incre_ment_taka,

    latest_ssa.from_date AS curr_increment_date,
    latest_ssa.base AS gross_salary_new,
    ((latest_ssa.base - COALESCE(latest_dm.dm_amount, 0)) / 1.5) AS basic_new,
    (((latest_ssa.base - COALESCE(latest_dm.dm_amount, 0)) / 1.5) / 2) AS hrent_new,
    COALESCE(latest_dm.dm_amount, 0) AS medical_new
FROM `tabEmployee` emp
LEFT JOIN LatestSalary ls ON emp.name = ls.employee
LEFT JOIN `tabSalary Structure Assignment` latest_ssa 
    ON emp.name = latest_ssa.employee AND latest_ssa.from_date = ls.latest_from_date
LEFT JOIN PreviousSalary ps ON emp.name = ps.employee
LEFT JOIN `tabSalary Structure Assignment` prev_ssa 
    ON emp.name = prev_ssa.employee AND prev_ssa.from_date = ps.prev_from_date
LEFT JOIN LatestDM latest_dm ON latest_dm.parent = latest_ssa.salary_structure
LEFT JOIN PreviousDM prev_dm ON prev_dm.parent = prev_ssa.salary_structure
WHERE emp.status = 'Active' and prev_ssa.docstatus = 1 and latest_ssa.docstatus=1 AND %s
ORDER BY emp.name;

"""% (con,from_date or date.today(),from_date or date.today(),conditions), as_dict=True)

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
	if filters.get("company"): conditions += "latest_ssa.company= '%s'" % filters["company"]
	# if from_date:conditions += " and ssa.from_date BETWEEN '{0}' AND '{1}'".format(from_date.strftime('%Y-%m-%d'), to_date.strftime('%Y-%m-%d'))
	# if (filters.get("employee")): 
	# 	valu = list(map(str.strip, (filters.get("employee")).split(','))) 
	# # frappe.publish_realtime('msgprint', valu)		
	# 	for i in range(0,len(valu)): 
	# 		if(i==len(valu)-1):
	# 			val= '"'+valu[i]+'"'	
	# 		else:
	# 			val= '"'+valu[i]+'",'
	# 		val=val.replace("\ ","")
	# 	conditions += " and employee in '%s'" % val.replace
	# if filters.get("employee"): conditions += "employee in ('%s'" % filters["employee"]
	# if filters.get("employee1"): conditions += ",'%s'" % filters["employee1"]
	# if filters.get("employee2"): conditions += "'%s'" % filters["employee2"]
	# if filters.get("employee"): conditions += ")"
	# if filters.get("employee"): conditions += " and ssa.employee in %s'" % filters["employee"]


	# if filters.get("department"): conditions += " and ssa.department= '%s'" % filters["department"]

	#frappe.publish_realtime('msgprint', 'condition = '+conditions)		
	conditions=conditions.replace("]'", ")")
	conditions=conditions.replace("[", "(")
	
	return conditions, filters

@frappe.whitelist()
def get_year_options():
    current_year = datetime.now().year
    return "\n".join(str(year) for year in range(current_year, current_year - 3, -1))
