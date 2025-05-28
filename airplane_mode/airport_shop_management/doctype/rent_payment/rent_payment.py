# Copyright (c) 2025, siddarth and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, add_months


class RentPayment(Document):
	
	def validate(self):
		if self.airport_shop and self.month:
			payement_recepit = frappe.get_all(
				"Rent Payment", 
				filters={
					"airport_shop":self.airport_shop, 
					"month":self.month,
					"tenant":self.tenant,
					"docstatus": 1
					},
				order_by="creation desc", limit=1)
						
			if len(payement_recepit) > 0:
				frappe.throw("Rent payment already exists for this month.")

	@frappe.whitelist()
	def set_due_date(self,doctype, airport_shop,tenant):
		#  Set due date to next month from the lease start date if already paid for a month then set to the next month
		shop = frappe.doc = frappe.get_doc('Airport Shop', airport_shop)

		if not shop:
			frappe.throw("Shop not found.")
		
		shop_rent = frappe.get_all(doctype, 
							 filters={"airport_shop": airport_shop,"tenant":tenant}, 
							 fields=["*"],
							 order_by="creation desc", limit=1)
	
		if shop_rent:
			# Get the last payment date
			last_payment_date = getdate(shop_rent[0].due_date)
			# Set the due date to the next month
			self.due_date = frappe.utils.add_months(last_payment_date, 1)
			return self.due_date
		else:
			# Set the due date to the lease start date # unsupported operand type(s) for +: 'datetime.date' and 'datetime.date'

			self.due_date =  frappe.utils.add_months(shop.lease_start_date, 1)

			return self.due_date
			
	def on_update(self):
		# self.update_status_from_workflow()
		pass


	def before_save(self):
		date = getdate(self.payment_date or nowdate())
	
		last_record = frappe.get_all("Rent Payment", 
							   fields=["receipt_number"], 
							   filters={"shop": self.airport_shop,"tenant":self.tenant}, 
							   order_by="creation desc", 
							   limit=1)
		
		if last_record:
			last_record = last_record[0]
			self.receipt_number = f"REC-{date.year}-{date.month}-{self.airport_shop}-{int(last_record.receipt_number.split('-')[6]) + 1}"
		else:
			self.receipt_number = f"REC-{date.year}-{date.month}-{self.airport_shop}-{1}"

	def update_status_from_workflow(self):
		# Set your custom status based on workflow_state or action
		if self.workflow_state == "Due":
			self.status = "Due"
		elif self.workflow_state == "Pending Approval":
			self.status = "Pending"
		elif self.workflow_state == "Paid":
			self.status = "Paid"
			
		self.save()


	@frappe.whitelist()
	def create_next_rent_payment(self,shop_name, tenant):

		shops = frappe.get_doc("Airport Shop", shop_name)
		if shops.status in ["Expired", "In-Active"]:
			frappe.throw(f"Cannot create rent payment: shop is {shops.status}.")
			
		lease_start_date = getdate(shops.lease_start_date)
		contract_expiry_date = getdate(shops.contract_expiry_date)

		today = getdate(nowdate())

		if today > contract_expiry_date:
			frappe.throw("Contract has ended. No more payments can be scheduled.")

		last_payment = frappe.get_all("Rent Payment", 
								filters={"airport_shop": shop_name, "tenant": tenant},
								fields=["*"],
								order_by="creation desc", limit=1
								)
		
		if last_payment:
			last_payment_date = getdate(last_payment[0].due_date)
			next_due_date = add_months(last_payment_date, 1)
		else:
			next_due_date = add_months(lease_start_date, 1)


