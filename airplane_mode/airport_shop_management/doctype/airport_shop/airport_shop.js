// Copyright (c) 2025, siddarth and contributors
// For license information, please see license.txt

frappe.ui.form.on("Airport Shop", {
	refresh: async function (frm) {
		if (frm.doc.airport) {
			await frm.trigger("render_shop_grid");
		}
	},

	onload: function (frm) {
		frm.set_query("shop_type", function () {
			return {
				filters: {
					enabled: 1,
				},
			};
		});
	},

	before_save: async function (frm) {
		await frm.trigger("calculate_rent_amount");
	},

	lease_start_date: (frm) => {
		// start date canot be less than today
		if (frm.doc.lease_start_date < frappe.datetime.get_today()) {
			frappe.msgprint("Lease start date cannot be less than today");
		}
	},

	contract_expiry_date: (frm) => {
		// start date canot be less than today
		if (frm.doc.contract_expiry_date < frappe.datetime.get_today()) {
			frappe.msgprint("Lease contract date cannot be less than today");
		}
		if (frm.doc.contract_expiry_date < frm.doc.lease_start_date) {
			frappe.msgprint("Lease contract date cannot be less than lease start date");
		}
	},

	// Calculate the Rent Amount based on the default airport rent amount and the area
	// sqft of the shop
	area_sqft: async function (frm) {
		await frm.trigger("calculate_rent_amount");
	},

	is_occupied: function (frm) {
		frm.set_value("total_rent_amount", frm.doc.monthly_rent);
	},

	extra_charges: (frm) => {
		let totalRent = frm.doc.extra_charges + frm.doc.monthly_rent;
		frm.set_value("total_rent_amount", totalRent);
	},

	async calculate_rent_amount(frm) {
		frappe.call({
			doc: frm.doc,
			method: "get_airport_rent_amount",
			args: {
				airport: frm.doc.airport,
			},
			callback: function (r) {
				if (r.message) {
					const monthly_rent = r.message * frm.doc.area_sqft;
					frm.set_value("monthly_rent", monthly_rent);
					if (frm.doc.is_occupied) {
						let totalRent = monthly_rent;

						if (doc.extra_charges !== 0) {
							totalRent += doc.extra_charges;
						}
						frm.set_value("total_rent_amount", totalRent);
					}
				}
			},
		});
	},

	airport: async (frm) => {
		if (frm.doc.airport) {
			await frm.trigger("render_shop_grid");
			frm.set_value("shop_code", "");
		}
	},

	async render_shop_grid(frm) {
		frappe.call({
			method: "airplane_mode.airport_shop_management.doctype.airport_shop.airport_shop.get_shop_details",
			args: {
				doctype: "Airport Shop",
				fields: ["shop_code", "code"],
				airport: frm.doc.airport,
			},
			callback: async function (r) {
				const occupied = r.message.shop_details.map((d) => d.shop_code);
				const capacity = r.message.capacity;
				const isShopNumberSet = frm.doc.shop_number !== undefined;

				console.log(frm.doc.shop_number);

				let html = `<div style="display: flex; flex-wrap: wrap; gap: 10px;">`;

				// let capacity = 0;
				for (let i = 1; i <= capacity; i++) {
					const isOccupied = occupied.includes(i);
					const selected = frm.doc.shop_code == i;
					const isShopNumberSet = frm.doc.shop_number !== undefined;

					console.log("shop code", frm.doc.shop_code);

					html += `
                        <div
                            class="locker-box ${isOccupied ? "Occupied" : "Available"} ${
						selected ? "selected" : ""
					}"
                            data-locker="${i}"
                            style="
                                width: 60px;
                                height: 60px;
                                background: ${
									selected ? "#00ff99" : isOccupied ? "#ccc" : "#e0ffe0"
								};
                                border: 1px solid #888;
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                cursor: ${isOccupied ? "not-allowed" : "pointer"};
                                font-weight: bold;
                                border-radius: 6px;
                            "
                        >
                            ${i}
                        </div>
                    `;
				}

				html += `</div>`;
				frm.fields_dict.shops.$wrapper.html(html);

				// Click to select locker
				frm.fields_dict.shops.$wrapper.on("click", ".locker-box.Available", function () {
					const isShopNumberSet = frm.doc.shop_number !== undefined;

					if (!isShopNumberSet || frm.doc.docstatus === 0) {
						console.log("On Click ", frm.doc.shop_number);
						const lockerNumber = $(this).data("locker");
						frm.set_value("shop_code", lockerNumber);
						if (frm.doc.docstatus === 0 && frm.doc.shop_number) {
							let shopPrefix = frm.doc.shop_number.split("-");
							newShopNumber =
								shopPrefix[0] + "-" + shopPrefix[1] + "-" + lockerNumber;
							frm.set_value("shop_number", newShopNumber);
						}
						frm.trigger("render_shop_grid");
					}
				});
			},
		});
	},
});

frappe.ui.form.on("Rent Payment", {
	rent_payment_add: function (frm, cdt, cdn) {
		const row = locals[cdt][cdn];

		const lease_start = frm.doc.lease_start_date;
		if (!lease_start) {
			frappe.msgprint("Please set Lease Start Date before adding rent payments.");
			return;
		}

		const leaseDate = frappe.datetime.str_to_obj(lease_start);
		const existingCount = (frm.doc.rent_payment || []).length - 1;
		const dueDate = frappe.datetime.add_months(leaseDate, existingCount + 1);

		row.due_date = frappe.datetime.obj_to_str(dueDate);

		row.rent_amount = frm.doc.total_rent_amount;

		frm.refresh_field("rent_payment");
	},
});
