# Copyright (c) 2025, Lithe-Tech Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date, flt, get_datetime, getdate, time_diff_in_hours


class DailyActivityLog(Document):
	def validate(self):
		for d in self.get("work_detail"):

			self.total_daily_wages += flt(d.job_price)*flt(d.quantity)
