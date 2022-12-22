# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import frappe
from typing import List
from frappe import _
from frappe.utils import cint,getdate
from calendar import monthrange

def execute(filters=None):
	if not filters:
		filters = {}
	
	columns = get_columns()
	data = get_summary(filters)
	return columns, data

	
def get_columns():
	return [
		_("Department") + ":Link/Department:120",
		_("Manpower") + ":Link/Employee:120",
		_("Gross") + ":Currency/Salary Slip:120",
		_("Net Payment") + ":Currency/Salary Slip:120",
		_("Total Payable") + ":Data/Salary Slip:120",
		
	]
def get_conditons(filters):
	conditions = ""
	
	#changes done here
	

	#changes done ended here
	if filters.get("company"): 
		conditions += "where `tabSalary Slip`.company= '%s'" % filters["company"]
	if filters.get("month") and filters.get("year"):

		total_number_of_days = get_total_days_in_month(filters)
		start_final_date =  filters.get("year")+"-" + str(int(filters.get("month"))).zfill(2) +"-"+  "01"		
		end_final_date = filters.get("year") +"-" + str(int(filters.get("month"))).zfill(2) + "-" + str(total_number_of_days)
	
		conditions += "and `tabSalary Slip`.start_date >= '%s' and `tabSalary Slip`.end_date <=  '%s'" % (start_final_date, end_final_date)
	return conditions,filters

def get_summary(filters):
	conditions,filters = get_conditons(filters)
	return frappe.db.sql("""select department,COUNT(employee),SUM(gross_pay),
	SUM(net_pay),(SUM(net_pay)-(COUNT(employee)*10))from 
	`tabSalary Slip` %s GROUP BY `tabSalary Slip`.department""" % conditions, as_list = 1)

@frappe.whitelist()
def get_salary_slip_years() -> List:
	"""Returns all the years for which salary slip records exist"""
	salary_slip_years = frappe.db.sql("""SELECT DISTINCT YEAR(end_date) from `tabSalary Slip`""",as_list = 1)

	if salary_slip_years:
		salary_slip_years.sort(reverse=True)
	else:
		salary_slip_years = [getdate().year]

	return salary_slip_years

def get_total_days_in_month(filters) -> int:
	return monthrange(cint(filters.get("year")), cint(filters.get("month")))[1]