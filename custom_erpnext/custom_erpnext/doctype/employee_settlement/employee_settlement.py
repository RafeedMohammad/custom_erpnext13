# Copyright (c) 2025, Lithe-Tech Limited and contributors
# For license information, please see license.txt

import frappe

from frappe.model.document import Document
from dateutil.relativedelta import relativedelta

class EmployeeSettlement(Document):
    def validate(self):
        self.calculate_length_of_service()
        self.get_attendance_details()
        self.get_salary_dateils()
        self.payment_entitled()
        self.get_sub_total_payments()
        self.get_adjustemnt_details()
        self.get_net_payments()
    
    def calculate_length_of_service(self):
        if self.last_date and self.date_of_joining:
            diff = relativedelta(self.last_date, self.date_of_joining)
            self.length_of_service = f"{diff.years} year(s) {diff.months} month(s)"

    def get_attendance_details(self):
        from_date=self.last_date.replace(day=1)
        attendance_records = frappe.get_all(
        "Attendance",
        filters={
            "employee": self.employee,
            "attendance_date": ["between", [from_date, self.last_date]],
            "docstatus": 1  # Only submitted records
        },
        fields=["status","rounded_ot", "is_night", "in_time","leave_type"]
        )

        self.present_days = sum(1 for record in attendance_records if record.status in ("Present","Late"))
        self.absent_days = sum(1 for record in attendance_records if record.status == "Absent")
        self.leave_days = sum(1 for record in attendance_records if record.status == "On Leave")
        self.leave_without_pay_days = sum(1 for record in attendance_records if record.status == "On Leave" and record.leave_type in("OL","Leave Without Pay"))

        self.night_days = sum(
        1 for record in attendance_records
        if record.status in ("Present","Late") and record.is_night == "Yes" and record.in_time
        )
        self.overtime = sum(record.rounded_ot or 0 for record in attendance_records)+2

    def get_salary_dateils(self):
        salary_detail = frappe.get_all(
            "Salary Structure Assignment",
            filters={
                "employee": self.employee,
                "docstatus": 1
            },
            fields=["base", "salary_structure", "from_date"],  # fieldname -> fields
            order_by="from_date desc",
            limit=1
        )

        if salary_detail:
            salary_structure = salary_detail[0].salary_structure
            self.gross_salary = salary_detail[0].base or 0

            # Now correctly fetching medical allowance
            self.medical_allowance = frappe.db.get_value(
                "Salary Detail",
                {
                    "salary_component": "Default Medical",
                    "parent": salary_structure,
                },
                "amount"
            ) or 0

            # Calculate basic and house rent
            self.basic = round((self.gross_salary - self.medical_allowance) * (2 / 3),0)
            self.house_rent = round((self.gross_salary - self.medical_allowance) * (1 / 3),0)
            
            # Calculate overtime rate
            self.overtime_rate = round(self.basic / 104,2)

    
    def payment_entitled(self):
        self.wagessalary_pay_period_total_days=self.last_date.day
        self.wagessalary_pay_period_total_days_payment=self.wagessalary_pay_period_total_days*(self.gross_salary/30)
        self.overtime_payment=self.overtime*self.overtime_rate
        self.leave_el_total_payment=self.leave_el_total_days*(self.gross_salary/30)
        self.p_f_fund=get_total_pf(self.employee)
                
        self.total_per_year_compensation_amount=self.total_years_for_per_year_compensation*self.basic

        self.lunch_amount=self.present_days*self.lunch_rate
        self.travel_amount=self.present_days*self.travel_rate
        self.night_amount=self.night_days*self.night_rate
        self.sub_total_payment_entitled=self.wagessalary_pay_period_total_days_payment+self.overtime_payment+self.leave_el_total_payment+self.p_f_fund+self.arrear+self.total_per_year_compensation_amount+self.lunch_amount+self.travel_amount+self.night_amount

    def get_sub_total_payments(self):
        self.total_notice_pay=self.number_of_basic_for_notice_pay_120_day_pay*self.basic
        self.total_service_benefit_pay=self.number_of_basic_for_service_benefit*self.basic
        self.gross_total_payment_entitiled=self.sub_total_payment_entitled+self.total_notice_pay+self.total_service_benefit_pay

    def get_adjustemnt_details(self):
        self.lay_off_amount=((self.basic/30)/2)*self.total_days_for_lay_off
        self.amount_for_friday_100_basic_and_medical_allowance=((self.basic+self.medical_allowance)/30)*self.total_days_for_friday
        self.medical_allow_amount=(self.medical_allowance/30)*self.total_days_for_medical_allow
        self.absentwithout_pay_leave_days=self.absent_days+self.leave_without_pay_days
        self.absentwithout_pay_leave_amount=(self.absent_days+self.leave_without_pay_days)*(self.basic/30)
        self.amount_for_instant_resign=self.total_basic_for_instant_resign*self.basic
        self.total_adjustment=round(self.lay_off_amount+self.medical_allow_amount+self.absentwithout_pay_leave_amount+self.amount_for_instant_resign+self.amount_for_friday_100_basic_and_medical_allowance,0)

    def get_net_payments(self):
        self.net_payment_entitled=round(self.gross_total_payment_entitiled-self.total_adjustment,0)
        self.balance_money_paid_by_cash=round(self.net_payment_entitled-self.less_provident_found_by_cheque,0)


def get_total_pf(employee):
    result = frappe.db.sql("""
        SELECT (emp.pf_default_amount + IFNULL(SUM(sd.amount), 0))
        FROM `tabSalary Slip` ss
        JOIN `tabSalary Detail` sd ON sd.parent = ss.name
        JOIN `tabEmployee` emp ON ss.employee = emp.name
        WHERE ss.employee = %s
        AND sd.salary_component = 'PF'
        AND sd.parenttype = 'Salary Slip'
        AND ss.docstatus = 1
        GROUP BY emp.name
    """, (employee,), as_list=True)

    total_pf = result[0][0] if result and result[0][0] is not None else 120
    return total_pf