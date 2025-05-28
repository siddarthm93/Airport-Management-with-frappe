# Copyright (c) 2025, siddarth and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator
from datetime import datetime
from frappe.utils import getdate, nowdate


class AirportShop(WebsiteGenerator):

	def validate(self):
		print("Validate")
		if self.monthly_rent == 0:
			self.area_sqft = 0
			frappe.throw("Monthly rent cannot be 0.")

		if self.area_sqft == 0:
			self.monthly_rent = 0
			frappe.throw("Area sqft cannot be 0.")

		if self.lease_start_date and self.contract_expiry_date:
			if self.lease_start_date > self.contract_expiry_date:
				frappe.throw("Lease start date cannot be greater than lease end date.")

		if self.lease_start_date:
			if self.lease_start_date < frappe.utils.nowdate():
				frappe.throw("Lease start date cannot be in the past date.")

		if self.contract_expiry_date:
			if self.contract_expiry_date < frappe.utils.nowdate():
				frappe.throw("Lease end date cannot be in the past date.")
		

	def before_submit(self):
		if self.is_occupied == 0:
			frappe.throw("Please select if the shop is occupied or not.")


	def before_insert(self):
		self.check_shop_exists()
		self.check_maximum_shop_capacity()
	
		if self.shop_code != 0 and self.shop_code:
			self.shop_number = f"{self.code}-SP-{self.shop_code}"
		else:
			frappe.throw("Please select a shop.")


	def on_submit(self):
		frappe.db.set_value("Airport Shop", self.name, "status", "Active")
		self.update_availability_count()
		self.reload()


	@frappe.whitelist()
	def get_airport_rent_amount(self,airport=None):
		# Fetch the airport rent amount from the Airport Shop Settings
		# document based on the airport name
		airport_setting = frappe.get_doc("Airport Shop Settings")
		if airport is None:
			frappe.throw("Please provide an airport name.")

		for airport_shop in airport_setting.airport_shop_price:
			if airport == airport_shop.airport:
				return airport_shop.default_rent_amount_per_sqft
			
		return 0
	

	def check_maximum_shop_capacity(self):
		capacity = frappe.get_doc("Airport",  self.airport).total_capacity

		total_shop = frappe.db.get_all(
			'Airport Shop', 
			filters={
				"airport": self.airport,
				"status" : ["in", ["Active", "In-active"]]
				}
			)

		if len(total_shop) > capacity:
			frappe.throw(f"Maximum shop capacity of {capacity} has been reached for {self.airport}. Please contact the administrator to increase the capacity.")

	
	def update_availability_count(self):

		occupied_count = frappe.db.count("Airport Shop",  {"status": "Active", "airport": self.airport, "docstatus": 1})
		total_count = frappe.get_doc("Airport", self.airport).total_capacity
		frappe.db.set_value('Airport', self.airport,{"occupied": occupied_count, "avilable": total_count - occupied_count})


	def check_shop_exists(self):

		existing_shops = frappe.get_all(
			"Airport Shop",
			filters={
				"airport": self.airport,
				"shop_code" : self.shop_code,
				"status" : ["in", ["Active", "In-active"]],
			})
		
		if len(existing_shops) > 0:
				frappe.throw(f"Shop with code {self.code}-SP-{self.shop_code} already exists in {self.airport}. Please select a different Shop.")


@frappe.whitelist()
def get_shop_details(doctype,fields,airport):
		shop_details ={}
		airport_shop = frappe.db.get_all(doctype, fields=fields, filters={"airport": airport})
		capacity = frappe.get_doc("Airport", airport).total_capacity

		shop_details["shop_details"] = airport_shop
		shop_details["capacity"] = capacity
		return shop_details