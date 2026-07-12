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
                        reqd: 1,
                        // This allows the MultiSelect to search the Employee DocType
                        get_query: () => {
                            return {
                                query: "frappe.desk.search.search_link",
                                filters: { status: 'Active' }
                            };
                        }
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
            
            // Critical fix: Tell the MultiSelect field which DocType to link to
            d.fields_dict['employees'].get_query = function() {
                return {
                    filters: { 'status': 'Active' }
                };
            };
            d.fields_dict['employees'].set_data([]); // Initialize data
            
            // We set the options to 'Employee' so it knows what to search
            d.fields_dict['employees'].df.options = 'Employee';
            
            d.show();
        });
    }
};