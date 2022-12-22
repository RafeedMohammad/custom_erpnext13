# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
from typing import List
from frappe.utils import cint,getdate
from calendar import month, monthrange

import erpnext


def execute(filters=None):
	if not filters:
		filters = {}
	currency = None
	if filters.get("currency"):
		currency = filters.get("currency")
	company_currency = erpnext.get_company_currency(filters.get("company"))
	salary_slips = get_salary_slips(filters, company_currency)
	if not salary_slips:
		return [], []

	columns, earning_types, ded_types = get_columns(salary_slips)
	ss_earning_map = get_ss_earning_map(salary_slips, currency, company_currency)
	ss_ded_map = get_ss_ded_map(salary_slips, currency, company_currency)
	doj_map = get_employee_doj_map()
	
	data = []
	
	weekly_offs = 0
	for ss in salary_slips:
		weekly_offs = frappe.db.sql("""SELECT count(*) FROM tabAttendance where status='Weekly Off' and employee='%s' and attendance_date BETWEEN '%s' AND '%s' GROUP BY status """% (ss.employee, ss.start_date, ss.end_date), as_list=1)
		# if len(weekly_offs) == 0:
		# 	weekly_offs.append(0)
	
		

		#Remove the comments after it's done

		if len(weekly_offs) == 0:
			working_on_weekly_off = 0
		else:
			working_on_weekly_off = str(weekly_offs[0][0])

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
			ss.leave_without_pay,
			ss.present_days,
			str(working_on_weekly_off),

			
			frappe.db.get_value('Salary Slip Leave', {'parent': ss.name, 'leave_type': 'Casual Leave'}, 'used_leaves'),
			frappe.db.get_value('Salary Slip Leave', {'parent': ss.name, 'leave_type': 'Sick Leave'}, 'used_leaves'),
			frappe.db.get_value('Salary Slip Leave', {'parent': ss.name, 'leave_type': 'Paternity Leave'}, 'used_leaves'),
			ss.absent_days,
			get_holiday(ss.start_date,ss.end_date),
			ss.total_working_days,
			ss.base_pay,
			10,
			flt(ss.overtime_pay),
			flt(ss.overtime_rate),
			flt(ss.total_overtime_pay)
		]
		


		# if ss.branch is not None:
		# 	columns[3] = columns[3].replace("-1", "120")
		if ss.department is not None:
			columns[4] = columns[4].replace("-1", "120")
		if ss.designation is not None:
			columns[5] = columns[5].replace("-1", "120")
		if ss.leave_without_pay is not None:
			columns[9] = columns[9].replace("-1", "130")

		count = 0
		for e in earning_types:
			if count == 0:
				row.append(get_basic(ss.name))
				count = 1
			else:
				#row.append(ss_earning_map.get(ss.name, {}).get(e))
				row.append(get_basic(ss.name))
				row.append(get_med(ss.name))
				row.append(10)


		if currency == company_currency:
			row += [flt(ss.gross_pay) * flt(ss.exchange_rate)]
		else:
			row += [ss.gross_pay]

		for d in ded_types:
			row.append(ss_ded_map.get(ss.name, {}).get(d))

		row.append(ss.total_loan_repayment)

		if currency == company_currency:
			row += [
				flt(ss.total_deduction) * flt(ss.exchange_rate),
				flt(ss.net_pay) * flt(ss.exchange_rate),
			]
		else:
			row += [ss.total_deduction, ss.net_pay]
		row.append(currency or company_currency)
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
		_("LWP") + ":Float:50",
		_("P") + ":Float:120",
		_("W/H") + ":Float:120",

		_("CL") + ":Float:80",
		_("SL") + ":Float:80",
		_("PL") + ":Float:80",
		_("AD") + ":Float:80",
		_("Holidays") + ":Data:80",
		_("Att.") + ":Float:80",
		_("Base Pay") +":Float:80",
		_("Stamp") +":Float:80",
		_("OT Hr") +":Float:80",
		_("OT Rate") +":Float:80",
		_("OT Amt.") +":Float:80"

	
	]

	salary_components = {_("Earning"): [], _("Deduction"): []}

	for component in frappe.db.sql(
		"""select distinct sd.salary_component, sc.type
		from `tabSalary Detail` sd, `tabSalary Component` sc
		where sc.name=sd.salary_component and sd.amount != 0 and sd.parent in (%s)"""
		% (", ".join(["%s"] * len(salary_slips))),
		tuple([d.name for d in salary_slips]),
		as_dict=1,
	):
		salary_components[_(component.type)].append(component.salary_component)

	columns = (
		columns
		+ [(e + ":Currency:120") for e in salary_components[_("Earning")]]
		+ [_("Gross Pay") + ":Currency:120"]
		+ [(d + ":Currency:120") for d in salary_components[_("Deduction")]]
		+ [
			_("Loan Repayment") + ":Currency:120",
			_("Total Deduction") + ":Currency:120",
			_("Net Pay") + ":Currency:120",
		]
		
	)

	return columns, salary_components[("Earning")], salary_components[("Deduction")]


def get_salary_slips(filters, company_currency):
	filters.update({"from_date": filters.get("from_date"), "to_date": filters.get("to_date")})
	conditions, filters = get_conditions(filters, company_currency)
	salary_slips = frappe.db.sql(
		"""select * from `tabSalary Slip` where %s
		order by employee"""
		% conditions,
		filters,
		as_dict=1,
	)

	return salary_slips or []


def get_conditions(filters, company_currency):
	conditions = ""
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

	if filters.get("docstatus"):
		conditions += "docstatus = {0}".format(doc_status[filters.get("docstatus")])

	
	# if filters.get("month") and filters.get("year"):
	# 	conditions += " and start_date <= " + filters.get("01"+"-"+filters.get("month")+ filters.get("year"))
	# 	conditions += " and end_date >= " + filters.get("30"+"-"+filters.get("month")+ filters.get("year"))

	
	if filters.get("company"):
		conditions += " and company = %(company)s"
	if filters.get("employee"):
		conditions += " and employee = %(employee)s"
	if filters.get("currency") and filters.get("currency") != company_currency:
		conditions += " and currency = %(currency)s"

	return conditions, filters


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
def get_holiday(sd,ed):
	cd ="'"+ str(sd) +"'"  + " and " + "'"+ str(ed) +"'"
	
	return frappe.db.sql(
		"""
			select count(holiday_date) 
			from tabHoliday 
			where holiday_date between %s""" % cd,as_list=1)
def get_basic(ss):
	return frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'B'}, 'default_amount')

def get_med(ss):
	return frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'M', 'abbr': 'HR'}, 'SUM(default_amount)')
	#return str(frappe.db.sql("""SELECT name FROM `tabSalary Detail` where parent=%s and abbr='M'""", ss))

def get_leave_type():
	return frappe.db.sql("""
		SELECT leave_type
		FROM `tabSalary Slip Leave`
	""", as_list = 1)


def get_ss_earning_map(salary_slips, currency, company_currency):
	ss_earnings = frappe.db.sql(
		"""select sd.parent, sd.salary_component, sd.amount, ss.exchange_rate, ss.name
		from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)"""
		% (", ".join(["%s"] * len(salary_slips))),
		tuple([d.name for d in salary_slips]),
		as_dict=1,
	)

	ss_earning_map = {}
	for d in ss_earnings:
		ss_earning_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
		if currency == company_currency:
			ss_earning_map[d.parent][d.salary_component] += flt(d.amount) * flt(
				d.exchange_rate if d.exchange_rate else 1
			)
		else:
			ss_earning_map[d.parent][d.salary_component] += flt(d.amount)

	return ss_earning_map

#Added code to get the summation of the components
def get_allowance_addition(salary_slips, currency):
	ss_earnings_addition = frappe.db.sql("""select sd.parent, sd.salary_component, sd.amount, ss.exchange_rate, ss.name
		from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name GROUP BY sd.parent""")
	return 0


def get_ss_ded_map(salary_slips, currency, company_currency):
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
		if currency == company_currency:
			ss_ded_map[d.parent][d.salary_component] += flt(d.amount) * flt(
				d.exchange_rate if d.exchange_rate else 1
			)
		else:
			ss_ded_map[d.parent][d.salary_component] += flt(d.amount)

	return ss_ded_map

def get_total_days_in_month(filters) -> int:
	return monthrange(cint(filters.get("year")), cint(filters.get("month")))[1]
