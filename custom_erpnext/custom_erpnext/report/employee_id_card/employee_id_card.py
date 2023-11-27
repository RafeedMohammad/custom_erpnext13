from datetime import datetime, timedelta
import frappe
from frappe import _


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
		_("Name") + ":Data/Employee:120",
		_("Company") + ":Data/Employee:120",
		_("Image") + ":Data/Employee:120",
		_("Employee Name") + ":Data/Employee:120",
		_("Department") + ":Data/Employee:120",
		_("Designation") + ":Data/Employee:120",
		_("Joining Date") + ":Data/Employee:120",
		_("Blood group") + ":Data/Employee:120",
		_("Phone No") + ":Data/Employee:120",
		_("Company logo") + ":Data:120",
	]

def get_data(filters):
	conditions, filters = get_conditions(filters)
	result = frappe.db.sql("""SELECT emp.name,emp.company,emp.image , emp.employee_name, emp.department ,emp.designation, emp.date_of_joining,emp.blood_group, emp.cell_number ,com.company_logo FROM tabEmployee as emp INNER JOIN tabCompany as com ON emp.company = com.name  where %s""" 
	% conditions, as_list=1)

	# for i in range(0,len(result)):
	# 	if result[i][2] is None:
	# 		result[1][2]=result[i][-1]

	# data = frappe.get_all(
	# 	"Employee",
	# 	filters=conditions,
	# 	fields=["name", "employee_name", "default_shift"],
	# )

	return result
	

def get_conditions(filters):
    conditions="" 
    if filters.get("company"): conditions += "company= '%s'" % filters["company"]
    if filters.get("employee"): conditions += " and employee= '%s'" % filters["employee"]
    if filters.get("department"): conditions += "and department= '%s'" % filters["department"]
    if filters.get("designation"): conditions += " and designation='%s'" % filters["designation"]
    if filters.get("status"): conditions += " and status='%s'" % filters["status"]
	
    return conditions, filters

