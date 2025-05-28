// Copyright (c) 2025, siddarth and contributors
// For license information, please see license.txt

frappe.ui.form.on("Airline", {
	refresh(frm) {
		if (frm.doc.website) {
			frm.add_web_link(frm.doc.website, "<i class='fa fa-globe'></i> Visit Website");
		}
	},
});
