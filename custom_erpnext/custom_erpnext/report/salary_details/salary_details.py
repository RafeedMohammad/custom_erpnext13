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
		_("Joining Date") + ":Data:100",
		_("Total Service Length") + ":Data:100",
		_("Last Increment Date")+ ":Date:200",
		# _("Status") + ":Data:200",
        _("Base") + ":Currency:100",
        _("Basic") + ":Currency:100",
        _("Hrent") + ":Currency:100",
		_("Medical") + ":Currency:100"
    ]

def get_data(filters,from_date=None,to_date=None):
	conditions, filters = get_conditions(filters,from_date=None,to_date=None)
	con=""
	if filters.get("month") and filters.get("year"):
		from_date = get_first_day(filters.get("month") + "-" + filters.get("year"))
		to_date = get_last_day(filters.get("month") + "-" + filters.get("year"))
		# filters.update({"from_date": filters.get("from_date"), "to_date": filters.get("to_date")})
		# conditions, filters = get_conditions(filters,from_date=None,to_date=None)
		con+=" and ssa.from_date BETWEEN '"+str(from_date)+"' and '"+str(to_date)+"'"
	
	result = frappe.db.sql("""
   SELECT 
    ssa.employee,
    ssa.employee_name,
	emp.date_of_joining as joining_date,
    CONCAT( FLOOR(TIMESTAMPDIFF(YEAR, emp.date_of_joining, '%s'))," Years ", MOD(TIMESTAMPDIFF(MONTH, emp.date_of_joining, '%s'),12)," Month") AS total_service_length,

	ssa.from_date as last_increment_date,
    ssa.base,
    ((ssa.base - SUM(CASE WHEN sd.abbr = 'DM' THEN sd.amount ELSE 0 END)) / 1.5) AS basic,
    (((ssa.base - SUM(CASE WHEN sd.abbr = 'DM' THEN sd.amount ELSE 0 END)) / 1.5) / 2) AS hrent,
    SUM(CASE WHEN sd.abbr = 'DM' THEN sd.amount ELSE 0 END) AS medical
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
		 %s
    )
    AND emp.status="Active" %s
GROUP BY
    ssa.employee, ssa.employee_name, emp.status, ssa.base
ORDER BY 
    ssa.employee;

"""% (from_date or date.today(),from_date or date.today(),con,conditions), as_list=True)

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
	# if filters.get("company"): conditions += "ssa.company= '%s'" % filters["company"]
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
	if filters.get("employee"): conditions += " and ssa.employee in %s'" % filters["employee"]


	if filters.get("department"): conditions += " and ssa.department= '%s'" % filters["department"]

	#frappe.publish_realtime('msgprint', 'condition = '+conditions)		
	conditions=conditions.replace("]'", ")")
	conditions=conditions.replace("[", "(")
	
	return conditions, filters

@frappe.whitelist()
def get_year_options():
    current_year = datetime.now().year
    return "\n".join(str(year) for year in range(current_year, current_year - 5, -1))
