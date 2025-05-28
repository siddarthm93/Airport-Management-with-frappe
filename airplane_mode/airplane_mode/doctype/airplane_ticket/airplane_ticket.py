# Copyright (c) 2025, siddarth and contributors
# For license information, please see license.txt

import frappe
import random
from frappe.model.document import Document


class AirplaneTicket(Document):
	
	def validate(self):
		self.remove_duplicate_addons()
		self.calculate_total_amount()

	def before_submit(self):
		self.check_passenger_is_boarded()

	def before_insert(self):
		self.check_flight_seat_capacity()

	# def on_update(self):
	# 	if self.status == "Checked-In":
	# 		self.generate_gate_number()

	def on_submit(self):
		self.update_ticket_status()
		
	
	def calculate_total_amount(self):
		total_addon_amount = 0

		for addons in self.add_ons:
			total_addon_amount += addons.amount

		self.total_amount = total_addon_amount + float(self.flight_price or 0)

	def remove_duplicate_addons(self):
		unique_addons =[]
		addons_name = set()

		for addon in self.add_ons:
			if addon.item not in addons_name:
				unique_addons.append(addon)
				addons_name.add(addon.item)

		self.add_ons = unique_addons

	def check_passenger_is_boarded(self):
		if self.status != "Boarded":
			frappe.throw("You can only submit the ticket if the status is 'Boarded'")


	def generate_seat_number(self):
		
		if not self.seat:
			number = random.randint(1, 99)
			letter = random.choice(['A', 'B', 'C', 'D'])
			self.seat = f"{number}{letter}"

	def update_ticket_status(self):
		self.db_set("status", "Completed")

	def check_flight_seat_capacity(self):
		flight = frappe.get_doc("Airplane Flight", self.flight)
		total_tickets = frappe.get_all("Airplane Ticket", filters={"flight": self.flight, "status" : "Booked"}, fields=["name"])
		airplane = frappe.get_doc("Airplane", flight.airplane)
		flight_capacity = airplane.capacity

		# Check if the flight is already full
		if len(total_tickets) >= flight_capacity:
			frappe.throw("Flight is already full. Cannot book more tickets.")


	def generate_gate_number(self):
		if not self.gate:
			# Generate a random gate number between 1 and 10
			number = random.randint(1, 10)
			letter = random.choice(['A', 'B', 'C', 'D'])
			gate_number = f"{number}{letter}"
			self.gate = f"G-{gate_number}"
