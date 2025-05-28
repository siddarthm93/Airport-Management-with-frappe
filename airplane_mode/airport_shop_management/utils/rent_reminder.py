import frappe
from frappe.utils import nowdate, add_days, getdate

def send_rent_due_reminders():
    setting = frappe.get_doc("Airport Shop Settings")
    if setting.enable_rent_reminder:
        payments = frappe.get_all("Rent Payment",
            filters={
                "status": "Due"
            },
            fields=["name", "tenant", "due_date", "airport_shop"] 
        )


        for payment in payments:
             
            tentant_email = frappe.get_doc("Tenant", payment.tenant).email_id

            if not tentant_email:
                continue
            
            subject = f"Rent Due Reminder - {payment.airport_shop}"
            message = f"""
                Dear Tenant,<br><br>
                This is a reminder that your rent for <b>{payment.airport_shop}</b> is due on <b>{payment.due_date}</b>.<br><br>
                Kindly make the payment before the due date to avoid any penalties.<br><br>
                Thank you.
            """
            frappe.sendmail(
                recipients=[tentant_email],
                subject=subject,
                message=message
            )
