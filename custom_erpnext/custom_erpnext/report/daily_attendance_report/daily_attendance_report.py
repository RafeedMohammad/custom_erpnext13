# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
#import datetime
from datetime import datetime, timedelta
from frappe import _

def execute(filters= None):
	if not filters:
		filters = {}
	columns = get_columns()
	data = get_attendance(filters)
	chart = get_chart(None)
	index_of_status = columns.index("Status:Data/:120")
	report_summary = get_report_summary(data,index_of_status)
	
	for i in range(0,len(data)):
		if data[i][index_of_status]=='Present':
			data[i][index_of_status]='P'
		elif data[i][index_of_status]=='Absent':
			data[i][index_of_status]='A'
		elif data[i][index_of_status]=='Late':
			data[i][index_of_status]='L'
		elif data[i][index_of_status]=='Weekly Off':
			data[i][index_of_status]='WO'
		elif data[i][index_of_status]=='Holiday':
			data[i][index_of_status]='H'
	
	return columns, data, None, chart, report_summary
	


def get_columns():
	return [
		_("Employee No") + ":Data/:120",
		_("Name") + ":Link/Employee:120",
		_("Designation") + ":Data/:120",
		_("Department") + ":Data/:120",
		_("Shift") + ":Data/:120",
		_("In Time") + ":Data/Attendance:120",
		_("Late") + ":Data/Attendance:120",
		_("Out Time") + ":Data/Attendance:120",
		_("OT") + ":Data/Attendance:120",
		_("Status") + ":Data/:120",
	]

def get_attendance(filters):
	type = frappe.db.get_value('User', frappe.session.user, 'type')
	if type is None:
		max_allowed_hour=13
		max_allowed_minute=00
	else:
		type_float=float(type)
		max_allowed_hour=int(type_float)
		max_allowed_minute=int((type_float%1)*60)

	rounded_over_time1 = frappe.db.get_value('Company', filters.company, 'rounding_overtime')
	rounded_over_time2 = frappe.db.get_value('Company', filters.company, 'rounding_overtime_for_extra_30min')

	conditions, filters = get_conditions(filters)
	result= frappe.db.sql("""select DISTINCT tabEmployee.employee,  tabAttendance.employee_name, tabEmployee.designation,tabAttendance.department,tabAttendance.shift,
	tabAttendance.in_time, tabAttendance.late_entry_duration, tabAttendance.out_time, tabAttendance.rounded_ot, tabAttendance.status,
	tabAttendance.shift_start,tabAttendance.shift_end,`tabAttendance`.leave_type
	FROM tabAttendance
	LEFT JOIN tabEmployee ON tabEmployee.name = tabAttendance.employee 
	where  %s
	ORDER BY tabEmployee.employee , tabAttendance.attendance_date""" 
		% conditions, 
		as_list=1)
		
	
	for i in range(0, len(result)):
		
		if result[i][9]=='Absent':
			result[i][5]=result[i][6]=result[i][7]="00:00"
		elif result[i][9]=='On Leave':
			result[i][5]=result[i][6]=result[i][7]="00:00"
			result[i][9]=result[i][12]


		elif result[i][7] is None:
			if result[i][5] !=None:
				result[i][5]=datetime.strftime(result[i][5],'%H:%M')
			if ((result[i][9]=="Weekly Off" or result[i][9]=="Holiday")and max_allowed_hour<10):
					result[i][5]=result[i][7]=None
					result[i][8]=0
			continue
		elif result[i][11] is None:
			continue
		else:
			if (max_allowed_hour>10): 
				pass
			elif(max_allowed_minute>10):
				if(result[i][7]>result[i][11]):
					overtime=result[i][7]-result[i][11]
					minute1=int(str(overtime).split(":")[1])

					#result[i][3]=overtime
					if(overtime>timedelta( hours=max_allowed_hour, minutes=max_allowed_minute+10)):
						result[i][7]=result[i][11]+timedelta(hours=max_allowed_hour,minutes=max_allowed_minute+(minute1%10))
						result[i][8]=max_allowed_hour+(max_allowed_minute/60)

					elif(overtime>=timedelta( hours=max_allowed_hour, minutes=max_allowed_minute-rounded_over_time2)):
						result[i][8]=max_allowed_hour+(max_allowed_minute/60)
					elif(int(str(overtime).split(":")[1])<rounded_over_time1):
						result[i][7]=result[i][11]+timedelta(hours=result[i][8],minutes=minute1%10)
			else:
				if(result[i][7]>result[i][11]):
					overtime=result[i][7]-result[i][11]
					minute1=int(str(overtime).split(":")[1])

					#result[i][3]=overtime
					if(overtime>timedelta( hours=max_allowed_hour)):
						result[i][7]=(result[i][11])+timedelta(hours=max_allowed_hour,minutes=minute1%10)
						result[i][8]=max_allowed_hour

					elif(minute1<rounded_over_time1):
						result[i][7]=result[i][11]+timedelta(hours=result[i][8],minutes=minute1%10)
		
									

			result[i][7]=datetime.strftime(result[i][7],'%H:%M')

			if(result[i][5]<result[i][10] and max_allowed_hour<10):
				early_entry_diff_min=int(str(result[i][10]-result[i][5]).split(":")[1])%10
				result[i][5]=result[i][10]-timedelta(minutes=early_entry_diff_min)

			if ((result[i][9]=="Weekly Off" or result[i][9]=="Holiday" )and max_allowed_hour<10):
					result[i][5]=result[i][7]=None
					result[i][8]=0
		if not isinstance(result[i][5],str) :
			if result[i][5]!=None:
				result[i][5]=datetime.strftime(result[i][5],'%H:%M')



		
	return result


def get_conditions(filters):
	conditions="" 
	if filters.get("date"): conditions += " tabAttendance.attendance_date = '%s'" % filters["date"]
	if filters.get("company"): conditions += " and tabAttendance.company= '%s'" % filters["company"]
	if filters.get("employee"): conditions += " and tabAttendance.employee= '%s'" % filters["employee"]
	if filters.get("department"): conditions += " and tabAttendance.department= '%s'" % filters["department"]
	if filters.get("designation"): conditions += " and tabEmployee.designation='%s'" % filters["designation"]
	if filters.get("shift"): conditions += " and tabAttendance.shift='%s'" % filters["shift"]
	if filters.get("section"): conditions += " and tabEmployee.section='%s'" % filters["section"]
	if filters.get("floor"): conditions += " and tabEmployee.floor='%s'" % filters["floor"]
	if filters.get("facility_or_line"): conditions += " and tabEmployee.facility_or_line='%s'" % filters["facility_or_line"]
	if filters.get("group_name"): conditions += " and tabEmployee.group='%s'" % filters["group_name"]
	if filters.get("status"): conditions += " and tabAttendance.status='%s'" % filters["status"]

	return conditions, filters

def get_chart(data):
	if not data:
		return None

def get_report_summary(data,a):
	if not data:
		return None

	total_present=total_absent=total_leave=total_late=work_from_home=total_weekly_off=total_holiday=0
	for i in range(len(data)):
		if data[i][a] == 'Present':
			total_present = total_present+1 
		elif data[i][a] == 'Absent':
			total_absent = total_absent+1
		elif data[i][a] in ['On Leave' , 'SL','CL','EL','OL','RL','ML','MCL', 'Maternity Leave', 'Sick Leave', 'Miscarriage Leave','Casual Leave','Earn Leave','Leave Without Pay']:
			total_leave = total_leave+1
		elif data[i][a] == 'Late':
			total_late = total_late+1 
		elif data[i][a] == 'Weekly Off':
			total_weekly_off = total_weekly_off+1
		elif data[i][a] == 'Holiday':
			total_holiday = total_holiday+1


	return [
		 {
		 	"value": total_present,
		 	"label": _("Total Present"),
		 	"datatype": "Int",
		 },
		{
			"value": total_absent,
			"label": _("Total Absent"),
			"datatype": "Int",
		},
		{
			"value": total_leave,
			"label": _("Total Leave"),
			"datatype": "Int",
		},
		{
			"value": total_late,
			"label": _("Total Late"),
			"datatype": "Int",
		},
		{
			"value": total_weekly_off,
			"label": _("Total Weekly Off"),
			"datatype": "Int",
		},
		{
			"value": total_holiday,
			"label": _("Total Holiday"),
			"datatype": "Int",
		},
	]