import frappe

def update_ticket_gate_numbers(flight, gate):
    tickets = frappe.get_all("Airplane Ticket", filters={"flight": flight}, fields=["name"])

    for ticket in tickets:
        ticket_doc = frappe.get_doc("Airplane Ticket", ticket.name)
        ticket_doc.gate = gate
        ticket_doc.save(ignore_permissions=True)

    frappe.db.commit()