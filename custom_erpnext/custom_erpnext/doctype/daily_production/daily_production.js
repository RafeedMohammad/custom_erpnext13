frappe.ui.form.on('Daily Production', {
    buyer: function(frm) {
        // Filter the order field based on buyer
        frm.set_query('order', () => {
            return {
                filters: {
                    buyer: frm.doc.buyer
                }
            };
        });

        // Optional: clear order and order_items when buyer changes
        frm.set_value('order', null);
        frm.clear_table('order_items');
        frm.refresh_field('order_items');
    },

    order: function(frm) {
        if (frm.doc.order) {
            // Fetch the selected Order List document
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Order List",
                    name: frm.doc.order
                },
                callback: function(r) {
                    if (r.message) {
                        let order = r.message;
                        frm.clear_table('daily_production_details');

                        // Copy each row from order_details to order_items
                        (order.order_details || []).forEach((item) => {
                            let row = frm.add_child('daily_production_details');
                            row.process_name = item.process_name;
                            row.rate = item.rate;
                            row.employee= item.employee;
                            row.department= item.department;
                        });

                        frm.refresh_field('daily_production_details');
                    }
                }
            });
        }
    }
});
