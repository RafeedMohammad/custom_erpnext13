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
	
def convert_to_bangla_number(value):
    eng_to_bangla_digits = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
    return str(value).translate(eng_to_bangla_digits)


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
		_("Boss Signature") + ":Data:120",
	]

def get_data(filters):
	conditions, filters = get_conditions(filters)
	result = frappe.db.sql("""SELECT emp.name,emp.company_in_bangla,emp.image , emp.name_in_bangla, emp.department_in_bangla ,emp.designation,TO_CHAR(emp.date_of_joining, 'dd-mm-YYYY'),emp.blood_group, emp.emergency_phone_number ,com.company_logo,com.lai_boss_signature FROM tabEmployee as emp INNER JOIN tabCompany as com ON emp.company = com.name  where %s""" 
	% conditions, as_list=1)

	final_result = []
	for row in result:
        # Convert joining date and EMC No to Bangla
		row = list(row)
		if row[6]:  # joining date
			row[6] = convert_to_bangla_number(row[6])
		if row[8]:  # emergency_phone_number
			row[8] = convert_to_bangla_number(row[8])
		final_result.append(row)

	return final_result
	

def get_conditions(filters):
	conditions="" 
	if filters.get("company"): conditions += "company= '%s'" % filters["company"]
	# if (filters.get("employee")): 
	if filters.get("employee"): conditions += " and employee in %s'" % filters["employee"]


	if filters.get("department"): conditions += " and department= '%s'" % filters["department"]
	if filters.get("designation"): conditions += " and designation='%s'" % filters["designation"]
	if filters.get("status"): conditions += " and status='%s'" % filters["status"]

	#frappe.publish_realtime('msgprint', 'condition = '+conditions)		
	conditions=conditions.replace("]'", ")")
	conditions=conditions.replace("[", "(")
	
	return conditions, filters

