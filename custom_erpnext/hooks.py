from . import __version__ as app_version

app_name = "custom_erpnext"
app_title = "Custom Erpnext"
app_publisher = "Lithe-Tech Limited"
app_description = "Customized ERPNext"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "rafeed.cse@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/custom_erpnext/css/custom_erpnext.css"
# app_include_js = "/assets/custom_erpnext/js/custom_erpnext.js"

# include js, css files in header of web template
# web_include_css = "/assets/custom_erpnext/css/custom_erpnext.css"
# web_include_js = "/assets/custom_erpnext/js/custom_erpnext.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "custom_erpnext/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
doctype_list_js = {"Shift Type" : "public/js/shift_type_list.js"}
doctype_js = {"Payroll Entry" : "public/js/payroll_entry.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "custom_erpnext.install.before_install"
# after_install = "custom_erpnext.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "custom_erpnext.uninstall.before_uninstall"
# after_uninstall = "custom_erpnext.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "custom_erpnext.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo",

    "Shift Type": "custom_erpnext.shift_type.override_ShiftType",
    "Attendance": "custom_erpnext.attendance.override_Attendance",
    "Employee Checkin": "custom_erpnext.employee_checkin.override_EmployeeCheckin",
	"Shift Assignment": "custom_erpnext.shift_assignment.override_ShiftAssignment",
	"Salary Slip": "custom_erpnext.salary_slip.override_SalarySlip",
	"Payroll Entry":"custom_erpnext.payroll_entry.PayrollEntry",
    "Loan Repayment":"custom_erpnext.loan_repayment.override_LoanRepayment",
    "Loan" : "custom_erpnext.loan.Loan",
    "Department" : "custom_erpnext.department.Department",
    "Leave Policy Assignment": "custom_erpnext.leave_policy_assignment.override_LeavePolicyAssignment"
	#"Asset": "custom_erpnext.asset.override_Asset",
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"custom_erpnext.tasks.all"
#	],
#	"daily": [
#		"custom_erpnext.tasks.daily"
#	],
#	"hourly": [
#		"custom_erpnext.tasks.hourly"
#	],
#	"weekly": [
#		"custom_erpnext.tasks.weekly"
#	]
#	"monthly": [
#		"custom_erpnext.tasks.monthly"
#	]
# }
scheduler_events = {
    "Daily Long": [
        "custom_erpnext.custom_erpnext.doctype.Customized_earned_leave.allocate_earned_leaves"
	]
}
# Testing
# -------

# before_tests = "custom_erpnext.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "custom_erpnext.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "custom_erpnext.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"custom_erpnext.auth.validate"
# ]

