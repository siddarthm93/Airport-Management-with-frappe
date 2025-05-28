# Copyright (c) 2025, siddarth and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = [
		{
			"fieldname": "airline",
			"label":"Airline",
			"fieldtype": "Link",
			"options": "Airline",
			"width": 150
		},
		{
			"fieldname": "revenue",
			"fieldtype": "Currency",
		   	"label":"Revenue",
			"options": "currency",
			"width": 150
		}
		],[]
	
	records = frappe.get_all("Airplane Ticket",fields=["flight_price","flight.airplane as airplane"])
	
	new_data = {}

	for record in records:
		if record.airplane is not None:
			airline = frappe.get_doc("Airplane",record.airplane).airline
			if airline in new_data:
				new_data[airline] += record.flight_price
			else:
				new_data[airline] = record.flight_price


	airline = frappe.get_all("Airline",fields=["name"])

	for item in airline:
		if item.name in new_data:
			airline = item.name
			revenue = new_data[item.name]
			data.append({
					"airline": airline,
					"revenue":revenue,	
				})
		else:
			data.append({
					"airline": item.name,
					"revenue":0,
				})

	
	if not data:
		return columns, 

	data = sorted(data, key=lambda x: x['revenue'], reverse=True)
	
	chart ={
		"data":{
			"labels" : [d["airline"] for d in data],
			"datasets":[ 
				{
					"name": "Revenue By Airline",
					"values": [d["revenue"] for d in data],
				}
			]
		},
		"type": "donut",
	}

	report_summary = [{"value": sum([d["revenue"] for d in data]), "datatype": "Currency", "label": "Total Revenue"}] 

	return columns, data, None, chart, report_summary
