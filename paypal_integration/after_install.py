# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.setup.setup_wizard.setup_wizard import create_bank_account

def create_payment_gateway():
	if frappe.db.exists("DocType", "Payment Gateway"):
		if not frappe.db.exists("Payment Gateway", "PayPal"):
			payment_gateway = frappe.get_doc({
				"doctype": "Payment Gateway",
				"gateway": "PayPal"
			})
			payment_gateway.insert(ignore_permissions=True)

			if frappe.db.exists("DocType", "Payment Gateway Account"):
				create_gateway_account()

def create_gateway_account():
	company_name = frappe.db.get_value("Global Defaults", None, "default_company")
	if company_name:
		bank_account = frappe.db.get_value("Account", {"account_name": "PayPal", "company": company_name},
			["name", 'account_currency'], as_dict=1)

		if not bank_account:
			# try creating one
			bank_account = create_bank_account({"company_name": company_name, "bank_account": "PayPal"})
			if not bank_account:
				frappe.msgprint(_("Payment Gateway Account not created, please create one manually."))
				return

		if bank_account:
			try:
				frappe.get_doc({
					"doctype": "Payment Gateway Account",
					"is_default": 1,
					"payment_gateway": "PayPal",
					"payment_account": bank_account.name,
					"currency": bank_account.account_currency
				}).insert(ignore_permissions=True)

			except frappe.DuplicateEntryError:
				# already exists, due to a reinstall?
				pass
