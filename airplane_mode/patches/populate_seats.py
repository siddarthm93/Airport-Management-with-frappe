import frappe
import random

def execute():
    tickets = frappe.get_all("Airplane Ticket", fields=["name", "seat"])

    for ticket in tickets:
        if not ticket.seat:
            seat_number = f"{random.randint(1, 99)}{random.choice(['A', 'B', 'C', 'D', 'E'])}"
            frappe.db.set_value("Airplane Ticket", ticket.name, "seat", seat_number)

    frappe.db.commit()