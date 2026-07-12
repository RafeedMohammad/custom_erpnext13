# Copyright (c) 2026, LTL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class EmployeeIncomeSummary(Document):
    def validate(self):
        """
        Main controller: runs whenever the document is saved.
        """
        if self.employee and self.from_date and self.to_date:
            self.fetch_income_details()

    def fetch_income_details(self):
        """
        Logic migrated from your SQL report to populate DocType fields.
        """
        # 1. Fetch Employee metadata (Designation, TIN)
        emp_info = frappe.db.get_value("Employee", self.employee, ["designation"], as_dict=1)
        if emp_info:
            self.designation = emp_info.designation
            # self.e_tin = emp_info.tax_id

        # 2. Execute the aggregation query based on the selected period
        # Note: We match the Salary Slip components based on your report logic
        income_data = frappe.db.sql("""
            SELECT 
                SUM(CASE WHEN sd.salary_component = 'Basic' THEN sd.amount ELSE 0 END) AS basic,
                SUM(CASE WHEN sd.salary_component = 'Medical' THEN sd.amount ELSE 0 END) AS medical,
                SUM(CASE WHEN sd.salary_component = 'Hrent' THEN sd.amount ELSE 0 END) AS hrent,
                SUM(CASE WHEN sd.salary_component IN ('Lunch', 'Conv','LunchTrAllow','Night Allow.') THEN sd.amount ELSE 0 END) AS conv,
                -- Getting the latest basic to calculate festival bonus (as per your report logic)
                MAX(CASE WHEN sd.salary_component = 'Basic' THEN sd.amount ELSE 0 END) AS latest_basic,
                SUM(CASE WHEN sd.salary_component ='PF' THEN sd.amount ELSE 0 END) AS pf

            FROM `tabSalary Slip` ss
            INNER JOIN `tabSalary Detail` sd ON ss.name = sd.parent
            WHERE ss.employee = %s 
                AND ss.start_date >= %s 
                AND ss.end_date <= %s
        """, (self.employee, self.from_date, self.to_date), as_dict=1)

        if income_data and income_data[0]:
            res = income_data[0]
            
            # Mapping SQL results to DocType field names
            self.total_basic = flt(res.basic)
            self.total_medical = flt(res.medical)
            self.total_hrent = flt(res.hrent)
            self.total_conveyance = flt(res.conv)
            
            # Calculation: Festival Bonus = 2 * Latest Basic (from your report logic)
            self.festival_bonus = flt(res.latest_basic) * 2
            self.total_pf=flt(res.pf)

            # Calculate Gross
            self.gross_income = round(
                self.total_basic + 
                self.total_medical + 
                self.total_hrent + 
                self.total_conveyance + 
                self.festival_bonus +
                self.earn_leave_allowance +
                self.total_pf
            ,0)
        else:
            frappe.msgprint(_("No submitted Salary Slips found for the selected period."))


from frappe import _

@frappe.whitelist()
def create_bulk_income_statements(employees, income_year, assessment_year):
    # Split MultiSelect string into a list
    if isinstance(employees, str):
        employee_list = [e.strip() for e in employees.split(',') if e.strip()]
    else:
        employee_list = employees

    created_count = 0
    
    for emp in employee_list:
        # Avoid creating duplicates for the same employee and year
        if not frappe.db.exists("Employee Income Summary", {"employee": emp, "income_year": income_year}):
            doc = frappe.get_doc({
                "doctype": "Employee Income Summary",
                "employee": emp,
                "income_year": income_year,
                "assessment_year": assessment_year,
                "docstatus": 0 # Draft
            })
            doc.insert()
            created_count += 1
            
    return created_count