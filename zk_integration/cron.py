# -*- coding: utf-8 -*-
# Copyright (c) 2021, Peter Maged and contributors
# For license information, please see license.txt


import frappe 



def update_employee_name_for_checkin():
    frappe.db.sql("""
                  update `tabEmployee Checkin` log 
                  set log.employee_name = 
                  (select emp.employee_name from tabEmployee emp where emp.name = log.employee limit 1) ;
                  """)
def cron_update_employee_name_for_checkin():
    update_employee_name_for_checkin()

def crons_all():
    print("\n\n\n\n all crons \n\n\n\n")
    frappe.msgprint("all crons")