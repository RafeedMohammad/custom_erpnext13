// Copyright (c) 2025, Lithe-Tech Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Contract Worker Salary Slip', {
	onload: function(frm) {
        frm.set_query('employee', function() {
            return {
                filters: {
                    employment_type: ['in', ['Contract', 'Part-time']]
                }
            };
        });
    },
});
