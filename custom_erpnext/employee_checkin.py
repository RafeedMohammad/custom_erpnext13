# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from math import ceil, floor
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, get_datetime, get_link_to_form
from erpnext.hr.doctype.employee_checkin.employee_checkin import EmployeeCheckin

from erpnext.hr.doctype.holiday_list.holiday_list import is_holiday
# from erpnext.hr.doctype.shift_assignment.shift_assignment import (
# 	get_actual_start_end_datetime_of_shift,
# )
from custom_erpnext.shift_assignment import (
	get_actual_start_end_datetime_of_shift,
)
from erpnext.hr.utils import validate_active_employee



from datetime import datetime,timedelta

class override_EmployeeCheckin(Document):
	
	def validate(self):
		if self.card_no: #added card no if there is only card number with out any employee info. this fuction will fetch employee data in the field.
			self.employee,self.employee_name = frappe.db.get_value("Employee",{"attendance_device_id":self.card_no},('name','employee_name'))
		validate_active_employee(self.employee)
		self.validate_duplicate_log()
		self.fetch_shift()
		get_employee_for_zk()

	def validate_duplicate_log(self):
		doc = frappe.db.exists(
			"Employee Checkin", {"employee": self.employee, "time": self.time, "name": ["!=", self.name]}
		)
		if doc:
			doc_link = frappe.get_desk_link("Employee Checkin", doc)
			frappe.throw(
				_("This employee already has a log with the same timestamp.{0}").format("<Br>" + doc_link)
			)

	def fetch_shift(self):
		shift_actual_timings = get_actual_start_end_datetime_of_shift(
			self.employee, get_datetime(self.time), True
		)
		if shift_actual_timings[0] and shift_actual_timings[1]:
			if (
				shift_actual_timings[2].shift_type.determine_check_in_and_check_out
				== "Strictly based on Log Type in Employee Checkin"
				and not self.log_type
				and not self.skip_auto_attendance
			):
				frappe.throw(
					_("Log Type is required for check-ins falling in the shift: {0}.").format(
						shift_actual_timings[2].shift_type.name
					)
				)
			if not self.attendance:
				self.shift = shift_actual_timings[2].shift_type.name
				self.shift_actual_start = shift_actual_timings[0]
				self.shift_actual_end = shift_actual_timings[1]
				self.shift_start = shift_actual_timings[2].start_datetime
				self.shift_end = shift_actual_timings[2].end_datetime
		else:
			self.shift = None
	


@frappe.whitelist()
def add_log_based_on_employee_field(
	employee_field_value,
	timestamp,
	device_id=None,
	log_type=None,
	skip_auto_attendance=0,
	employee_fieldname="attendance_device_id",
):
	"""Finds the relevant Employee using the employee field value and creates a Employee Checkin.

	:param employee_field_value: The value to look for in employee field.
	:param timestamp: The timestamp of the Log. Currently expected in the following format as string: '2019-05-08 10:48:08.000000'
	:param device_id: (optional)Location / Device ID. A short string is expected.
	:param log_type: (optional)Direction of the Punch if available (IN/OUT).
	:param skip_auto_attendance: (optional)Skip auto attendance field will be set for this log(0/1).
	:param employee_fieldname: (Default: attendance_device_id)Name of the field in Employee DocType based on which employee lookup will happen.
	"""

	if not employee_field_value or not timestamp:
		frappe.throw(_("'employee_field_value' and 'timestamp' are required."))

	employee = frappe.db.get_values(
		"Employee",
		{employee_fieldname: employee_field_value},
		["name", "employee_name", employee_fieldname],
		as_dict=True,
	)
	if employee:
		employee = employee[0]
	else:
		frappe.throw(
			_("No Employee found for the given employee field value. '{}': {}").format(
				employee_fieldname, employee_field_value
			)
		)

	doc = frappe.new_doc("Employee Checkin")
	doc.employee = employee.name
	doc.employee_name = employee.employee_name
	doc.time = timestamp
	doc.device_id = device_id
	doc.log_type = log_type
	if cint(skip_auto_attendance) == 1:
		doc.skip_auto_attendance = "0"
	doc.insert()

	return doc


def mark_attendance_and_link_log(
	logs,
	attendance_status,
	attendance_date,
	working_hours=None,
	late_entry=False,
	early_exit=False,
	in_time=None,
	out_time=None,
	shift=None,
	late_entry_duration=None,
	overtime=None,
	rounding_ot=None
	
):
	#frappe.publish_realtime('msgprint', 'Starting mark_attendance of '+logs[0].employee+" for "+str(attendance_date))
	#mark_attendance_start=datetime.now()
	"""Creates an attendance and links the attendance to the Employee Checkin.
	Note: If attendance is already present for the given date, the logs are marked as skipped and no exception is thrown.

	:param logs: The List of 'Employee Checkin'.
	:param attendance_status: Attendance status to be marked. One of: (Present, Absent, Half Day, Skip). Note: 'On Leave' is not supported by this function.
	:param attendance_date: Date of the attendance to be created.
	:param working_hours: (optional)Number of working hours for the given date.
	"""
	log_names = [x.name for x in logs]
	employee = logs[0].employee
	company = frappe.get_cached_value("Employee", employee, "company")

	allowed_for_overtime = frappe.get_cached_value("Employee", employee, "ot_enable")

	shift_start = logs[0].shift_start
	shift_end = logs[0].shift_end

	#allowed_for_late = frappe.get_cached_value("Employee", employee, "late_allow")

	# if allowed_for_late=="Y" and attendance_status=="Late":
	# 	late_entry_duration=0
	# 	attendance_status="Present"

	# if attendance_status in ("Weekly Off", "Holiday"):
	# 	overtime_hour=working_hours
	overtime_hour = 0

	if allowed_for_overtime=="No":
		overtime=0
	
	else:
		#overtime_hour=rounding_ot
		overtime_hour_fraction  = ((overtime.total_seconds())%3600)//60
		if rounding_ot<0:
		#for the company which has ot_rules as Queen South
			if overtime_hour_fraction >= abs(rounding_ot):			
				overtime_hour = (overtime.total_seconds()//3600)+.5
				overtime=overtime-timedelta(minutes=overtime_hour_fraction//30)
			else:			
				overtime_hour = (overtime.total_seconds()//3600)
				overtime=overtime-timedelta(minutes=overtime_hour_fraction//30)
		else:
			if overtime_hour_fraction >= rounding_ot:			
				overtime_hour = (overtime.total_seconds()//3600)+1
			else:		
				overtime_hour = (overtime.total_seconds()//3600)





	
	if attendance_status == "Skip":
		skip_attendance_in_checkins(log_names)
		return None

	elif attendance_status in ("Present", "Absent", "Half Day", "Weekly Off", "Holiday", "Late"):
		company = frappe.get_cached_value("Employee", employee, "company")
		#frappe.publish_realtime('msgprint', 'Starting duplicate check attendance of '+logs[0].employee+" for "+str(attendance_date)+' at-> '+str(datetime.now()))
		#duplicate_check_start=datetime.now()
		duplicate = frappe.db.exists(
			"Attendance",
			{"employee": employee, "attendance_date": attendance_date, "docstatus": ("!=", "2")},
		)
		#duplicate_check_end=datetime.now()
		#frappe.publish_realtime('msgprint', 'Ending duplicate check attendances o f '+logs[0].employee+" for "+str(attendance_date)+' at-> '+str(datetime.now()))
		#frappe.publish_realtime('msgprint','Duplicate check time= '+str(duplicate_check_end-duplicate_check_start))
		if not duplicate:
			#frappe.publish_realtime('msgprint', 'Starting insertion attendance of '+logs[0].employee+" for "+str(attendance_date)+' at-> '+str(datetime.now()))
			#insert_start=datetime.now()
			doc_dict = {
				"doctype": "Attendance",
				"employee": employee,
				"attendance_date": attendance_date,
				"status": attendance_status,
				"working_hours": working_hours,
				"company": company,
				"shift": shift,
				"late_entry": late_entry,
				"early_exit": early_exit,
				"in_time": in_time,
				"out_time": out_time,
				"rounded_ot": overtime_hour,
				"late_entry_duration":late_entry_duration,
				"shift_start": shift_start,
				"shift_end":shift_end,
				"overtime":overtime
			}
			attendance = frappe.get_doc(doc_dict).insert()
			attendance.submit()
			#frappe.publish_realtime('msgprint', 'Ending insertion attendance of '+logs[0].employee+" for "+str(attendance_date)+' at-> '+str(datetime.now()))
			if attendance_status == "Absent":
				attendance.add_comment(
					text=_("Employee was marked Absent for not meeting the working hours threshold.")
				)

			#-->Updated the Employee Checkin document for multi-attendance processing. The checkins which are given later, will be set with the attendance ID processed before
			# frappe.db.sql(
			# 	"""update `tabEmployee Checkin`
			# 	set attendance = %s
			# 	where name in %s""",
			# 	(attendance.name, log_names),
			# )
			#frappe.publish_realtime('msgprint', 'Ending mark_attendance of '+employee+" for "+str(attendance_date)+' at-> '+str(datetime.now()))
			#insert_end=datetime.now()
			# frappe.publish_realtime('msgprint', 'insertion time= '+str(insert_end-insert_start))
			# frappe.publish_realtime('msgprint', 'Mark Attendance time= '+str(insert_end-mark_attendance_start))


			return attendance
		else:
			#change_start
			#insert_start=datetime.now()  
			#frappe.publish_realtime('msgprint', 'Starting insertion attendance for duplicate '+logs[0].employee+" for "+str(attendance_date)+' at-> '+str(datetime.now()))		
			previous_attendance_name=frappe.db.get_value("Attendance",{"attendance_date":attendance_date,"employee":employee},'name')
			doc_dict = {
                "doctype": "Attendance",
                "employee": employee,
                "attendance_date": attendance_date,
                "status": attendance_status,
                "working_hours": working_hours,
                "company":company,
                "shift": shift,
                "late_entry": late_entry,
                "early_exit": early_exit,
                "in_time": in_time,
                "out_time": out_time,
				"rounded_ot":overtime_hour,
				"late_entry_duration":late_entry_duration,
				"shift_start": shift_start,
				"shift_end":shift_end,
				"overtime":overtime	
            }
			attendance=frappe.db.set_value('Attendance', previous_attendance_name, {'out_time': doc_dict['out_time'],'working_hours': doc_dict['working_hours'],
            'in_time': doc_dict['in_time'],'status': doc_dict['status'],'late_entry': doc_dict['late_entry'],'early_exit': doc_dict['early_exit'], 
			'rounded_ot': doc_dict['rounded_ot'],'late_entry_duration':doc_dict['late_entry_duration'], 'shift_start':doc_dict['shift_start'],
			'shift_end':doc_dict['shift_end'], 'shift':doc_dict['shift'], "overtime":doc_dict['overtime']}, update_modified=True)
			#Changed Code - End

			#Attendance document with updated values will be saved
			attendance = frappe.get_doc('Attendance',previous_attendance_name).save()

			#-->skip_attendance_in_checkins(log_names,previous_attendance_name)#added previous_attendance
			#skip_attendance_in_checkins(log_names)
			# if duplicate:
			# 	add_comment_in_checkins(log_names, duplicate)
			#frappe.publish_realtime('msgprint', 'Ending mark_attendance of '+employee+" for "+str(attendance_date)+' at-> '+str(datetime.now()))
			#insert_end=datetime.now()
			# frappe.publish_realtime('msgprint', 'insertion time= '+str(insert_end-insert_start))
			# frappe.publish_realtime('msgprint', 'Mark Attendance time= '+str(insert_end-mark_attendance_start))
			return None
	else:
		frappe.throw(_("{} is an invalid Attendance Status.").format(attendance_status))

def calculate_working_hours(logs, check_in_out_type, working_hours_calc_type):
	"""Given a set of logs in chronological order calculates the total working hours based on the parameters.
	Zero is returned for all invalid cases.

	:param logs: The List of 'Employee Checkin'.
	:param check_in_out_type: One of: 'Alternating entries as IN and OUT during the same shift', 'Strictly based on Log Type in Employee Checkin'
	:param working_hours_calc_type: One of: 'First Check-in and Last Check-out', 'Every Valid Check-in and Check-out'
	"""
	total_hours = 0
	in_time = out_time = None
	if check_in_out_type == "Alternating entries as IN and OUT during the same shift":
		in_time = logs[0].time
		if len(logs) >= 2:
			out_time = logs[-1].time
		if working_hours_calc_type == "First Check-in and Last Check-out":
			# assumption in this case: First log always taken as IN, Last log always taken as OUT
			total_hours = time_diff_in_hours(in_time, logs[-1].time)
		elif working_hours_calc_type == "Every Valid Check-in and Check-out":
			logs = logs[:]
			while len(logs) >= 2:
				total_hours += time_diff_in_hours(logs[0].time, logs[1].time)
				del logs[:2]

	elif check_in_out_type == "Strictly based on Log Type in Employee Checkin":
		if working_hours_calc_type == "First Check-in and Last Check-out":
			first_in_log_index = find_index_in_dict(logs, "log_type", "IN")
			first_in_log = (
				logs[first_in_log_index] if first_in_log_index or first_in_log_index == 0 else None
			)
			last_out_log_index = find_index_in_dict(reversed(logs), "log_type", "OUT")
			last_out_log = (
				logs[len(logs) - 1 - last_out_log_index]
				if last_out_log_index or last_out_log_index == 0
				else None
			)
			if first_in_log and last_out_log:
				in_time, out_time = first_in_log.time, last_out_log.time
				total_hours = time_diff_in_hours(in_time, out_time)
		elif working_hours_calc_type == "Every Valid Check-in and Check-out":
			in_log = out_log = None
			for log in logs:
				if in_log and out_log:
					if not in_time:
						in_time = in_log.time
					out_time = out_log.time
					total_hours += time_diff_in_hours(in_log.time, out_log.time)
					in_log = out_log = None
				if not in_log:
					in_log = log if log.log_type == "IN" else None
					if in_log and not in_time:
						in_time = in_log.time
				elif not out_log:
					out_log = log if log.log_type == "OUT" else None

			if in_log and out_log:
				out_time = out_log.time
				total_hours += time_diff_in_hours(in_log.time, out_log.time)

	return total_hours, in_time, out_time

def time_diff_in_hours(start, end):
	return round((end - start).total_seconds() / 3600, 1)


def find_index_in_dict(dict_list, key, value):
	return next((index for (index, d) in enumerate(dict_list) if d[key] == value), None)


def add_comment_in_checkins(log_names, duplicate):
	text = _("Auto Attendance skipped due to duplicate attendance record: {}").format(
		get_link_to_form("Attendance", duplicate)
	)

	for name in log_names:
		frappe.get_doc(
			{
				"doctype": "Comment",
				"comment_type": "Comment",
				"reference_doctype": "Employee Checkin",
				"reference_name": name,
				"content": text,
			}
		).insert(ignore_permissions=True)


def skip_attendance_in_checkins(log_names, attendance):
	EmployeeCheckin = frappe.qb.DocType("Employee Checkin")
	(
		frappe.qb.update(EmployeeCheckin)
		#.set("skip_auto_attendance", 1) #commented 
		.set("attendance",attendance) #added
		.where(EmployeeCheckin.name.isin(log_names))
	).run()


@frappe.whitelist()
def get_employee_for_zk(department=None):#custom code for pull data from employee to device"
	
	max_user_id=frappe.db.sql("""select max(attendance_device_id) from tabEmployee""") or 0
	if max_user_id[0][0] is None:
		max_user_id=('0')
	employee=frappe.db.get_list('Employee',
    filters={
        "status":"Active",
		"Department":department,
		"employee_card_number": ["is", "set"],
		"attendance_device_id": ["is", "not set"]
    },
    fields=["name", "employee_name", "attendance_device_id","employee_card_number"],
	as_list=1
	)
	for i in range(0,len(employee)):
		frappe.db.set_value('Employee', employee[i][0], 'attendance_device_id',int(max_user_id[0][0])+i+1)
	return employee
