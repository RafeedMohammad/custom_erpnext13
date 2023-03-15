frappe.listview_settings['Shift Type'] = {	
	onload: function(list_view) {
            let me = this;
            const months = moment.months();
            list_view.page.add_inner_button(__("Mark Attendance"), function() {
                let dialog = new frappe.ui.Dialog({
                    title: __("Mark Attendance"),
                    fields: [{
                            "fieldname":"from_date",
                            "label": __("From Date"),
                            "fieldtype": "Date",
                            "default": frappe.datetime.get_today(),
                            "reqd": 1,
                            "width": "100px"
                        
                    },
                    {
                        "fieldname":"to_date",
                        "label": __("To Date"),
                        "fieldtype": "Date",
                        "default": frappe.datetime.get_today(),
                        "reqd": 1,
                        "width": "100px"
                    
                }
                    
                    ],
                primary_action(data) {
                    frappe.call({
                        method: 'custom_erpnext.shift_type.process_auto_attendance_for_all_shifts',
                        args: {
                            from_date: data.from_date,
                            to_date: data.to_date
                        },
                        freeze: true,

                        callback: () => {
                            frappe.msgprint(__('Attendance has been marked as per employee check-ins'));
                        }
                
                        
                    });
                    
                    dialog.hide();
					list_view.refresh();    
                },
                    primary_action_label: __('Mark Attendance')
    
                });
                dialog.show();
            });
        
    }
};
// list_view.page.add_inner_button(__("Mark Attendance"), function() {
//     frappe.call({
//         method: 'custom_erpnext.shift_type.process_auto_attendance_for_all_shifts'

        
//     });
// })
