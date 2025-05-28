// Copyright (c) 2025, siddarth and contributors
// For license information, please see license.txt

frappe.ui.form.on("Airplane Ticket", {
	refresh(frm) {
		frm.add_custom_button(
			"Assign Seat",
			() => {
				let d = new frappe.ui.Dialog({
					title: "Select Seat",
					fields: [
						{
							label: "Seat Number",
							fieldname: "seat_number",
							fieldtype: "Data",
						},
					],
					size: "small",
					primary_action_label: "Assign",
					primary_action(values) {
						console.log(values);
						frm.set_value("seat", values.seat_number);
						d.hide();
					},
				});

				d.show();
			},
			"Actions"
		);
	},

	onload: function (frm) {
		frm.set_query("flight", function () {
			return {
				filters: {
					status: "Scheduled",
				},
			};
		});
	},

	after_save: function (frm) {
		if (frm.doc.status === "Checked-In") {
			let options = frm.fields_dict.status.df.options.split("\n");
			let new_options = options.filter((opt) => opt.trim() !== "Booked");
			frm.fields_dict.status.df.options = new_options.join("\n");
			frm.refresh_field("status");
			frappe.show_alert({
				message: "Checked-In Successfully",
				indicator: "green",
			});
		}
	},
});
