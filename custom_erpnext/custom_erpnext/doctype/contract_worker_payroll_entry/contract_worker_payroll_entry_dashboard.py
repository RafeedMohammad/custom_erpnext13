def get_data():
	return {
		"fieldname": "contract_worker_payroll_entry",
		"non_standard_fieldnames": {
			"Journal Entry": "reference_name",
			# "Payment Entry": "reference_name",
		},
		"transactions": [{"items": ["Contract Worker Salary Slip"]}],
	}