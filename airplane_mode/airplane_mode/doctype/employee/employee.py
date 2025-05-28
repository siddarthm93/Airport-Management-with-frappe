# Copyright (c) 2025, siddarth and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime


class Employee(Document):
	
	def before_save(self):
		self.set_full_name()
		self.set_employee_id()
		
	def set_employee_id(self):
		if self.employee_id:
			return
		# Get the current year and month
		year = datetime.now().year

		# Get the current count of employees with the same designation
		designation = (self.designation or "EMP").replace(" ","-").upper()

		# Generate a new number based on the current count
		current_count = frappe.db.count("Employee", {
            "designation": self.designation,
            "creation": ["between", [f"{year}-01-01", f"{year}-12-31"]]
        })
		new_number = current_count + 1
		self.employee_id = f"EMP-{designation}-{year}-{new_number:03d}"

	# Set full name
	def set_full_name(self):
		self.full_name = f"{self.first_name} {self.last_name}" if self.last_name else self.first_name