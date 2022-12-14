# Copyright (c) 2022, Lithe-Tech Limited and contributors
# For license information, please see license.txt

# import frappe


def execute(filters=None):
	if not filters:
		filters = {}
	#columns, data = [], []
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		_("S/L") + ":Data/:120",
		_("Item Name") + ":Link/Item:120",
		_("Brand") + ":Link/Item:120",
		_("Model") + ":Link/Item:120",
		_("Purchase Date") + ":Date/Asset:120",
		_("Asset Number") + ":Data/Attendance:120",
		_("Location") + ":Data/Attendance:120",
		_("Condition") + ":Data/:120",
		_("Remarks") + ":Data/:120",

	]


def get_data(filters):
	conditions, filters = get_conditions(filters)



def get_conditions(filters):
    conditions="" 
    if filters.get("from_date"): conditions += " att.attendance_date>= '%s'" % filters["from_date"]
    if filters.get("to_date"): conditions += " and att.attendance_date<= '%s'" % filters["to_date"]
    
    return conditions, filters



