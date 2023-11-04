
from datetime import datetime, timedelta
import frappe
from frappe.utils import flt
from frappe import _
from frappe.utils import add_days, cstr, date_diff, get_first_day, get_last_day, getdate


def execute(filters= None):

	if not filters:
		filters = {}

	salary_slips = get_salary_slip(filters)
	columns = get_columns(salary_slips)

	data = []


	allowance = 0
	for ss in salary_slips:
		

		allowance = allowance+get_allowance(ss.name)
		
		

			
			
	row=[
		filters["employee"],
		round(allowance,0),
	]
	data.append(row)



	return columns, data
	


def get_columns(salary_slips):
	columns = [
		# _("Salary Slip ID") + ":Link/Salary Slip:150",
		_("Employee") + "::80",
		_("Total PF") + "::40",

		
	]

	return columns


def get_salary_slip(filters):
	conditions, filters = get_conditions(filters)	

	salary_slips = frappe.db.sql("""select * from `tabSalary Slip` as ss WHERE docstatus!= '2' and %s ORDER BY employee
	""" 
	%conditions, filters, as_dict=1)


	return salary_slips or []



def get_conditions(filters):
	conditions="" 
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}
	if filters.get("docstatus"):
		conditions += "docstatus = {0}".format(doc_status[filters.get("docstatus")])


	if filters.get("company"): conditions += "ss.company= '%s'" % filters["company"]
 
	if filters.get("employee"): conditions += " and ss.employee= '%s'" % filters["employee"]
	if filters.get("department"): conditions += " and ss.department= '%s'" % filters["department"]
	if filters.get("designation"): conditions += " and ss.designation='%s'" % filters["designation"]
	# if filters.get("shift"): conditions += " and att.shift='%s'" % filters["shift"]
	if filters.get("section"): conditions += " and ss.section='%s'" % filters["section"]
	if filters.get("floor"): conditions += " and ss.floor='%s'" % filters["floor"]
	if filters.get("facility_or_line"): conditions += " and ss.facility_or_line='%s'" % filters["facility_or_line"]
	if filters.get("group_name"): conditions += " and ss.group='%s'" % filters["group_name"]
	if filters.get("grade"): conditions += " and ss.grade='%s'" % filters["grade"]
	# if filters.get("sub_department"): conditions += " and ss.sub_department like '%s'" % filters["sub_department"]


	return conditions, filters

def get_basic(ss):
	return frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'B'}, ['default_amount','amount'])

# def get_salary_basic(ss):
	# return frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'B'}, 'amount')

def get_allowance(ss):
	#return frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'HR'}, 'SUM(amount)')
	return frappe.db.sql("""SELECT SUM(amount) FROM `tabSalary Detail` where parent=%s and abbr IN('PF')""", ss)[0][0] or 0



def off_days(employee, start_date, end_date):
	return frappe.db.sql("""SELECT COUNT(*) FROM `tabAttendance` as a where a.employee='%s' and status IN('Weekly Off', 'Holiday') and a.attendance_date BETWEEN '%s' AND '%s'""" % (employee, start_date, end_date))[0][0]


# def on_leave(employee, start_date, end_date):
# 	return frappe.db.sql("""SELECT COUNT(*) FROM `tabAttendance` as a where a.employee='%s' and status IN('Weekly Off', 'Holiday') and a.attendance_date BETWEEN '%s' AND '%s'""" % (employee, start_date, end_date))[0][0]


def get_attendance_bonus(ss):
	return (frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'AB'}, 'amount') or 0)

def get_lunch_tr_allowance(ss):
	return (frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'LT'}, 'amount') or 0)

def get_lunch(ss):
	return (frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'Lunch Allowance'}, 'amount') or 0)

def get_night_allowance(ss):
	return (frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'NA'}, 'amount') or 0)

def get_convanse(ss):
	return (frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'CNV'}, 'amount') or 0)