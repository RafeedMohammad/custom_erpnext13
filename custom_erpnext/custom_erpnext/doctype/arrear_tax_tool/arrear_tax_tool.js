// Copyright (c) 2024, Lithe-Tech Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Arrear Tax Tool', {
    refresh: function(frm) {
        frm.disable_save();
    },

    onload: function(frm) {
        frm.set_value("month", ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            [frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()]);
        frm.set_value("year", frappe.datetime.get_today().split("-")[0]);
        erpnext.arrear_tax_tool.load_employees(frm);
    },

    month: function(frm) {
        erpnext.arrear_tax_tool.load_employees(frm);
    },
    year: function(frm) {
        erpnext.arrear_tax_tool.load_employees(frm);
    },

    department: function(frm) {
        erpnext.arrear_tax_tool.load_employees(frm);
    },

    designation: function(frm) {
        erpnext.arrear_tax_tool.load_employees(frm);
    },

    floor: function(frm) {
        erpnext.arrear_tax_tool.load_employees(frm);
    },

    facility_or_line: function(frm) {
        erpnext.arrear_tax_tool.load_employees(frm);
    },

    section: function(frm) {
        erpnext.arrear_tax_tool.load_employees(frm);
    },

    group: function(frm) {
        erpnext.arrear_tax_tool.load_employees(frm);
    },

    company: function(frm) {
        erpnext.arrear_tax_tool.load_employees(frm);
    },

    employee_id: function(frm) {
        erpnext.arrear_tax_tool.load_employees(frm);
    },
});

erpnext.arrear_tax_tool = {
    load_employees: function(frm) {
        if (frm.doc.month) {
            frappe.call({
                method: "custom_erpnext.custom_erpnext.doctype.arrear_tax_tool.arrear_tax_tool.get_employees",
                args: {
                    month: frm.doc.month,
                    year: frm.doc.year,
                    department: frm.doc.department,
                    designation: frm.doc.designation,
                    floor: frm.doc.floor,
                    facility_or_line: frm.doc.facility_or_line,
                    section: frm.doc.section,
                    group: frm.doc.group,
                    company: frm.doc.company,
                    employee_id: frm.doc.employee_id
                },
                callback: function(r) {
                    if (r.message['unmarked'].length > 0) {
                        unhide_field('unmarked_attendance_section');
                        if (!frm.employee_area) {
                            frm.employee_area = $('<div>')
                                .appendTo(frm.fields_dict.employees_html.wrapper);
                        }
                        frm.EmployeeSelector = new erpnext.EmployeeSelector(frm, frm.employee_area, r.message['unmarked']);
                    } else {
                        hide_field('unmarked_attendance_section');
                    }

                    if (r.message['marked'].length > 0) {
                        unhide_field('marked_attendance_section');
                        if (!frm.marked_employee_area) {
                            frm.marked_employee_area = $('<div>')
                                .appendTo(frm.fields_dict.marked_attendance_html.wrapper);
                        }
                    } else {
                        hide_field('marked_attendance_section');
                    }
                }
            });
        }
    }
}

erpnext.EmployeeSelector = class EmployeeSelector {
    constructor(frm, wrapper, employee) {
        this.wrapper = wrapper;
        this.frm = frm;
        this.make(frm, employee);
    }

    make(frm, employee) {
        var me = this;

        $(this.wrapper).empty();
        var employee_toolbar = $('<div class="col-sm-12 top-toolbar">\
            <button class="btn btn-default btn-add btn-xs" style="background-color:LightGray"></button>\
            <button class="btn btn-xs btn-default btn-remove" style="background-color:LightGray"></button>\
        </div>').appendTo($(this.wrapper));

        var mark_employee_toolbar = $('<div class="col-sm-12 bottom-toolbar" style="margin-top: 25px;">\
            <button class="btn btn-primary btn-assign btn-xs"></button>\
        </div>');

        employee_toolbar.find(".btn-add")
            .html(__('Check all'))
            .on("click", function() {
                $(me.wrapper).find('input[type="checkbox"]').each(function(i, check) {
                    if (!$(check).is(":checked")) {
                        check.checked = true;
                    }
                });
            });

        employee_toolbar.find(".btn-remove")
            .html(__('Uncheck all'))
            .on("click", function() {
                $(me.wrapper).find('input[type="checkbox"]').each(function(i, check) {
                    if ($(check).is(":checked")) {
                        check.checked = false;
                    }
                });
            });

        mark_employee_toolbar.find(".btn-assign")
            .html(__('Update'))
            .on("click", function() {
                var employees_to_shift = [];
                $(me.wrapper).find('input[type="checkbox"]').each(function(i, check) {
                    if ($(check).is(":checked")) {
                        var employeeData = {
                            employee: employee[i],
                            tax: $(me.wrapper).find('input[name="tax_' + (i + 1) + '"]').val(),
                            arear: $(me.wrapper).find('input[name="arear_' + (i + 1) + '"]').val(),
                            other_deduction: $(me.wrapper).find('input[name="other_deduction_' + (i + 1) + '"]').val(),
                        };
                        employees_to_shift.push(employeeData);
                    }
                });
                frappe.call({
                    method: "custom_erpnext.custom_erpnext.doctype.arrear_tax_tool.arrear_tax_tool.update_salary_slip",
                    args: {
                        "employee_list": employees_to_shift,
                    },
                    callback: function(r) {
                        alert("Salary Updated!");
                        erpnext.arrear_tax_tool.load_employees(frm);
                    }
                });
            });

        var row;
        $.each(employee, function(i, m) {
            if (i === 0 || (i % 1) === 0) {
                row = $('<div class="row"></div>').appendTo(me.wrapper);
            }
            if (i === 0) {
                $(repl('<table border="1" style="width:100%;  margin-top: 25px;">\
                    <tr>\
                        <td style="width:2%; text-align:center; color:transparent;">\
                            <label>chk</label>\
                        </td>\
                        <td style="width:30%; text-align:center;">\
                            <label>Employee</label>\
                        </td>\
                        <td style="width:20%; text-align:center;">\
                            <label>Income Tax</label>\
                        </td>\
                        <td style="width:20%; text-align:center;">\
                            <label>Arrear</label>\
                        </td>\
                        <td style="width:20%; text-align:center;">\
                            <label>Other Deduction</label>\
                        </td>\
                        <td style="width:3%; text-align:center;">\
                            <label>No</label>\
                        </td>\
                    </tr>\
                </table>', 
                '')).appendTo(row);
            }

            $(repl('<table border="1" style="width:100%">\
                <tr>\
                    <td style="width:1%; text-align:center;">\
                        <div class="checkbox">\
                            <label><input type="checkbox" /></label>\
                        </div>\
                    </td>\
                    <td style="width:30%; text-align:center;">\
                        <label>%(employee)s</label>\
                    </td>\
                    <td style="width:20%; text-align:center;">\
                        <label><input type="number" class="employee-check" name="tax_%(employee6)s" value="%(employee2)s" /></label>\
                    </td>\
                    <td style="width:20%; text-align:center;">\
                        <label><input type="number" class="employee-check" name="arear_%(employee6)s" value="%(employee3)s" /></label>\
                    </td>\
                    <td style="width:20%; text-align:center;">\
                        <label><input type="number" class="employee-check" name="other_deduction_%(employee6)s" value="%(employee4)s" /></label>\
                    </td>\
                    <td style="width:3%; text-align:center;">\
                        <label>%(employee6)s</label>\
                    </td>\
                </tr>\
            </table>', {
                employee6: i + 1,
                employee: m[0] + " : " + m[1],
                employee2: m[2],
                employee3: m[3],
                employee4: m[4]
            })).appendTo(row);
        });

        mark_employee_toolbar.appendTo($(this.wrapper));
    }
};
