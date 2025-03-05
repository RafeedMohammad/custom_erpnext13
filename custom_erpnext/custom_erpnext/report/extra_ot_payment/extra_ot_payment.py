
from datetime import datetime, timedelta
import frappe
from frappe.utils import flt
from frappe import _
from frappe.utils import add_days, cstr, date_diff, get_first_day, get_last_day, getdate


def execute(filters= None):
	
	from_date = get_first_day(filters["month"] + "-" + filters["year"])
	to_date = get_last_day(filters["month"] + "-" + filters["year"])
	data=[]
	if not filters:
		filters = {}
	departments = frappe.db.get_list("Department", pluck="name", order_by="name")
	for department in departments:
		salary_slips = get_salary_slip(from_date,to_date,filters,department)

		columns = get_columns(salary_slips)
		doj_map = get_employee_doj_map()
		# ss_ded_map = get_ss_ded_map(salary_slips)
		if len(salary_slips) >= 1:
			data.append({"department": department})

		# data = []
		result=[]



		for ss in salary_slips:
			allowance = 0
			acctual_basic,salary_slip_basic = get_basic(ss.name)
			if acctual_basic is None:
				acctual_basic = 0
			# salary_slip_basic = get_salary_basic(ss.name)
			if salary_slip_basic is None:
				salary_slip_basic = 0

			
			overtime_hours=ss.overtime_hours


			buyer2_ot_hours= frappe.db.sql("""SELECT SUM(case when rounded_ot>%s then %s else rounded_ot end) FROM `tabAttendance` where status not in ('Holiday','Weekly Off') and employee=%s AND attendance_date between %s and %s group by employee""",
			(filters.buyer,filters.buyer,ss.employee, ss.start_date, ss.end_date))

			if buyer2_ot_hours:
				buyer2_ot_hours = buyer2_ot_hours[0][0]
			else:
				buyer2_ot_hours = 0
			remain_ot=float(overtime_hours)-buyer2_ot_hours
			remain_ot_amount=remain_ot*float(ss.overtime_rate)

			row = [
				None,
				#ss.name,
				ss.employee,
				ss.employee_name,
				# doj_map.get(ss.employee),
				# ss.branch,
				# ss.department,
				ss.designation,
				# ss.company,
				# ss.start_date,
				# ss.end_date,
				round(acctual_basic,0),
				round(float(overtime_hours or 0),1),
				buyer2_ot_hours,
				remain_ot,
				round(float(ss.overtime_rate),1),
				round(remain_ot_amount,1),
				ss.working_holidays,
				round(ss.working_holidays*ss.lunch_rate,1),
				round(ss.working_holidays*ss.travel_rate,1),
				ss.working_holiday_in_night,
				round(ss.working_holiday_in_night*ss.night_rate,1),
				#ss.total_overtime_pay,
				# round(float(ot_amount or 0),0),
				# get_lunch_tr_allowance(ss.name),	
				round(remain_ot_amount,1)+round(ss.working_holidays*ss.lunch_rate,1)+round(ss.working_holidays*ss.travel_rate,1)+round(ss.working_holiday_in_night*ss.night_rate,1)
			]
			
			for i in range(len(row)): 
				if i>4 and i<len(row): # Use the length of 'row' to avoid accessing out of bounds
					result.append(0)  # Initialize result with 0s or use an already initialized result list
					result[i] = result[i] + row[i]
				else:
					result.append(None)
			
			data.append(row)
			# for index, p in enumerate(products):
  			# 	if index == len(products) - 1:
			# 		result[0]="Total"
			# 	data.append(result)
		for index, ss in enumerate(salary_slips):
			if index == len(salary_slips) - 1:
				result[0]="Total"
				result[1]="Total"
				result[2]=len(salary_slips)
				data.append(result)

	return columns, data
	


def get_columns(salary_slips):
	columns = [
		# _("Salary Slip ID") + ":Link/Salary Slip:150",
		_("Department") + "::150",
		_("Employee") + "::80",
		_("Employee Name") + "::40",
		# _("Joining_Date") + "::12",
		_("Designation") + "::40",
		# _("Start Date") + "::80",
		# _("End Date") + "::80",

		_("Basic") + "::10",
		_("Total OT Hr.") + ":%.2Float:7",
		_("Avail OT Hr.") + ":%.2Float:7",
		_("Remain OT Hr.") + ":%.2Float:7",
		_("OT Rate") + ":%.2Float:7",
		_("OT Amount") + ":%.2Float:7",
		_("Allowance Day") + ":%.2Float:7",
		_("Allowance Amount") + ":%.2Float:7",
		_("Trans") + ":%.2Float:7",
		_("Night Day") + ":%.2Float:7",
		_("Night Amount") + ":%.2Float:7",
		_("Net Amount") + ":%.2Float:7",

	]

	
	columns = (
		columns
		+ [
			_("Signature_&_Stamp") + ":Text:10",
		]
		
	)

	return columns

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


def get_salary_slip(from_date,to_date,filters,department):
	conditions, filters = get_conditions(from_date,to_date,filters,department)
	

	filters.update({"from_date": filters.get("from_date"), "to_date": filters.get("to_date")})
	conditions, filters = get_conditions(from_date,to_date,filters,department)
	

	salary_slips = frappe.db.sql("""
    SELECT ss.* ,e.status,e.relieving_date,e.lunch_rate,e.travel_rate,e.night_rate
    FROM `tabSalary Slip` AS ss
    JOIN `tabEmployee` AS e ON ss.employee = e.name
    WHERE e.ot_enable = 'Yes' and %s
    ORDER BY ss.department, ss.employee"""
	%conditions, filters, as_dict=1)


	return salary_slips or []


def get_conditions(from_date,to_date,filters,department):
	conditions="" 
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}
	if filters.get("docstatus"):
		conditions += "ss.docstatus = {0}".format(doc_status[filters.get("docstatus")])
	if department: conditions += " and ss.department= '%s'" % department


	if from_date: conditions += " and ss.start_date>= '%s'" % from_date
	if to_date: conditions += " and ss.end_date<= '%s'" % to_date
	if filters.get("employee"): conditions += " and ss.employee= '%s'" % filters["employee"]
	if filters.get("company"): conditions += " and ss.company= '%s'" % filters["company"]
	if filters.get("department"): conditions += " and ss.department= '%s'" % filters["department"]
	if filters.get("designation"): conditions += " and ss.designation='%s'" % filters["designation"]
	# if filters.get("shift"): conditions += " and att.shift='%s'" % filters["shift"]
	if filters.get("section"): conditions += " and ss.section='%s'" % filters["section"]
	if filters.get("floor"): conditions += " and ss.floor='%s'" % filters["floor"]
	if filters.get("facility_or_line"): conditions += " and ss.facility_or_line='%s'" % filters["facility_or_line"]
	if filters.get("group_name"): conditions += " and ss.group='%s'" % filters["group_name"]
	if filters.get("grade"): conditions += " and ss.grade='%s'" % filters["grade"]
	if filters.get("mode_of_payment"): conditions += " and ss.mode_of_payment='%s'" % filters["mode_of_payment"]
	if filters.get("bank"): conditions += " and ss.bank_name='%s'" % filters["bank"]
	# if filters.get("sub_department"): conditions += " and ss.sub_department like '%s'" % filters["sub_department"]
	if filters.get("employee_type"):
		if (filters["employee_type"]=="New Join"):
			conditions += " and ss.date_of_joining between ss.start_date and ss.end_date"
		if (filters["employee_type"]=="Active"):
			conditions += " and e.status='Active' "
		if (filters["employee_type"]=="Left"):
			conditions += " and e.status='Left' and e.relieving_date between ss.start_date and ss.end_date"


	return conditions, filters

def get_basic(ss):
	return frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'B'}, ['default_amount','amount'])

# def get_salary_basic(ss):
	# return frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'B'}, 'amount')


