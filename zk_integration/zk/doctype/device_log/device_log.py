# -*- coding: utf-8 -*-
# Copyright (c) 2021, Peter and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from zk_integration.zk.doctype.zk_device.zk_device import sync_employee
from zk_integration.zk.doctype.zk_device.zk_device import get_active_device_logs
from frappe.utils import cint, get_datetime
from hrms.hr.doctype.shift_assignment.shift_assignment import (
	get_actual_start_end_datetime_of_shift,
)

class DeviceLog(Document):
	pass
@frappe.whitelist()
def create_employee_checkin(names=None):
	sync_employee()
	# sql = """
	# Insert Into `tabEmployee Checkin` (name , employee , time , log_type,device_log,device,creation,modified,owner)
	# (select name , employee , time , type,name,device,creation,modified,owner from `tabDevice Log` 
	# where employee is not null
	# and  name not in (select device_log from `tabEmployee Checkin` where device_log is not null));
	# """
	sql = """
			INSERT INTO `tabEmployee Checkin` (name, employee, time, log_type, device_log, device, creation, modified, owner, shift)
			(SELECT 
				dl.name, 
				dl.employee, 
				dl.time, 
				dl.type, 
				dl.name, 
				dl.device, 
				dl.creation, 
				dl.modified, 
				dl.owner, 
				e.default_shift
			FROM `tabDevice Log` dl
			JOIN `tabEmployee` e ON dl.employee = e.name
			WHERE dl.employee IS NOT NULL
			AND dl.name NOT IN (SELECT device_log FROM `tabEmployee Checkin` WHERE device_log IS NOT NULL));

			"""
	# frappe.msgprint(sql)
	frappe.db.sql(sql)
	frappe.db.commit()
	update_shift_time()
	frappe.db.commit()
	

def update_shift_time():
	list_checking = frappe.db.get_list('Employee Checkin',filters={
                        "shift_actual_end": None,
                        "shift_actual_start":None,
                        "shift_end":None,
                        },
                        fields='name',as_list=True)
	# print(f"\n\nlist {len(list_checking)}\n\n")
	if isinstance(list_checking, tuple): 
		list_checking = list(list_checking)

	for checkin in list_checking:
		get_checkin_doc = frappe.get_doc("Employee Checkin", checkin[0])
		if get_checkin_doc.shift:
			fetch_shift(get_checkin_doc)

@frappe.whitelist()
def cron_create_employee_checkin(names=None):
	create_employee_checkin(names)

def execute (names=None):
	try:
		get_active_device_logs()
	except :
		pass
	try:
		sync_employee()
	except :
		pass
	try:
		create_employee_checkin()
	except :
		pass


def fetch_shift(doc):
		shift_actual_timings = get_actual_start_end_datetime_of_shift(
			doc.employee, get_datetime(doc.time), True
		)
		if shift_actual_timings:
			if (
				shift_actual_timings.shift_type.determine_check_in_and_check_out
				== "Strictly based on Log Type in Employee Checkin"
				and not doc.log_type
				and not doc.skip_auto_attendance
			):
				frappe.throw(
					_("Log Type is required for check-ins falling in the shift: {0}.").format(
						shift_actual_timings.shift_type.name
					)
				)
			if not doc.attendance:
				doc.shift = shift_actual_timings.shift_type.name
				doc.shift_actual_start = shift_actual_timings.actual_start
				doc.shift_actual_end = shift_actual_timings.actual_end
				doc.shift_start = shift_actual_timings.start_datetime
				doc.shift_end = shift_actual_timings.end_datetime
		else:
			doc.shift = None
		doc.save()
