// Copyright (c) 2025, siddarth and contributors
// For license information, please see license.txt

frappe.ui.form.on("Rent Payment", {
	// refresh(frm) {

	// },

	airport_shop: function (frm) {
		frappe.call({
			doc: frm.doc,
			method: "set_due_date",
			args: {
				doctype: "Rent Payment",
				airport_shop: frm.doc.airport_shop,
				tenant: frm.doc.tenant,
			},
			freeze: true,
			// async: true,
			callback: function (r) {
				if (r.message) {
					console.log(r.message);
					frm.refresh_field("due_date");
				}
			},
		});
	},
});
