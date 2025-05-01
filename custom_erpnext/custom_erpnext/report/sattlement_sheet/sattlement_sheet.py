from datetime import datetime, timedelta,date
import frappe
from frappe import _
from frappe.utils import add_days, cstr, date_diff, get_first_day, get_last_day, getdate


def execute(filters= None):
	if not filters:
		filters = {}
	
	columns = get_columns()
	data=get_data(filters)
	
	return columns, data
	


def get_columns():
	 return [
		_("Employee") + ":Data:200",
        _("Employee Name") + ":Data:200",
		_("Department") + ":Data:200",
        _("Designation") + ":Data:200",
		_("Reason") + ":Data:200",
        _("Posting Date") + ":Date:200",
		_("Date Of Joining") + ":Date:200",
        _("Last Date") + ":Date:200",
		_("Length of Service") + ":Data:200",
        _("Basic") + ":Currency:200",
		_("Medical Allowance") + ":Currency:200",
        _("House Rent") + ":Currency:200",
		_("Gross Salary") + ":Currency:200",
        _("Present Days") + ":Data:200",
		_("Overtime") + ":Data:200",
        _("Night Days") + ":Data:200",
		_("Absent Days") + ":Data:200",
        _("Leave Days") + ":Data:200",
		_("Leave Without Pay Days") + ":Data:200",
        _("WagesSalary Pay Period Total Days") + ":Data:200",
		_("Overtime Rate") + ":Currency:200",
        _("Leave EL Total Days") + ":Data:200",
		_("Arrear") + ":Data:200",
        _("Total Years for Per Year Compensation") + ":Data:200",
		_("Lunch Rate") + ":Data:200",
        _("Travel Rate") + ":Data:200",
		_("Night Rate") + ":Data:200",
        _("Sub Total Payment Entitled") + ":Currency:200",
		_("WagesSalary Pay Period Total Days Payment") + ":Currency:200",
        _("Overtime Payment") + ":Currency:200",
		_("Leave EL Total Payment") + ":Currency:200",
        _("P F Fund") + ":Currency:200",
		_("Total Per Year Compensation Amount") + ":Currency:200",
		_("Lunch Amount") + ":Currency:200",
        _("Travel Amount") + ":Currency:200",
		_("Night Amount") + ":Currency:200",
        _("Number of Basic for Notice pay 120 Day pay") + ":Data:200",
		_("Number of Basic for Service Benefit") + ":Data:200",
        _("Gross Total Payment Entitiled") + ":Currency:200",
		_("Total Notice Pay") + ":Currency:200",
        _("Total Service Benefit Pay") + ":Currency:200",
		_("Total Days for Lay Off") + ":Data:200",
		_("Total Days For Friday") + ":Data:200",
        _("Total Days For Medical allow") + ":Data:200",
		_("AbsentWithout Pay Leave Days") + ":Data:200",
        _("Total Basic For Instant resign") + ":Data:200",
		_("Total Adjustment") + ":Currency:200",
        _("Lay Off Amount") + ":Currency:200",
		_("Amount for Friday 100 basic and Medical allowance") + ":Currency:200",
        _("Medical Allow Amount") + ":Currency:200",
		_("AbsentWithout Pay Leave Amount") + ":Currency:200",
		_("Amount For Instant resign") + ":Currency:200",
        _("Net Payment Entitled") + ":Currency:200",
		_("Less Provident Found By Cheque") + ":Currency:200",
		_("Balance Money Paid By Cash") + ":Currency:200",
        # _("Employee") + ":Data:200",
		# _("Remarks") + ":Text:10",
    ]

def get_data(filters):
	from_date = get_first_day(filters["month"] + "-" + filters["year"])
	to_date = get_last_day(filters["month"] + "-" + filters["year"])
	conditions, filters = get_conditions(from_date,to_date,filters)	
	result = frappe.db.sql("""
  	SELECT 
    employee,employee_name,department,designation,reason,posting_date,date_of_joining,last_date,length_of_service,basic,medical_allowance,house_rent,gross_salary,
	present_days,overtime,night_days,absent_days,leave_days, leave_without_pay_days,
	wagessalary_pay_period_total_days,overtime_rate,leave_el_total_days,arrear,total_years_for_per_year_compensation,lunch_rate,travel_rate,night_rate,sub_total_payment_entitled,
	wagessalary_pay_period_total_days_payment,overtime_payment,leave_el_total_payment,p_f_fund,total_per_year_compensation_amount,lunch_amount,travel_amount,night_amount,
	number_of_basic_for_notice_pay_120_day_pay,number_of_basic_for_service_benefit,gross_total_payment_entitiled,total_notice_pay,total_service_benefit_pay,
	total_days_for_lay_off,total_days_for_friday,total_days_for_medical_allow,absentwithout_pay_leave_days,total_basic_for_instant_resign,total_adjustment,lay_off_amount,amount_for_friday_100_basic_and_medical_allowance,
	medical_allow_amount,absentwithout_pay_leave_amount,amount_for_instant_resign,net_payment_entitled,less_provident_found_by_cheque,balance_money_paid_by_cash
						
	FROM `tabEmployee Settlement` where 1=1 %s
	"""% (conditions), as_list=True)

	return result
	
def get_conditions(from_date,to_date,filters):
	conditions="" 
	if from_date: conditions += " and last_date>= '%s'" % from_date
	if to_date: conditions += " and last_date<= '%s'" % to_date
	if filters.get("employee"): conditions += " and employee= '%s'" % filters["employee"]
	if filters.get("department"): conditions += " and department= '%s'" % filters["department"]
	if filters.get("designation"): conditions += " and designation='%s'" % filters["designation"]
	# if filters.get("shift"): conditions += " and att.shift='%s'" % filters["shift"]

	return conditions, filters
