# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _
from frappe.desk.form import assign_to
from frappe.model.document import Document
from frappe.utils import (
	add_days,
	cstr,
	flt,
	format_datetime,
	formatdate,
	get_datetime,
	get_link_to_form,
	get_number_format_info,
	getdate,
	nowdate,
	today,
	unique,
)

import erpnext
from erpnext.hr.doctype.employee.employee import (
	InactiveEmployeeStatusError,
	get_holiday_list_for_employee,
)


class DuplicateDeclarationError(frappe.ValidationError):
	pass


class a(Document):
	"""
	Create the project and the task for the boarding process
	Assign to the concerned person and roles as per the onboarding/separation template
	"""

	def validate(self):
		validate_active_employee(self.employee)
		# remove the task if linked before submitting the form
		if self.amended_from:
			for activity in self.activities:
				activity.task = ""

	def on_submit(self):
		# create the project for the given employee onboarding
		project_name = _(self.doctype) + " : "
		if self.doctype == "Employee Onboarding":
			project_name += self.job_applicant
		else:
			project_name += self.employee

		project = frappe.get_doc(
			{
				"doctype": "Project",
				"project_name": project_name,
				"expected_start_date": self.date_of_joining
				if self.doctype == "Employee Onboarding"
				else self.resignation_letter_date,
				"department": self.department,
				"company": self.company,
			}
		).insert(ignore_permissions=True, ignore_mandatory=True)

		self.db_set("project", project.name)
		self.db_set("boarding_status", "Pending")
		self.reload()
		self.create_task_and_notify_user()

	def create_task_and_notify_user(self):
		# create the task for the given project and assign to the concerned person
		for activity in self.activities:
			if activity.task:
				continue

			task = frappe.get_doc(
				{
					"doctype": "Task",
					"project": self.project,
					"subject": activity.activity_name + " : " + self.employee_name,
					"description": activity.description,
					"department": self.department,
					"company": self.company,
					"task_weight": activity.task_weight,
				}
			).insert(ignore_permissions=True)
			activity.db_set("task", task.name)

			users = [activity.user] if activity.user else []
			if activity.role:
				user_list = frappe.db.sql_list(
					"""
					SELECT
						DISTINCT(has_role.parent)
					FROM
						`tabHas Role` has_role
							LEFT JOIN `tabUser` user
								ON has_role.parent = user.name
					WHERE
						has_role.parenttype = 'User'
							AND user.enabled = 1
							AND has_role.role = %s
				""",
					activity.role,
				)
				users = unique(users + user_list)

				if "Administrator" in users:
					users.remove("Administrator")

			# assign the task the users
			if users:
				self.assign_task_to_users(task, users)

	def assign_task_to_users(self, task, users):
		for user in users:
			args = {
				"assign_to": [user],
				"doctype": task.doctype,
				"name": task.name,
				"description": task.description or task.subject,
				"notify": self.notify_users_by_email,
			}
			assign_to.add(args)

	def on_cancel(self):
		# delete task project
		for task in frappe.get_all("Task", filters={"project": self.project}):
			frappe.delete_doc("Task", task.name, force=1)
		frappe.delete_doc("Project", self.project, force=1)
		self.db_set("project", "")
		for activity in self.activities:
			activity.db_set("task", "")
def generate_leave_encashment():
	"""Generates a draft leave encashment on allocation expiry"""
	from erpnext.hr.doctype.leave_encashment.leave_encashment import create_leave_encashment

	if frappe.db.get_single_value("HR Settings", "auto_leave_encashment"):
		leave_type = frappe.get_all("Leave Type", filters={"allow_encashment": 1}, fields=["name"])
		leave_type = [l["name"] for l in leave_type]

		leave_allocation = frappe.get_all(
			"Leave Allocation",
			filters={"to_date": add_days(today(), -1), "leave_type": ("in", leave_type)},
			fields=[
				"employee",
				"leave_period",
				"leave_type",
				"to_date",
				"total_leaves_allocated",
				"new_leaves_allocated",
			],
		)

		create_leave_encashment(leave_allocation=leave_allocation)


def allocate_earned_leaves():
	"""Allocate earned leaves to Employees"""
	e_leave_types = get_earned_leaves()
	today = frappe.flags.current_date or getdate()

	for e_leave_type in e_leave_types:

		leave_allocations = get_leave_allocations(today, e_leave_type.name)

		for allocation in leave_allocations:

			if not allocation.leave_policy_assignment and not allocation.leave_policy:
				continue

			leave_policy = (
				allocation.leave_policy
				if allocation.leave_policy
				else frappe.db.get_value(
					"Leave Policy Assignment", allocation.leave_policy_assignment, ["leave_policy"]
				)
			)

			annual_allocation = frappe.db.get_value(
				"Leave Policy Detail",
				filters={"parent": leave_policy, "leave_type": e_leave_type.name},
				fieldname=["annual_allocation"],
			)

			from_date = allocation.from_date

			if e_leave_type.based_on_date_of_joining:
				from_date = frappe.db.get_value("Employee", allocation.employee, "date_of_joining")

			if check_effective_date(
				allocation.employee, from_date, today, e_leave_type.earned_leave_frequency, e_leave_type.based_on_date_of_joining
			):
				update_previous_leave_allocation(allocation.employee, from_date, today, allocation, annual_allocation, e_leave_type)


def update_previous_leave_allocation(employee_name, from_date, to_date, allocation, annual_allocation, e_leave_type):
	import calendar

	from_date = get_datetime(from_date)
	to_date = get_datetime(to_date)

	allocation = frappe.get_doc("Leave Allocation", allocation.name)
	annual_allocation = flt(annual_allocation, allocation.precision("total_leaves_allocated"))

	earned_leaves = get_monthly_earned_leave(
		employee_name, from_date, to_date, annual_allocation, e_leave_type.earned_leave_frequency, e_leave_type.rounding
	)

	earned_leaves = earned_leaves - allocation.total_leaves_allocated

	new_allocation = flt(allocation.total_leaves_allocated) + flt(earned_leaves)
	new_allocation_without_cf = flt(
		flt(allocation.get_existing_leave_count()) + flt(earned_leaves),
		allocation.precision("total_leaves_allocated"),
	)

	if new_allocation > e_leave_type.max_leaves_allowed and e_leave_type.max_leaves_allowed > 0:
		new_allocation = e_leave_type.max_leaves_allowed

	if (
		new_allocation != allocation.total_leaves_allocated
		# annual allocation as per policy should not be exceeded
		and new_allocation_without_cf <= annual_allocation
	):
		today_date = frappe.flags.current_date or getdate()

		allocation.db_set("total_leaves_allocated", new_allocation, update_modified=False)
		create_additional_leave_ledger_entry(allocation, earned_leaves, today_date)

		if e_leave_type.based_on_date_of_joining:
			text = _("allocated {0} leave(s) via scheduler on {1} based on the date of joining").format(
				frappe.bold(earned_leaves), frappe.bold(formatdate(today_date))
			)
		else:
			text = _("allocated {0} leave(s) via scheduler on {1}").format(
				frappe.bold(earned_leaves), frappe.bold(formatdate(today_date))
			)

		allocation.add_comment(comment_type="Info", text=text)


def get_monthly_earned_leave(employee_name, from_date, to_date, annual_leaves, frequency, rounding):
	total_working_days = frappe.db.sql("""select count(*) from `tabAttendance` where
									employee = '%s' and status in ('Present', 'Late')
									and attendance_date between '%s' and '%s'""" %(employee_name,from_date,to_date))
	
	earned_leaves = 0.0
	#divide_by_frequency = {"Yearly": 1, "Half-Yearly": 6, "Quarterly": 4, "Monthly": 12}
	#if annual_leaves:
		#earned_leaves = flt(annual_leaves) / divide_by_frequency[frequency]
		#if rounding:
			#if rounding == "0.25":
			#	earned_leaves = round(earned_leaves * 4) / 4
			#elif rounding == "0.5":
				#earned_leaves = round(earned_leaves * 2) / 2
			#	earned_leaves = round(total_working_days / 18)
			#else:
			#	earned_leaves = round(earned_leaves) 
	
	if rounding == "0.5":
		earned_leaves = round(total_working_days[0][0] / 18)


	return earned_leaves


def is_earned_leave_already_allocated(allocation, annual_allocation):
	from erpnext.hr.doctype.leave_policy_assignment.leave_policy_assignment import (
		get_leave_type_details,
	)

	leave_type_details = get_leave_type_details()
	date_of_joining = frappe.db.get_value("Employee", allocation.employee, "date_of_joining")

	assignment = frappe.get_doc("Leave Policy Assignment", allocation.leave_policy_assignment)
	leaves_for_passed_months = assignment.get_leaves_for_passed_months(
		allocation.leave_type, annual_allocation, leave_type_details, date_of_joining
	)

	# exclude carry-forwarded leaves while checking for leave allocation for passed months
	num_allocations = allocation.total_leaves_allocated
	if allocation.unused_leaves:
		num_allocations -= allocation.unused_leaves

	if num_allocations >= leaves_for_passed_months:
		return True
	return False


def get_leave_allocations(date, leave_type):
	return frappe.db.sql(
		"""select name, employee, from_date, to_date, leave_policy_assignment, leave_policy
		from `tabLeave Allocation`
		where
			%s between from_date and to_date and docstatus=1
			and leave_type=%s""",
		(date, leave_type),
		as_dict=1,
	)


def get_earned_leaves():
	return frappe.get_all(
		"Leave Type",
		fields=[
			"name",
			"max_leaves_allowed",
			"earned_leave_frequency",
			"rounding",
			"based_on_date_of_joining",
		],
		filters={"is_earned_leave": 1},
	)


def create_additional_leave_ledger_entry(allocation, leaves, date):
	"""Create leave ledger entry for leave types"""
	allocation.new_leaves_allocated = leaves
	allocation.from_date = date
	allocation.unused_leaves = 0
	allocation.create_leave_ledger_entry()


def check_effective_date(employee_name, from_date, to_date, frequency, based_on_date_of_joining):
	import calendar

	from dateutil import relativedelta

	from_date = get_datetime(from_date)
	to_date = get_datetime(to_date)
	rd = relativedelta.relativedelta(to_date, from_date)
	# last day of month
	last_day = calendar.monthrange(to_date.year, to_date.month)[1]

	total_working_days = frappe.db.sql("""select count(*) from `tabAttendance` where
									employee = '%s' and status in ('Present', 'Late')
									and attendance_date between '%s' and '%s'""" %(employee_name,from_date,to_date))
	if (from_date.day == to_date.day and based_on_date_of_joining) or (
		not based_on_date_of_joining and to_date.day == last_day) or(
		total_working_days[0][0]%18==0
	):
		if frequency == "Monthly":
			return True
		elif frequency == "Quarterly" and rd.months % 3:
			return True
		elif frequency == "Half-Yearly" and rd.months % 6:
			return True
		elif frequency == "Yearly" and rd.months % 12:
			return True
		elif frequency == "18_Days" and total_working_days[0][0] % 18 == 0:
			return True
		

	if frappe.flags.in_test:
		return True

	return False

