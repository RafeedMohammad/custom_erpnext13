
from datetime import datetime, timedelta
import frappe
from frappe.utils import flt
from frappe import _




def execute(filters= None):
	if not filters:
		filters = {}

	salary_slips = get_salary_slip(filters)
	columns, ded_types = get_columns(salary_slips)
	doj_map = get_employee_doj_map()
	ss_ded_map = get_ss_ded_map(salary_slips)

	data = []



	for ss in salary_slips:
		allowance = 0
		basic = get_basic(ss.name)
		if basic is None:
			basic = 0
		allowance = get_allowance(ss.name)
		
		row = [
			ss.name,
			ss.employee,
			ss.employee_name,
			doj_map.get(ss.employee),
			# ss.branch,
			# ss.department,
			ss.designation,
			# ss.company,
			ss.start_date,
			ss.end_date,
			basic,
			allowance,
			basic + allowance,
			ss.present_days,
			worked_on_off_days(ss.employee, ss.start_date, ss.end_date),
			frappe.db.get_value('Attendance', {'employee': ss.employee, 'leave_type': 'CL', 'attendance_date': ['>',  ss.start_date], 'attendance_date': ['<',  ss.end_date]}, 'count(*)'),
			frappe.db.get_value('Attendance', {'employee': ss.employee, 'leave_type': 'EL', 'attendance_date': ['>',  ss.start_date], 'attendance_date': ['<',  ss.end_date]}, 'count(*)'),
			frappe.db.get_value('Attendance', {'employee': ss.employee, 'leave_type': 'ML', 'attendance_date': ['>',  ss.start_date], 'attendance_date': ['<',  ss.end_date]}, 'count(*)'),
			frappe.db.get_value('Attendance', {'employee': ss.employee, 'leave_type': 'SL', 'attendance_date': ['>',  ss.start_date], 'attendance_date': ['<',  ss.end_date]}, 'count(*)'),
			frappe.db.get_value('Attendance', {'employee': ss.employee, 'leave_type': 'Leave Without Pay', 'attendance_date': ['>',  ss.start_date], 'attendance_date': ['<',  ss.end_date]}, 'count(*)'),


			ss.absent_days,
			ss.gross_pay,
			ss.overtime_hours,
			ss.total_overtime_pay,
			get_attendance_bonus(ss.name),
			get_lunch_tr_allowance(ss.name),
			ss.night_days,
			get_night_allowance(ss.name),
			ss.arrear,
			ss.gross_pay,


			
			
		]

		for d in ded_types:
			row.append(ss_ded_map.get(ss.name, {}).get(d))
		
		row += [ss.total_loan_repayment,ss.total_deduction, ss.net_pay, None]
		

		data.append(row)



	return columns, data
	


def get_columns(salary_slips):
	columns = [
		_("Salary Slip ID") + ":Link/Salary Slip:150",
		_("Employee") + ":Link/Employee:120",
		_("Employee Name") + "::140",
		_("Date of Joining") + "::80",
		_("Designation") + ":Link/Designation:120",
		_("Start Date") + "::80",
		_("End Date") + "::80",
		_("Basic") + "::80",
		_("Allowance") + "::80",
		_("Gross") + "::80",
		_("P") + ":Float:120",
		_("W/H") + ":Float:120",
		_("CL") + ":Float:80",
		_("EL") + ":Float:80",
		_("ML") + ":Float:80",
		_("SL") + ":Float:80",
		_("LL LWP") + ":Float:80",
		_("A") + ":Float:80",
		_("Total Salary") + ":Float:80",
		_("O.T Hr.") + ":Float:80",
		_("O.T Amt.") + ":Currency:80",
		_("Attn. Bon.") + ":Currency:80",
		_("Lunch Tran. Allow") + ":Currency:80",
		_("Night Allow - Day") + ":Float:80",
		_("Night Allow - Amt.") + ":Currency:80",
		_("Arrear") + ":Currency:80",
		_("Gross Payable") + ":Currency:80",


		#_("Date of Joining") + "::80",

	]

	salary_components = { _("Deduction"): []}
	if salary_slips:
		for component in frappe.db.sql(
			"""select distinct sd.salary_component, sc.type
			from `tabSalary Detail` sd, `tabSalary Component` sc
			where sc.name=sd.salary_component and sc.type = 'Deduction' and sd.parent in (%s)"""
			% (", ".join(["%s"] * len(salary_slips))),
			tuple([d.name for d in salary_slips]),
			as_dict=1,
		):
			salary_components[_(component.type)].append(component.salary_component)

	columns = (
		columns
		+ [(d + ":Currency:120") for d in salary_components[_("Deduction")]]
		+ [
			_("Advance") + ":Currency:120",
			_("Total Deduction") + ":Currency:120",
			_("Net Pay") + ":Currency:120",
			_("Signature & Stamp") + ":Text:140",

		]
		
	)

	return columns, salary_components[("Deduction")]







def get_employee_doj_map():
	return frappe._dict(
		frappe.db.sql(
			"""
				SELECT
					employee,
					date_of_joining
				FROM `tabEmployee`
				"""
		)
	)


def get_salary_slip(filters):
	conditions, filters = get_conditions(filters)
	

	filters.update({"from_date": filters.get("from_date"), "to_date": filters.get("to_date")})
	conditions, filters = get_conditions(filters)
	

	salary_slips = frappe.db.sql("""select * from `tabSalary Slip` as ss WHERE %s ORDER BY employee
	""" 
	%conditions, filters, as_dict=1)


	return salary_slips or []


def get_ss_ded_map(salary_slips):
	if salary_slips:
		ss_deductions = frappe.db.sql(
			"""select sd.parent, sd.salary_component, sd.amount, ss.exchange_rate, ss.name
			from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)"""
			% (", ".join(["%s"] * len(salary_slips))),
			tuple([d.name for d in salary_slips]),
			as_dict=1,
		)

		ss_ded_map = {}
		for d in ss_deductions:
			ss_ded_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
			ss_ded_map[d.parent][d.salary_component] += flt(d.amount)

		return ss_ded_map




def get_conditions(filters):
	conditions="" 
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}
	if filters.get("docstatus"):
		conditions += "docstatus = {0}".format(doc_status[filters.get("docstatus")])


	if filters.get("from_date"): conditions += " and ss.start_date>= '%s'" % filters["from_date"]
	if filters.get("to_date"): conditions += " and ss.end_date<= '%s'" % filters["to_date"]
	if filters.get("employee"): conditions += " and ss.employee= '%s'" % filters["employee"]
	# if filters.get("company"): conditions += " and att.company= '%s'" % filters["company"]
	# if filters.get("department"): conditions += " and att.department= '%s'" % filters["department"]
	# if filters.get("designation"): conditions += " and tabEmployee.designation='%s'" % filters["designation"]
	# if filters.get("shift"): conditions += " and att.shift='%s'" % filters["shift"]
	# if filters.get("section"): conditions += " and tabEmployee.section='%s'" % filters["section"]
	# if filters.get("floor"): conditions += " and tabEmployee.floor='%s'" % filters["floor"]
	# if filters.get("facility_or_line"): conditions += " and tabEmployee.facility_or_line='%s'" % filters["facility_or_line"]
	# if filters.get("group_name"): conditions += " and tabEmployee.group='%s'" % filters["group_name"]

	return conditions, filters

def get_basic(ss):
	return frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'B'}, 'default_amount')


def get_allowance(ss):
	#return frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'HR'}, 'SUM(amount)')
	return frappe.db.sql("""SELECT SUM(amount) FROM `tabSalary Detail` where parent=%s and abbr IN('M', 'HR')""", ss)[0][0]



def worked_on_off_days(employee, start_date, end_date):
	#return frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'HR'}, 'SUM(amount)')
	return frappe.db.sql("""SELECT COUNT(*) FROM `tabAttendance` as a where a.employee='%s' and status IN('Weekly Off', 'Holiday') and a.attendance_date BETWEEN '%s' AND '%s'""" % (employee, start_date, end_date))[0][0]


def on_leave(employee, start_date, end_date):
	return frappe.db.sql("""SELECT COUNT(*) FROM `tabAttendance` as a where a.employee='%s' and status IN('Weekly Off', 'Holiday') and a.attendance_date BETWEEN '%s' AND '%s'""" % (employee, start_date, end_date))[0][0]


def get_attendance_bonus(ss):
	return frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'AB'}, 'amount')

def get_lunch_tr_allowance(ss):
	return frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'LT'}, 'amount')

def get_night_allowance(ss):
	return frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'NA'}, 'amount')
