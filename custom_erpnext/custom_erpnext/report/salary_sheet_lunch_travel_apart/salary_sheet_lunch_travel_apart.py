from datetime import datetime, timedelta
import frappe
from frappe.utils import flt
from frappe import _
from frappe.utils import add_days, cstr, date_diff, get_first_day, get_last_day, getdate

def execute(filters = None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data

def get_data(filters= None):
	type = frappe.db.get_value('User', frappe.session.user, 'type')
	if type is None or float(type)>11:
		hours_for_ot=34
	else:
		hours_for_ot=float(type)
	
	from_date = get_first_day(filters["month"] + "-" + filters["year"])
	to_date = get_last_day(filters["month"] + "-" + filters["year"])
	if not filters:
		filters = {}
	data = []
	total_result=[]
	departments = frappe.db.get_list("Department", pluck="name", order_by="name")
	for department in departments:
		salary_slips = get_salary_slip(from_date,to_date,filters,department)
		if len(salary_slips)==None:
			continue
		#columns, ded_types = get_columns(salary_slips)
		# columns=get_columns(salary_slips)
		
		ss_ded_map = get_ss_ded_map(salary_slips)

		
		if len(salary_slips) >= 1:
			data.append({"department": department})
		# else:
		# 	row = frappe._dict({"leave_type": department})
		result=[]

		for ss in salary_slips:
			allowance = 0
			acctual_basic,salary_slip_basic = get_basic(ss.name)
			if acctual_basic is None:
				acctual_basic = 0
			# salary_slip_basic = get_salary_basic(ss.name)
			if salary_slip_basic is None:
				salary_slip_basic = 0
			actual_allowance= (get_default_medical(ss.name) or 2375)+(acctual_basic/2)
			allowance = get_allowance(ss.name)
			acctual_lunch=get_lunch_tr_allowance(ss.name)+get_lunch(ss.name)+get_convanse(ss.name)
			if acctual_lunch is None:
				acctual_lunch=0
			leaves=frappe.db.sql('''select lt.name leave_name, ifnull(tot_lv,0) total_leaves from `tabLeave Type` lt left join  (select lti.name, count(a.attendance_date) tot_lv from `tabLeave Type` lti join tabAttendance a on lti.name = a.leave_type where a.employee=%s and a.status="On Leave" and a.attendance_date between %s and %s group by lti.name) ali on lt.name = ali.name;''',(ss.employee,ss.start_date,ss.end_date), as_dict=1)
			CL,EL,ML,SL,OL=0,0,0,0,0
			for l in leaves:
				if l.leave_name=="CL":
					CL=l.total_leaves
				elif l.leave_name=="EL":
					EL=l.total_leaves
				elif l.leave_name=="ML":
					ML=l.total_leaves
				elif l.leave_name=="SL":
					SL=l.total_leaves
				elif l.leave_name=="OL":
					OL=l.total_leaves

			
			if hours_for_ot>=10:
				overtime_hours=ss.overtime_hours
				ot_amount=ss.total_overtime_pay
				holiday_allowance=0 #it will deduct from gross and net pay so if acctual it is 0 and if buyer all its amount will deduct.
				# lunch=float(acctual_lunch)


			else:
				ot_hours = frappe.db.sql("""SELECT SUM(case when rounded_ot>%s then %s else rounded_ot end) FROM `tabAttendance` where status not in ('Holiday','Weekly Off') and employee=%s AND attendance_date between %s and %s group by employee""",
				(hours_for_ot,hours_for_ot,ss.employee, ss.start_date, ss.end_date))
				overtime_hours = ot_hours[0][0] if ot_hours else 0  
				ot_amount=(ot_hours[0][0] if ot_hours else 0  )*float(ss.overtime_rate)
				holiday_allowance=ss.holiday_allowance or 0 
				# if ss.present_days!=0:
				# 	lunch=(float(acctual_lunch)*ss.present_days/(ss.present_days+max(ss.late_days,ss.working_holidays)))#previously we count working_holidays in late_days 




			row = [
				None,
				#ss.name,
				ss.employee,
				ss.employee_name,
				ss.date_of_joining,
				# ss.branch,
				# ss.department,
				ss.designation,
				# ss.company,
				# ss.start_date,
				# ss.end_date,
				round(acctual_basic,0),
				round(actual_allowance,0)-round((get_default_medical(ss.name) or 2375),0),
				round((get_default_medical(ss.name) or 2375),0),
				round(acctual_basic + actual_allowance,0),
				ss.present_days,
				off_days(ss.employee, ss.start_date, ss.end_date),
				# len(frappe.db.sql('''select * from tabAttendance where employee=%s and status="On Leave" and leave_type='CL' and attendance_date between %s and %s''',(ss.employee,ss.start_date,ss.end_date))),
				# len(frappe.db.sql('''select * from tabAttendance where employee=%s and status="On Leave" and leave_type='EL' and attendance_date between %s and %s''',(ss.employee,ss.start_date,ss.end_date))),
				# len(frappe.db.sql('''select * from tabAttendance where employee=%s and status="On Leave" and leave_type='ML' and attendance_date between %s and %s''',(ss.employee,ss.start_date,ss.end_date))),
				# len(frappe.db.sql('''select * from tabAttendance where employee=%s and status="On Leave" and leave_type='SL' and attendance_date between %s and %s''',(ss.employee,ss.start_date,ss.end_date))),
				# len(frappe.db.sql('''select * from tabAttendance where employee=%s and status="On Leave" and leave_type='OL' and attendance_date between %s and %s''',(ss.employee,ss.start_date,ss.end_date))),
				CL,
				EL,
				ML,
				SL,
				OL,


				ss.absent_days,
				# ss.gross_pay,
				round(float((salary_slip_basic+allowance) or 0),0),
				round(float(overtime_hours or 0),1),
				#ss.total_overtime_pay,
				round(float(ot_amount or 0),0),
				get_attendance_bonus(ss.name),
				# get_lunch_tr_allowance(ss.name),
				#float(acctual_lunch),
				get_lunch(ss.name),
				get_convanse(ss.name),
				ss.night_days,
				get_night_allowance(ss.name),
				ss.arear,
				round(ss.gross_pay-float(ss.total_overtime_pay)-float(acctual_lunch)-float(holiday_allowance)+float(acctual_lunch)+float(ot_amount),0),
				round(ss.absent_deduction or 0,0),
				round(get_pf(ss.name),0),
				round(get_late_amt(ss.name),0),
				get_stamp(ss.name),
				round(ss.income_tax,0),
				round(ss.other_deduction,0),

				
				
			]

			# for d in ded_types:
			# 	row.append(ss_ded_map.get(ss.name, {}).get(d))
			
			row += [round(ss.total_loan_repayment,0),(round(ss.total_deduction,0)+round(ss.total_loan_repayment,0)), round((ss.net_pay-float(ss.total_overtime_pay)-float(acctual_lunch)-float(holiday_allowance)+float(acctual_lunch)+float(ot_amount)),0), None]
			

			
			for i in range(len(row)): 
				if i>16 and i<len(row)-1: # Use the length of 'row' to avoid accessing out of bounds
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



	return data
	


def get_columns():
	columns = [
		_("Department") + "::150",
		_("Employee") + "::80",
		_("Employee Name") + "::40",
		_("Joining_Date") + "::12",
		_("Designation") + "::40",
		# _("Start Date") + "::80",
		# _("End Date") + "::80",
		_("Basic") + "::10",
		_("H-rent") + "::10",
		_("Medical") + "::10",
		_("Gross") + "::10",
		_("P") + ":Integer:5",
		_("W/H") + ":Integer:5",
		_("CL") + ":Integer:5",
		_("EL") + ":Integer:5",
		_("ML") + ":Integer:5",
		_("SL") + ":Integer:5",
		_("LL LWP") + ":Integer:5",
		_("A") + ":Integer:5",
		_("Total Salary") + ":Integer:10",
		_("O.T Hr.") + ":%.2Float:7",
		_("O.T Amt.") + "::10",
		_("Attn. Bon.") + ":Integer:5",
		_("Lun") + ":Integer:20",
		_("Tr") + ":Integer:20",
		_("Night Allow Day") + ":Integer:5",
		_("Night Allow Amt") + ":Integer:20",
		_("Arrear") + ":Integer:10",
		_("Gross Payable") + ":Integer:20",


		#_("Date of Joining") + "::80",
	#("Total Salary") + ":Float:80",

	]

	# salary_components = { _("Deduction"): []}
	# if salary_slips:
	# 	for component in frappe.db.sql(
	# 		"""select distinct sd.salary_component, sc.type
	# 		from `tabSalary Detail` sd, `tabSalary Component` sc
	# 		where sc.name=sd.salary_component and sc.type = 'Deduction' and sd.parent in (%s)"""
	# 		% (", ".join(["%s"] * len(salary_slips))),
	# 		tuple([d.name for d in salary_slips]),
	# 		as_dict=1,
	# 	):
	# 		salary_components[_(component.type)].append(component.salary_component)

	columns = (
		columns
		# + [(d + ":Integer:10") for d in salary_components[_("Deduction")]]
		+ [
			_("Abs Ded") + ":Integer:10",
			_("PF") + ":Integer:10",
			_("Late amt") + ":Integer:10",
			_("Sta mp") + ":Integer:10",
			_("Tax") + ":Integer:10",
			_("other Ded") + ":Integer:10",
			_("Advance") + ":Integer:10",
			_("Total Deduc tion") + ":Integer:20",
			_("Net Pay") + ":Integer:20",
			_("Signature_& Stamp") + ":Text:10",

		]
		
	)

	return columns#, salary_components[("Deduction")]




def get_salary_slip(from_date,to_date,filters,department):
	conditions, filters = get_conditions(from_date,to_date,filters,department)
	

	filters.update({"from_date": filters.get("from_date"), "to_date": filters.get("to_date")})
	conditions, filters = get_conditions(from_date,to_date,filters,department)
	

	salary_slips = frappe.db.sql("""select ss.*,e.status,e.relieving_date,e.lunch_rate,e.travel_rate,e.night_rate from `tabSalary Slip` as ss inner join tabEmployee as e on ss.employee=e.name WHERE %s ORDER BY ss.department,employee
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

def get_allowance(ss):
	#return frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'HR'}, 'SUM(amount)')
	return frappe.db.sql("""SELECT SUM(amount) FROM `tabSalary Detail` where parent=%s and abbr IN('M', 'HR')""", ss)[0][0]

def get_default_medical(ss):
	return frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'DM'}, ['default_amount'])

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

def get_pf(ss):
	return (frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'PF'}, 'amount') or 0)

def get_late_amt(ss):
	return (frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'LD'}, 'amount') or 0)

def get_stamp(ss):
	return (frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'ST'}, 'amount') or 0)