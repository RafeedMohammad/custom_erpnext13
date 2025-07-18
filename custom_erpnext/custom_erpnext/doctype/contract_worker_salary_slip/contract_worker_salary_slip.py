# Copyright (c) 2025, Lithe-Tech Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
from frappe.model.document import Document

class ContractWorkerSalarySlip(Document):
    def validate(self):
        self.get_production_data()
        self.calculate_total_amount()
        
    def get_production_data(self):
        if not self.employee or not self.from_date or not self.to_date:
            frappe.throw(_("Please set Employee, From Date and To Date before calculating."))

        # Clear existing rows
        self.set("activities", [])

        # Fetch and aggregate production data
        data = frappe.db.sql("""
            SELECT
                dpd.process_name,
                dpd.rate,
                SUM(dpd.quantity) AS quantity,
                dp.production_date,
                dp.buyer
            FROM
                `tabDaily Production Details` dpd
            JOIN
                `tabDaily Production` dp ON dp.name = dpd.parent
            WHERE
                dp.employee = %s
                AND dp.production_date BETWEEN %s AND %s
            GROUP BY
                dpd.process_name, dpd.rate
        """, (self.employee, self.from_date, self.to_date), as_dict=True)

        for row in data:
            if row.quantity!=0:
                  self.append("activities", {
					"process_name": row.process_name,
					"rate": row.rate,
					"quantity": row.quantity,
					"buyer": row.buyer,
					"production_date": row.production_date,
				})
    def calculate_total_amount(self):
        total = 0
        for row in self.activities:
            row.amount = row.rate * row.quantity
            total += row.amount
        self.total_amount = total

		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		#self.calculate_salary_data()

	# def calculate_salary_data(self):
	# 	self.activities = []
	# 	total_amount = 0

	# 	if not (self.employee and self.from_date and self.to_date):
	# 		return

	# 	activity_logs = frappe.db.sql("""
	# 		SELECT d.activity_type, SUM(d.quantity) AS total_pieces
	# 		FROM `tabDaily Activity Log` p
	# 		JOIN `tabDaily Job Detail` d ON d.parent = p.name
	# 		WHERE p.employee = %s AND p.posting_date BETWEEN %s AND %s
	# 		GROUP BY d.activity_type
	# 	""", (self.employee, self.from_date, self.to_date), as_dict=True)

	# 	for row in activity_logs:
	# 		rate = frappe.db.get_value("Activity Type", row.activity_type, "billing_rate") or 0
	# 		amount = flt(row.total_pieces) * flt(rate)

	# 		self.append("activities", {
	# 			"activity_type": row.activity_type,
	# 			"pieces_done": row.total_pieces,
	# 			"rate_per_piece": rate,
	# 			"amount": amount
	# 		})

	# 		total_amount += amount

	# 	self.total_amount = total_amount


	# def calculate_salary_data(self):
	# 	self.activities = []
	# 	total_amount = 0

	# 	if not (self.employee and self.from_date and self.to_date):
	# 		return

	# 	activity_logs = frappe.db.sql("""
	# 		SELECT 
	# 			at.name AS activity_type,
	# 			COALESCE(SUM(djd.quantity), 0) AS total_pieces,
	# 			at.billing_rate
	# 		FROM `tabActivity Type` at
	# 		LEFT JOIN `tabDaily Job Detail` djd ON djd.activity_type = at.name
	# 		LEFT JOIN `tabDaily Activity Log` dal ON dal.name = djd.parent
	# 			AND dal.employee = %s
	# 			AND dal.posting_date BETWEEN %s AND %s
	# 		GROUP BY at.name, at.billing_rate
	# 	""", (self.employee, self.from_date, self.to_date), as_dict=True)

	# 	for row in activity_logs:
	# 		rate = row.billing_rate or 0
	# 		amount = flt(row.total_pieces) * flt(rate)

	# 		self.append("activities", {
	# 			"activity_type": row.activity_type,
	# 			"pieces_done": row.total_pieces,
	# 			"rate_per_piece": rate,
	# 			"amount": amount
	# 		})

	# 		total_amount += amount

	# 	self.total_amount = total_amount
