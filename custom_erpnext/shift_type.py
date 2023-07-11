# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import itertools
from datetime import timedelta,datetime

from erpnext.hr.doctype.holiday_list.holiday_list import is_holiday

from frappe.utils import cint, get_datetime, get_time, getdate

from erpnext.buying.doctype.supplier_scorecard.supplier_scorecard import daterange

import frappe
from frappe.utils import today
from frappe.model.document import Document
from frappe.utils import cint, get_datetime, getdate
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee

from erpnext.hr.doctype.shift_type.shift_type import ShiftType


#from erpnext.hr.doctype.attendance.attendance import mark_attendance

from custom_erpnext.attendance import mark_attendance

# from erpnext.hr.doctype.employee_checkin.employee_checkin import (
# 	calculate_working_hours,
# 	mark_attendance_and_link_log,
# )
# from erpnext.hr.doctype.shift_assignment.shift_assignment import (
# 	get_actual_start_end_datetime_of_shift,
# 	get_employee_shift,
# )
from custom_erpnext.employee_checkin import (
	calculate_working_hours,
	mark_attendance_and_link_log,
)

from custom_erpnext.shift_assignment import (
	get_employee_shift,
	get_actual_start_end_datetime_of_shift,
)




class override_ShiftType(Document):
	@frappe.whitelist()
	def process_auto_attendance(self,from_date=None,to_date=None): #added from date to date in oder to access the date given in mark attendance in shift type front desk
		frappe.publish_realtime('msgprint', 'Starting process for '+self.name+' at-> '+str(datetime.now()))
		if from_date and to_date:
			self.process_attendance_after=from_date
			#self.name=name
			shift_start_time =to_date+" "+ str(self.start_time)
			self.last_sync_of_checkin = datetime.strptime(shift_start_time, "%Y-%m-%d %H:%M:%S")+timedelta(days=1)
			# added to set eligiable time for the shifts to process the attendance which is given in mark attendance in shift type front desk
		if (
			not cint(self.enable_auto_attendance)
			or not self.process_attendance_after
			or not self.last_sync_of_checkin
		):
			return
		filters = {
			"skip_auto_attendance": "0",
			#"attendance": ("is", "not set"),
			"time": (">=", self.process_attendance_after),
			"shift_actual_end": ("<", self.last_sync_of_checkin),
			"shift": self.name,
		}
		weekly_off_list=frappe.db.sql("""select holiday_date,weekly_off from tabHoliday where parent=%s and holiday_date between %s and %s""",
				(self.holiday_list,self.process_attendance_after,self.last_sync_of_checkin))

		logs = frappe.db.get_list(
			"Employee Checkin", fields="*", filters=filters, order_by="employee,time"
		)
		if logs:
			employee=logs[0].employee
			company =frappe.db.get_value("Employee", employee, "company")
			rounding_ot = frappe.db.get_value("Company", company, "rounding_overtime") 
		
		for key, group in itertools.groupby(
			logs, key=lambda x: (x["employee"], x["shift_actual_start"])
		):
			single_shift_logs = list(group)
			(
				attendance_status,
				working_hours,
				late_entry,
				early_exit,
				in_time,
				out_time,
				late_entry_duration,
				overtime,
			) = self.get_attendance(single_shift_logs,weekly_off_list)
			mark_attendance_and_link_log(
				single_shift_logs,
				attendance_status,
				key[1].date(),
				working_hours,
				late_entry,
				early_exit,
				in_time,
				out_time,
				self.name,
				late_entry_duration,
				overtime,
				rounding_ot,
			)
		for employee in self.get_assigned_employee(self.process_attendance_after, True):
			self.mark_absent_for_dates_with_no_attendance(employee)
		frappe.publish_realtime('msgprint', 'Ending process for '+self.name+' at-> '+str(datetime.now()))


	def get_attendance(self, logs,weekly_off_list):
		frappe.publish_realtime('msgprint', 'Starting Get_attendance for '+logs[0].employee+' at-> '+str(datetime.now()))
		"""Return attendance_status, working_hours, late_entry, early_exit, in_time, out_time
		for a set of logs belonging to a single shift.
		Assumtion:
		        1. These logs belongs to an single shift, single employee and is not in a holiday date.
		        2. Logs are in chronological order
		"""
		late_entry = early_exit = False
		total_working_hours, in_time, out_time, = calculate_working_hours(
			logs, self.determine_check_in_and_check_out, self.working_hours_calculation_based_on
		)

		# total_working_hours, in_time, out_time, weekly_off_check = calculate_working_hours(
		# 	logs, self.determine_check_in_and_check_out, self.working_hours_calculation_based_on, self.holiday_list, self.lunch_start, self.lunch_end, self.start_time, self.end_time##Change - Added parameter: self.holiday_list
		# )

		late_entry_duration=0
		overtime=timedelta(0)

		in_date1 = datetime.strptime(str(logs[0].shift_start).split(" ")[0], "%Y-%m-%d")
		weekly_off_check=None

		#weekly_off_check = frappe.db.get_value('Holiday', {'parent': self.holiday_list, 'holiday_date': in_date1}, 'weekly_off')
		for i in range(len(weekly_off_list)):
			if(weekly_off_list[i][0]==in_date1.date()):
				weekly_off_check= weekly_off_list[i][1]
				break


		# if (datetime.strptime(str(self.lunch_start), "%H:%M:%S") < datetime.strptime(str(self.start_time), "%H:%M:%S")):
		# 	start_time_to_lunch_duration=datetime.strptime(str(self.lunch_start), "%H:%M:%S")-datetime.strptime(str(self.start_time), "%H:%M:%S")+timedelta(days=1)
		# else:
		# 	start_time_to_lunch_duration=datetime.strptime(str(self.lunch_start), "%H:%M:%S")-datetime.strptime(str(self.start_time), "%H:%M:%S")

		# if(datetime.strptime(str(self.lunch_end), "%H:%M:%S") < datetime.strptime(str(self.lunch_start), "%H:%M:%S")):
		# 	lunch_duration	=datetime.strptime(str(self.lunch_end), "%H:%M:%S")-datetime.strptime(str(self.lunch_start), "%H:%M:%S")+timedelta(days=1)
		# else:
		# 	lunch_duration	=datetime.strptime(str(self.lunch_end), "%H:%M:%S")-datetime.strptime(str(self.lunch_start), "%H:%M:%S")


		if (
			cint(self.enable_entry_grace_period)
			and in_time
			and in_time > logs[0].shift_start + timedelta(minutes=cint(self.late_entry_grace_period))
		):
			late_entry = True
			# late_entry_time=round((in_time-logs[0].shift_start-timedelta(minutes=cint(self.late_entry_grace_period))).total_seconds() / 60)
			# late_entry_duration=str(int(late_entry_time/60)).zfill(2)+":"+str(late_entry_time%60).zfill(2)
			late_entry_duration=in_time-logs[0].shift_start-timedelta(minutes=cint(self.late_entry_grace_period))
			#late_entry_duration=str(int(late_entry_time/60)).zfill(2)+":"+str(late_entry_time%60).zfill(2)


		if (
			cint(self.enable_exit_grace_period)
			and out_time
			and out_time < logs[0].shift_end - timedelta(minutes=cint(self.early_exit_grace_period))
		):
			early_exit = True
		if (
			cint(self.enable_auto_attendance)
			and out_time
			and out_time > logs[0].shift_end #- timedelta(minutes=cint(self.early_exit_grace_period))
		):
			overtime=out_time-logs[0].shift_end
		if (out_time):
			start_time_to_lunch_duration,lunch_duration= self.lunch_timing()
			if(weekly_off_check==0 or weekly_off_check==1):
				if(in_time<= (logs[0].shift_start+start_time_to_lunch_duration) and (logs[0].shift_start+start_time_to_lunch_duration+lunch_duration) <= out_time):
					overtime=out_time-in_time-lunch_duration
				else:
					overtime=out_time-in_time
				# if(overtime>=timedelta(days=1)):
				# 	overtime=timedelta(days=1)-timedelta(minutes=1)


#if (lunch_start_datetime.time() > in_time_time) and (lunch_end_datetime.time() < out_time_time):

		#change start
		if(weekly_off_check == 1):
			return "Weekly Off", total_working_hours, 0, early_exit, in_time, out_time,0,overtime
		
		if(weekly_off_check==0):
			return "Holiday", total_working_hours, 0, early_exit, in_time, out_time, 0,overtime
		
		if(late_entry):
			return "Late", total_working_hours, late_entry, early_exit, in_time, out_time, late_entry_duration,overtime

		#change end

		if (
			self.working_hours_threshold_for_absent
			and total_working_hours < self.working_hours_threshold_for_absent
		): 
			return "Absent", total_working_hours, late_entry, early_exit, in_time, out_time,0,0
		if (
			self.working_hours_threshold_for_half_day
			and total_working_hours < self.working_hours_threshold_for_half_day
		):
			return "Half Day", total_working_hours, late_entry, early_exit, in_time, out_time,overtime
		return "Present", total_working_hours, late_entry, early_exit, in_time, out_time, late_entry_duration,overtime

	def mark_absent_for_dates_with_no_attendance(self, employee):
		"""Marks Absents for the given employee on working days in this shift which have no attendance marked.
		The Absent is marked starting from 'process_attendance_after' or employee creation date.
		"""
		date_of_joining, relieving_date, employee_creation = frappe.get_cached_value(
			"Employee", employee, ["date_of_joining", "relieving_date", "creation"]
		)
		if not date_of_joining:
			date_of_joining = employee_creation.date()
		start_date = max(getdate(self.process_attendance_after), date_of_joining)
		actual_shift_datetime = get_actual_start_end_datetime_of_shift(
			employee, get_datetime(self.last_sync_of_checkin), True
		)
		last_shift_time = (
			actual_shift_datetime[0]
			if actual_shift_datetime[0]
			else get_datetime(self.last_sync_of_checkin)
		)
		prev_shift = get_employee_shift(
			employee, last_shift_time.date() - timedelta(days=1), True, "reverse"
		)
		if prev_shift:
			end_date = (
				min(prev_shift.start_datetime.date(), relieving_date)
				if relieving_date
				else prev_shift.start_datetime.date()
			)
		else:
			return

		holiday_list_name = self.holiday_list

		start_time = get_time(self.start_time)
		
		if not holiday_list_name:
			holiday_list_name = get_holiday_list_for_employee(employee, False)


		for date in daterange(getdate(start_date), getdate(end_date)):
			check_if_weekly_off = frappe.db.get_value('Holiday', {'parent': holiday_list_name, 'holiday_date':date}, 'weekly_off')
			check_if_holiday=is_holiday(holiday_list_name, date)
			if check_if_holiday:
				# skip marking absent on a holiday
				#Dev: Can be changed because if it's a weekly holiday, the status is shown as 'W'
				if(check_if_weekly_off==1):
					attendance = mark_attendance(employee, date, "Weekly Off", self.name)
				attendance = mark_attendance(employee, date, "Holiday", self.name)
				
		
		# dates = get_filtered_date_list(employee, start_date, end_date, holiday_list=holiday_list_name)
		# for date in dates:
			#timestamp = datetime.combine(date, start_time)
			shift_details = get_employee_shift(employee, date, True)
			if shift_details and shift_details.shift_type.name == self.name:
				attendance = mark_attendance(employee, date, "Absent", self.name)
				if attendance:
					frappe.get_doc(
						{
							"doctype": "Comment",
							"comment_type": "Comment",
							"reference_doctype": "Attendance",
							"reference_name": attendance,
							"content": frappe._("Employee was marked Absent due to missing Employee Checkins."),
						}
					).insert(ignore_permissions=True)

	def get_assigned_employee(self, from_date=None, consider_default_shift=False):
		filters = {"start_date": (">", from_date), "shift_type": self.name, "docstatus": "1"}
		if not from_date:
			del filters["start_date"]

		assigned_employees = frappe.get_all("Shift Assignment", filters, pluck="employee")

		if consider_default_shift:
			filters = {"default_shift": self.name, "status": ["!=", "Inactive"]}
			default_shift_employees = frappe.get_all("Employee", filters, pluck="name")
			return list(set(assigned_employees + default_shift_employees))
		return assigned_employees
	
	def lunch_timing(self):
		if (datetime.strptime(str(self.lunch_start), "%H:%M:%S") < datetime.strptime(str(self.start_time), "%H:%M:%S")):
			start_time_to_lunch_duration=datetime.strptime(str(self.lunch_start), "%H:%M:%S")-datetime.strptime(str(self.start_time), "%H:%M:%S")+timedelta(days=1)
		else:
			start_time_to_lunch_duration=datetime.strptime(str(self.lunch_start), "%H:%M:%S")-datetime.strptime(str(self.start_time), "%H:%M:%S")

		if(datetime.strptime(str(self.lunch_end), "%H:%M:%S") < datetime.strptime(str(self.lunch_start), "%H:%M:%S")):
			lunch_duration	=datetime.strptime(str(self.lunch_end), "%H:%M:%S")-datetime.strptime(str(self.lunch_start), "%H:%M:%S")+timedelta(days=1)
		else:
			lunch_duration	=datetime.strptime(str(self.lunch_end), "%H:%M:%S")-datetime.strptime(str(self.lunch_start), "%H:%M:%S")
		return start_time_to_lunch_duration, lunch_duration



@frappe.whitelist()
def process_auto_attendance_for_all(from_date=None,to_date=None): #added from date to date in oder to access the date given in mark attendance in shift type
	shift_args1={
	#"name":doc.name,
	"from_date":from_date,
	"to_date":to_date,
	}
	# added in 10-7-23 for delete attendance
	#frappe.db.sql("""delete from tabAttendance where status in ("Present", "Absent", "Half Day", "Weekly Off", "Holiday", "Late") and attendance_date between %s and %s""",(from_date,to_date))
	#frappe.enqueue(method="test123",queue="long",**shift_args1)
	#frappe.enqueue_doc(doctype="Shift Type", name="Shift Type",method="test123",queue="long",timeout=3600,**shift_args1)
	frappe.enqueue("custom_erpnext.shift_type.process_auto_attendance_intermediate_function",queue="long",**shift_args1)

def process_auto_attendance_intermediate_function(from_date=None,to_date=None):
	shift_list = frappe.get_all("Shift Type", filters={"enable_auto_attendance": "1"}, pluck="name")
	for shift in shift_list:
		doc = frappe.get_cached_doc("Shift Type", shift)
		shift_args={
		#"name":doc.name,
		"from_date":from_date,
		"to_date":to_date,
		}
		doc.process_auto_attendance(**shift_args)
		#frappe.enqueue_doc("Shift Type",doc.name,"process_auto_attendance",timeout=1800,**shift_args)

def get_filtered_date_list(
	employee, start_date, end_date, filter_attendance=True, holiday_list=None
):
	"""Returns a list of dates after removing the dates with attendance and holidays"""
	base_dates_query = """select adddate(%(start_date)s, t2.i*100 + t1.i*10 + t0.i) selected_date from
		(select 0 i union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t0,
		(select 0 i union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t1,
		(select 0 i union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t2"""
	condition_query = ""
	if filter_attendance:
		condition_query += """ and a.selected_date not in (
			select attendance_date from `tabAttendance`
			where docstatus = 1 and employee = %(employee)s
			and attendance_date between %(start_date)s and %(end_date)s)"""
	if holiday_list:
		condition_query += """ and a.selected_date not in (
			select holiday_date from `tabHoliday` where parenttype = 'Holiday List' and
    		parentfield = 'holidays' and parent = %(holiday_list)s
    		and holiday_date between %(start_date)s and %(end_date)s)"""

	dates = frappe.db.sql(
		"""select * from
		({base_dates_query}) as a
		where a.selected_date <= %(end_date)s {condition_query}
		""".format(
			base_dates_query=base_dates_query, condition_query=condition_query
		),
		{
			"employee": employee,
			"start_date": start_date,
			"end_date": end_date,
			"holiday_list": holiday_list,
		},
		as_list=True,
	)

	return [getdate(date[0]) for date in dates]
