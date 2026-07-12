frappe.listview_settings['Employee Income Summary'] = {
    onload: function(listview) {
        listview.page.add_inner_button(__('Bulk Entry'), function() {
            let d = new frappe.ui.Dialog({
                title: __('Bulk Income Statement Entry'),
                fields: [
                    {
                        label: __('Employees'),
                        fieldname: 'employees',
                        fieldtype: 'MultiSelect',
                        get_query: () => {
                            return {
                                filters: { status: 'Active' }
                            };
                        },
                        reqd: 1
                    },
                    {
                        label: __('Income Year'),
                        fieldname: 'income_year',
                        fieldtype: 'Link',
                        options: 'Fiscal Year',
                        reqd: 1
                    },
                    {
                        label: __('Assessment Year'),
                        fieldname: 'assessment_year',
                        fieldtype: 'Data',
                        reqd: 1
                    }
                ],
                primary_action_label: __('Create Statements'),
                primary_action(values) {
                    d.get_primary_btn().attr('disabled', true);
                    
                    frappe.call({
                        method: "custom_erpnext.employee_income_summary.api.create_bulk_income_statements",
                        args: {
                            employees: values.employees,
                            income_year: values.income_year,
                            assessment_year: values.assessment_year
                        },
                        callback: function(r) {
                            if (r.message !== undefined) {
                                frappe.msgprint(__('{0} statements created successfully', [r.message]));
                                d.hide();
                                listview.refresh();
                            }
                        },
                        always: function() {
                            d.get_primary_btn().attr('disabled', false);
                        }
                    });
                }
            });
            d.show();
        });
    }
};