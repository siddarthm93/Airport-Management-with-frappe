// Copyright (c) 2025, siddarth and contributors
// For license information, please see license.txt

frappe.ui.form.on("Airplane Flight", {
	refresh(frm) {
		if (frm.doc.gate !== undefined) {
			frm.add_custom_button("Generate New Gate", () => {
				frappe.call({
					doc: frm.doc,
					method: "generate_gate_number",
					args: {
						check: true,
					},
					callback: function (r) {
						console.log(r.message);

						if (r.message) {
							frappe.msgprint("New Gate number is generated");
						}
					},
				});
			});
		}
	},

	validate(frm) {
		let crew_member_name = [];

		frm.doc.table_bebe.map((item) => {
			if (crew_member_name.includes(item.crew_member_name)) {
				frappe.throw(item.crew_member_name + " Member already selected");
			} else {
				crew_member_name.push(item.crew_member_name);
			}
		});
	},
});

// crew_member_name: (frm) => {
// 		frappe.throw("Member already selected");
// 	},

// frappe.ui.form.on("Flight Crew Member", {
// 	crew_member_name: (frm, cdt, cdn) => {
// 		let row = locals[cdt][cdn];
// 		console.log(row.crew_member_name);

// 		for (let row of frm.doc.table_bebe) {
// 			// console.log("row.crew_member_name : ", row.crew_member_name);
// 			// console.log("frm.doc.crew_member_name : ", frm.doc.table_bebe);
// 			if (row.crew_member_name == row.crew_member_name) {
// 				frappe.throw("Member already selected");
// 				return;
// 			}
// 		}
// 	},
// });
