# Copyright (c) 2025, siddarth and contributors
# For license information, please see license.txt

import frappe
import random
from frappe.website.website_generator import WebsiteGenerator
from frappe.utils.background_jobs import enqueue
from airplane_mode.background_tasks.ticket_updates import update_ticket_gate_numbers

class AirplaneFlight(WebsiteGenerator):
	def on_submit(self):
		self.update_ticket_status()

	def before_save(self):
		if not self.gate:
			self.generate_gate_number()
			# self.reload()

	def on_update(self,method=None):
		if self.has_value_changed("gate"):
			enqueue(
				update_ticket_gate_numbers,
				queue='long',
				flight=self.name,
				gate=self.gate
		   )

	def update_ticket_status(self):
		self.db_set("status", "Completed")

	@frappe.whitelist()
	def generate_gate_number(self,check=False):
		if not self.gate or check:
			# Generate a random gate number between 1 and 10
			number = random.randint(1, 10)
			letter = random.choice(['A', 'B', 'C', 'D'])
			gate_number = f"{number}{letter}"
			self.gate = f"G-{gate_number}"
			if check:
				self.save()

			return gate_number