# Copyright (c) 2025, siddarth and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FlightPassenger(Document):
	
	#  Set full name
	def before_save(self):
		    self.full_name = f"{self.first_name} {self.last_name}" if self.last_name else self.first_name


		

