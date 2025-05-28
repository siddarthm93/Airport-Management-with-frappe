import frappe
from frappe.utils import add_months, getdate, today
import calendar


def schedule_rent_payments():
    shops = frappe.get_all(
        "Airport Shop",
        filters={"status": "Active"},
        fields=["name", "tenant", "lease_start_date", "contract_expiry_date", "total_rent_amount"]
    )

    for shop in shops:
        try:
            # Get last payment
            last_payment = frappe.get_all(
                "Rent Payment",
                filters={"airport_shop": shop.name},
                order_by="due_date desc",
                limit=1,
                fields=["due_date"]
            )

            if last_payment:
                last_date = getdate(last_payment[0]["due_date"])
                next_due = add_months(last_date, 1)
            else:
                next_due = getdate(shop.lease_start_date)

            if next_due > getdate(shop.contract_expiry_date):
                continue

            if frappe.db.exists("Rent Payment", {"airport_shop": shop.name, "due_date": next_due}):
                continue

            rent_date = getdate(next_due)
            month_str = rent_date.strftime("%m")
            year_str = rent_date.strftime("%y")

            # Count existing records for this month-year-shop
            existing_count = frappe.db.count("Rent Payment", {
                "airport_shop": shop.name,
                "month": calendar.month_name[rent_date.month],
                "due_date": ("like", f"{rent_date.year}-{rent_date.month:02d}-%")
            })

            sequence = f"{existing_count + 1:04d}"  # 0001, 0002, etc.
            custom_name = f"REC-{month_str}-{year_str}-{shop.name}-{sequence}"

            doc = frappe.new_doc("Rent Payment")
            doc.name = custom_name
            doc.airport_shop = shop.name
            doc.tenant = shop.tenant
            doc.payment_date = today()
            doc.due_date = add_months(next_due, 1)
            doc.month = calendar.month_name[rent_date.month]
            doc.rent_amount = shop.total_rent_amount
            doc.status = "Due"

            doc.insert(ignore_permissions=True)
            frappe.db.commit()

        except Exception as e:
            frappe.log_error(f"Failed to create rent payment for {shop.name}: {str(e)}")
            frappe.db.rollback()
