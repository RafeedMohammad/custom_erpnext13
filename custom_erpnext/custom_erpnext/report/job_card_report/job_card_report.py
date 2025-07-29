# Copyright (c) 2022, Lithe-Tech Limited and contributors
# For license information, please see license.txt

# import frappe



from datetime import datetime, timedelta
import frappe
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
		_("Date") + ":Date/:120",
		_("Employee") + ":Link/Employee:120",
		_("Shift") + ":Data/Attendance:120",
		_("In Time") + ":Data/Attendance:120",
		_("Late") + ":Data/Attendance:120",
		_("Out Time") + ":Data/Attendance:120",
		_("O.T.") + ":Data/Attendance:120",
		_("Status") + ":Data/:120",
		_("Department") + ":Data/:120",
		_("Designation") + ":Data/:120",
		_("Joining Date") + ":Data/:120",
		_("Emp Name") + ":Data/:120",
		_("Is night") + ":Data/:120",

	]

def get_attendance(filters):
	type = frappe.db.get_value('User', frappe.session.user, 'type')
	total_late_minutes = 0
	total_ot_hours = 0.0
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
	
	result= frappe.db.sql("""select DISTINCT att.attendance_date, att.employee, att.shift,
	att.in_time, att.late_entry_duration, att.out_time, att.rounded_ot, att.status,
	emp.department,emp.designation,emp.date_of_joining,emp.employee_name,
	CASE 
            WHEN att.in_time IS NOT NULL THEN att.is_night 
            ELSE NULL 
        END AS is_night,
	att.shift_start, att.shift_end, att.leave_type
	FROM tabAttendance as att
	INNER JOIN tabEmployee as emp ON emp.name = att.employee  	
	where %s and att.docstatus = 1
	ORDER BY att.attendance_date""" 
	% conditions, as_list=1)



	
	for i in range(0,len(result)):
		if result[i][7]=="Absent":
			result[i][3]=result[i][4]=result[i][5]="00:00"
		
		elif result[i][7]=='On Leave' :
			result[i][3]=result[i][4]=result[i][5]="00:00"
			result[i][7]= result[i][15]
		
		elif result[i][5] is None:
			if result[i][3] !=None:
				result[i][3]=datetime.strftime(result[i][3],'%H:%M')
			if ((result[i][7]=="Weekly Off" or result[i][7]=="Holiday" )and max_allowed_hour<10):
				result[i][3]=result[i][5]=None
				result[i][6]=0
			continue
		elif result[i][14] is None:
			continue
		
		else:
			if (max_allowed_hour>10): 
				pass
			elif(max_allowed_minute>10):
				if(result[i][5]>result[i][14]):
					ot_difference=result[i][5]-result[i][14]
					minute1=int(str(ot_difference).split(":")[1])

					if(ot_difference>timedelta(hours=max_allowed_hour,minutes=max_allowed_minute+10)):
						result[i][5]=result[i][14]+timedelta(hours=max_allowed_hour,minutes=max_allowed_minute+(minute1%10))
						result[i][6]=max_allowed_hour+(max_allowed_minute/60)

					elif(ot_difference>=timedelta(hours=max_allowed_hour,minutes=max_allowed_minute-rounded_over_time2)):#rounding_time2
						result[i][6]=max_allowed_hour+(max_allowed_minute/60)
					elif(ot_difference<timedelta(hours=result[i][6],minutes=rounded_over_time1)):#rounding_time1
						pass
					elif(ot_difference<timedelta(hours=result[i][6],minutes=rounded_over_time1)):#rounding_time1
						result[i][5]=result[i][14]+timedelta(hours=max_allowed_hour,minutes=(minute1%10))




			elif(max_allowed_minute<10):
				if(result[i][5]>result[i][14]):
					ot_difference=result[i][5]-result[i][14]
					minute1=int(str(ot_difference).split(":")[1])

					if(ot_difference>timedelta(hours=max_allowed_hour,minutes=max_allowed_minute)):
						result[i][5]=result[i][14]+timedelta(hours=max_allowed_hour,minutes=(minute1%10))
						result[i][6]=max_allowed_hour#+(max_allowed_minute/60)

					elif(minute1>rounded_over_time1):	#rounding_time
						result[i][5]=result[i][14]+timedelta(hours=result[i][6],minutes=(minute1%10))
			result[i][5]=datetime.strftime(result[i][5],'%H:%M')

			#for late
			if(result[i][3]<result[i][13] and max_allowed_hour<10):
				early_entry_diff_min=int(str(result[i][13]-result[i][3]).split(":")[1])%10
				result[i][3]=result[i][13]-timedelta(minutes=early_entry_diff_min)
			result[i][3]=datetime.strftime(result[i][3],'%H:%M')
			
			if ((result[i][7]=="Weekly Off" or result[i][7]=="Holiday" )and max_allowed_hour<10):
					result[i][3]=result[i][5]=None
					result[i][6]=0
		try:
			total_ot_hours += float(result[i][6])
		except:
			pass

			
		
	total_late_minutes,total_ot=frappe.db.sql("""select DISTINCT SUM(IFNULL(TIME_TO_SEC(att.late_entry_duration),0)),SUM(IFNULL(att.rounded_ot,0))
	FROM tabAttendance as att
	INNER JOIN tabEmployee as emp ON emp.name = att.employee  	
	where %s and att.docstatus = 1 and att.status!="On Leave"
	ORDER BY att.attendance_date""" 
	% conditions)[0]
		
	total_row = [""] * 20
	total_row[1] = "Total"
	if(total_late_minutes):
		total_row[4] = round(total_late_minutes/60,2)#"{:02d}:{:02d}".format(total_late_minutes // 60, total_late_minutes % 60)
	else:
		total_row[4]=0
	
	total_row[6] = round(total_ot_hours, 2)
	
	result.append(total_row)		
	return result


def get_conditions(filters):
    conditions="" 
    if filters.get("from_date"): conditions += " att.attendance_date>= '%s'" % filters["from_date"]
    if filters.get("to_date"): conditions += " and att.attendance_date<= '%s'" % filters["to_date"]
    if filters.get("employee"): conditions += " and att.employee= '%s'" % filters["employee"]
    if filters.get("company"): conditions += " and att.company= '%s'" % filters["company"]
    if filters.get("department"): conditions += " and att.department= '%s'" % filters["department"]
    if filters.get("designation"): conditions += " and tabEmployee.designation='%s'" % filters["designation"]
    if filters.get("shift"): conditions += " and att.shift='%s'" % filters["shift"]
    if filters.get("section"): conditions += " and emp.section='%s'" % filters["section"]
    if filters.get("floor"): conditions += " and emp.floor='%s'" % filters["floor"]
    if filters.get("facility_or_line"): conditions += " and emp.facility_or_line='%s'" % filters["facility_or_line"]
    if filters.get("group_name"): conditions += " and emp.group='%s'" % filters["group_name"]

    return conditions, filters

def get_chart(data):
	if not data:
		return None

def get_report_summary(data,a):
	if not data:
		return None

	total_present=total_absent=total_leave=total_late=work_from_home=total_weekly_off=total_holiday=total_null=total_night=0
	for i in range(len(data)):
		total_null=total_null+1

		if data[i][a] == 'Present':
			total_present = total_present+1 
			if data[i][12] =='Yes':
				total_night=total_night+1
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

	#total_employee = frappe.db.sql("""SELECT count(status) FROM `tabAttendance` where status='Present'""")
	
	#fnf_pending = len([entry.name for entry in data if not entry.full_and_final_statement])
	#questionnaires_pending = len([entry.name for entry in data if not entry.questionnaire])

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
		{
			"value": total_night,
			"label": _("Total Night"),
			"datatype": "Int",
		},	
	]