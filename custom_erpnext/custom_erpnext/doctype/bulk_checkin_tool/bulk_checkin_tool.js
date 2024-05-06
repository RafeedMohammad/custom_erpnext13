// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bulk Checkin Tool', {
	refresh: function(frm) {
		frm.disable_save();
	},
	

	onload: function(frm) {
		frm.set_value("date", frappe.datetime.get_today());
		erpnext.bulk_checkin_tool.load_employees(frm);
	},

	select_shift: function(frm){
		erpnext.bulk_checkin_tool.load_employees(frm);

	},

	department: function(frm) {
		erpnext.bulk_checkin_tool.load_employees(frm);
	},

	designation: function(frm) {
		erpnext.bulk_checkin_tool.load_employees(frm);
	},

	floor: function(frm) {
		erpnext.bulk_checkin_tool.load_employees(frm);
	},

	facility_or_line: function(frm) {
		erpnext.bulk_checkin_tool.load_employees(frm);
	},

	section: function(frm) {
		erpnext.bulk_checkin_tool.load_employees(frm);
	},

	group: function(frm) {
		erpnext.bulk_checkin_tool.load_employees(frm);
	},

	company: function(frm) {
		erpnext.bulk_checkin_tool.load_employees(frm);
	},

	employee_id: function(frm) {
		erpnext.bulk_checkin_tool.load_employees(frm)
	},	

});


erpnext.bulk_checkin_tool = {
	load_employees: function(frm) {
		if(frm.doc.date) {
			frappe.call({
				method: "custom_erpnext.custom_erpnext.doctype.bulk_checkin_tool.bulk_checkin_tool.get_employees",
				args: {
					date: frm.doc.date,
					shift: frm.doc.select_shift,
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
					if(r.message['unmarked'].length > 0) {
						unhide_field('unmarked_attendance_section')
						if(!frm.employee_area) {
							frm.employee_area = $('<div>')
							.appendTo(frm.fields_dict.employees_html.wrapper);
						}
						frm.EmployeeSelector = new erpnext.EmployeeSelector(frm, frm.employee_area, r.message['unmarked'])
					}
					else{
						hide_field('unmarked_attendance_section')
					}

					if(r.message['marked'].length > 0) {
						unhide_field('marked_attendance_section')
						if(!frm.marked_employee_area) {
							frm.marked_employee_area = $('<div>')
								.appendTo(frm.fields_dict.marked_attendance_html.wrapper);
						}
						frm.marked_employee = new erpnext.MarkedEmployee(frm, frm.marked_employee_area, r.message['marked'])
					}
					else{
						hide_field('marked_attendance_section')
					}
				}
			});
		} //load_employees ends here

	}
}






erpnext.MarkedEmployee = class MarkedEmployee {
	constructor(frm, wrapper, employee) {
		this.wrapper = wrapper;
		this.frm = frm;
		this.make(frm, employee);
	}
	make(frm, employee) {
		var me = this;
		$(this.wrapper).empty();

		var row;
		$.each(employee, function(i, m) {
			var attendance_icon = "fa fa-check";
			var color_class = "";
			if(m.status == "Absent") {
				attendance_icon = "fa fa-check-empty"
				color_class = "text-muted";
			}
			else if(m.status == "Half Day") {
				attendance_icon = "fa fa-check-minus"
			}

			if (i===0 || i % 4===0) {
				row = $('<div class="row"></div>').appendTo(me.wrapper);
			}

			$(repl('<div class="col-sm-3 %(color_class)s">\
				<label class="marked-employee-label"><span class="%(icon)s"></span>\
				%(employee)s</label>\
				</div>', {
					employee: m.employee_name, //employee_name
					icon: attendance_icon,
					color_class: color_class
				})).appendTo(row);
		});
	}
};


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
			<button class="btn btn-default btn-add btn-xs"></button>\
			<button class="btn btn-xs btn-default btn-remove"></button>\
			</div>').appendTo($(this.wrapper));

		var mark_employee_toolbar = $('<div class="col-sm-12 bottom-toolbar">\
			<button class="btn btn-primary btn-assign btn-xs"></button>\
			');

		employee_toolbar.find(".btn-add")
			.html(__('Check all'))
			.on("click", function() {
				$(me.wrapper).find('input[type="checkbox"]').each(function(i, check) {
					if(!$(check).is(":checked")) {
						check.checked = true;
					}
				});
			});

		employee_toolbar.find(".btn-remove")
			.html(__('Uncheck all'))
			.on("click", function() {
				$(me.wrapper).find('input[type="checkbox"]').each(function(i, check) {
					if($(check).is(":checked")) {
						check.checked = false;
					}
				});
			});


		//This methods are used to set the marked employees' status to the selected one! We can take status from a dropdown or link, instead of a button 

		mark_employee_toolbar.find(".btn-assign")
			.html(__('Assign'))
			.on("click", function() {
				var employees_to_shift = [];
				$(me.wrapper).find('input[type="checkbox"]').each(function(i, check) {
					if($(check).is(":checked")) {
						employees_to_shift.push(employee[i]);
					}
				});
				frappe.call({
					method: "custom_erpnext.custom_erpnext.doctype.bulk_checkin_tool.bulk_checkin_tool.mark_employee_attendance2",
					args:{
						"employee_list":employees_to_shift,
						"checkin_time": frm.doc.checkin_time,
					},

					callback: function(r) {
						alert("Checkin Assigned successfully !");
						erpnext.bulk_checkin_tool.load_employees(frm);

					}
				});
			});

		
		var row;
		$.each(employee, function(i, m) {
			if (i===0 || (i % 2) === 0) {
				row = $('<div class="row"></div>').appendTo(me.wrapper);
			}
			if (i===0){
			$(repl('<table border="1" style="width:100%;  margin-top: 25px;">\
			<tr>\
				<td style="width:2%; text-align:center; color:transparent;">\
						<label>chk</label>\
				</td>\
				<td style="width:30%; text-align:center;">\
						<label><class="employee-check""/>Employee</label>\
				</td>\
				<td style="width:20%; text-align:center;">\
						<label><class="employee-check""/>Shift</label>\
				</td>\
				<td style="width:3%; text-align:center;">\
				<label><class="employee-check""/></label>\
				</td>\
			</tr>\
		</table>'
		, )).appendTo(row); }

			$(repl('<table border="1" style="width:100%">\
			<tr>\
				<td style="width:1%; text-align:center;">\
				<div class="checkbox">\
						<label><input type="checkbox" "</label>\
					</div>\
				</td>\
				<td style="width:30%; text-align:center;">\
						<label><class="employee-check""/>%(employee)s</label>\
				</td>\
				<td style="width:20%; text-align:center;">\
						<label><class="employee-check""/>%(employee2)s</label>\
				</td>\
				<td style="width:3%; text-align:center;">\
				<label><class="employee-check""/>%(employee6)s</label>\
				</td>\
			</tr>\
		</table>'
		, {employee6:i+1,employee:m[0]+" : "+m[1],employee2:m[2]})).appendTo(row); //was: m.employee_name
		});


		mark_employee_toolbar.appendTo($(this.wrapper));
	}
};
