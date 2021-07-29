# -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, get_datetime, flt
from collections import defaultdict
from erpnext.controllers.taxes_and_totals import get_itemised_tax_breakup_data


class POSClosingShift(Document):
    def validate(self):
        user = frappe.get_all('POS Closing Shift',
                              filters={'user': self.user, 'docstatus': 1},
                              or_filters={
                                  'period_start_date': ('between', [self.period_start_date, self.period_end_date]),
                                  'period_end_date': ('between', [self.period_start_date, self.period_end_date])
                              })

        if user:
            frappe.throw(_("POS Closing Shift {} against {} between selected period"
                           .format(frappe.bold("already exists"), frappe.bold(self.user))), title=_("Invalid Period"))

        if frappe.db.get_value("POS Opening Shift", self.pos_opening_shift, "status") != "Open":
            frappe.throw(_("Selected POS Opening Shift should be open."), title=_(
                "Invalid Opening Entry"))

    def on_submit(self):
        opening_entry = frappe.get_doc(
            "POS Opening Shift", self.pos_opening_shift)
        opening_entry.pos_closing_shift = self.name
        opening_entry.set_status()
        self.delete_draft_invoices()
        opening_entry.save()

    def delete_draft_invoices(self):
        if frappe.get_value("POS Profile", self.pos_profile, "posa_allow_delete"):
            data = frappe.db.sql("""
                select
                    name
                from
                    `tabSales Invoice`
                where
                    docstatus = 0 and posa_is_printed = 0 and posa_pos_opening_shift = %s
                """, (self.pos_opening_shift), as_dict=1)

            for invoice in data:
                frappe.delete_doc("Sales Invoice", invoice.name, force=1)

    def get_payment_reconciliation_details(self):
        currency = frappe.get_cached_value(
            'Company', self.company,  "default_currency")
        return frappe.render_template("posawesome/posawesome/doctype/pos_closing_shift/closing_shift_details.html",
                                      {"data": self, "currency": currency})

    
    def on_update_invoice(self):
            total=0
            # grand_total=0
            val=frappe.get_doc("POS Closing Shift", self.name)
            for item in val.pos_transactions:
                total+=1
                # grand_total= grand_total + item.grand_total
            val.no_of_invoices = total
            # val.grand_total = grand_total
            val.save()
            val.submit()


@frappe.whitelist()
def get_cashiers(doctype, txt, searchfield, start, page_len, filters):
    cashiers_list = frappe.get_all(
        "POS Profile User", filters=filters, fields=['user'])
    return [c['user'] for c in cashiers_list]


@frappe.whitelist()
def get_pos_invoices(pos_opening_shift):
    submit_printed_invoices(pos_opening_shift)
    data = frappe.db.sql("""
	select
		name
	from
		`tabSales Invoice`
	where
		docstatus = 1 and posa_pos_opening_shift = %s
	""", (pos_opening_shift), as_dict=1)

    data = [frappe.get_doc("Sales Invoice", d.name).as_dict() for d in data]

    return data


@frappe.whitelist()
def make_closing_shift_from_opening(opening_shift):
    opening_shift = json.loads(opening_shift)
    submit_printed_invoices(opening_shift.get("name"))
    closing_shift = frappe.new_doc("POS Closing Shift")
    closing_shift.pos_opening_shift = opening_shift.get("name")
    closing_shift.period_start_date = opening_shift.get("period_start_date")
    closing_shift.period_end_date = frappe.utils.get_datetime()
    closing_shift.pos_profile = opening_shift.get("pos_profile")
    closing_shift.user = opening_shift.get("user")
    closing_shift.company = opening_shift.get("company")
    closing_shift.grand_total = 0
    closing_shift.net_total = 0
    closing_shift.total_quantity = 0

    invoices = get_pos_invoices(opening_shift.get("name"))

    pos_transactions = []
    taxes = []
    payments = []
    # cash_denominations_breakdown = [] #

    # doc = frappe.get_doc("POS Closing Shift")
    # row = closing_shift.append("cash_denominations_breakdown", {})
    # row.amount = 50
    # row.quantity = 2
    # row.total = 50
    
    for detail in opening_shift.get("balance_details"):
        payments.append(frappe._dict({
            'mode_of_payment': detail.get("mode_of_payment"),
            'opening_amount': detail.get("amount") or 0,
            'expected_amount': detail.get("amount") or 0
        }))

    for d in invoices:
        pos_transactions.append(frappe._dict({
            'sales_invoice': d.name,
            'posting_date': d.posting_date,
            'grand_total': d.grand_total,
            'customer': d.customer
        }))
        closing_shift.grand_total += flt(d.grand_total)
        closing_shift.net_total += flt(d.net_total)
        closing_shift.total_quantity += flt(d.total_qty)

        for t in d.taxes:
            existing_tax = [tx for tx in taxes if tx.account_head ==
                            t.account_head and tx.rate == t.rate]
            if existing_tax:
                existing_tax[0].amount += flt(t.tax_amount)
            else:
                taxes.append(frappe._dict({
                    'account_head': t.account_head,
                    'rate': t.rate,
                    'amount': t.tax_amount
                }))

        for p in d.payments:
            existing_pay = [
                pay for pay in payments if pay.mode_of_payment == p.mode_of_payment]
            if existing_pay:
                cash_mode_of_payment = frappe.get_value(
                    "POS Profile", opening_shift.get("pos_profile"), "posa_cash_mode_of_payment")
                if not cash_mode_of_payment:
                    cash_mode_of_payment = "Cash"
                if existing_pay[0].mode_of_payment == cash_mode_of_payment:
                    amount = p.amount - d.change_amount
                else:
                    amount = p.amount
                existing_pay[0].expected_amount += flt(amount)
            else:
                payments.append(frappe._dict({
                    'mode_of_payment': p.mode_of_payment,
                    'opening_amount': 0,
                    'expected_amount': p.amount,
                }))

    closing_shift.set("pos_transactions", pos_transactions)
    closing_shift.set("payment_reconciliation", payments)
    closing_shift.set("taxes", taxes)

    return closing_shift

@frappe.whitelist()
def submit_closing_shift(closing_shift, closing_cash, checkout_counter):
    cash_details = []
    closing_cash = json.loads(closing_cash)
    closing_shift = json.loads(closing_shift)    
    closing_shift_doc = frappe.get_doc(closing_shift)
    closing_cash_withdrawal = frappe.get_doc({
        'doctype': 'POS Closing Shift'
    })
    # for item in closing_cash.get("cash_details"):
    #         cash_details.append({'amount': item["amount"], 'quantity': item["quantity"], 'total': item["total"]})
    # closing_cash_withdrawal.set("cash_denominations_breakdown", cash_details)
    for item in closing_cash.get("cash_details"):
            closing_shift_doc.append("cash_denominations_breakdown", {'amount': item["amount"], 'quantity': item["quantity"], 'total': item["total"]})
    closing_cash_withdrawal.set("cash_denominations_breakdown", cash_details)
    # closing_shift_doc.append("cash_denominations_breakdown", {
    #     "amount": 100,
    #     "quantity": 1,
    #     "total": 100
    # })
    closing_shift_doc.checkout_counter = checkout_counter
    submit_total_closing_readings(closing_shift_doc) #testing
    closing_shift_doc.flags.ignore_permissions = True
    closing_shift_doc.save()
    closing_shift_doc.submit()
    return closing_shift_doc.name


def submit_printed_invoices(pos_opening_shift):
    invoices_list = frappe.get_all("Sales Invoice", filters={
        "posa_pos_opening_shift": pos_opening_shift,
        "docstatus": 0,
        "posa_is_printed": 1
    })
    for invoice in invoices_list:
        invoice_doc = frappe.get_doc("Sales Invoice", invoice.name)
        invoice_doc.submit()

def submit_total_closing_readings(closing_shift_doc):
    total_cash=0
    total_card=0
    first_invoice = ""
    last_invoice = ""
    first_void=""
    void_count_array = []
    total = 0
    gross_amount = 0
    senior_discount = 0
    pwd_discount = 0

    # closing_shift_doc=frappe.get_doc("POS Closing Shift", closing_shift)
    array_length = len(closing_shift_doc.pos_transactions)
    for i in closing_shift_doc.pos_transactions:
        total+=1
        gross_amount= gross_amount + i.grand_total

        invoice_get=frappe.get_doc("Sales Invoice", i.sales_invoice)

        if(invoice_get.additional_discount_type):
            if(invoice_get.additional_discount_type=="PWD"):
                pwd_discount += invoice_get.grand_total
            elif (invoice_get.additional_discount_type=="SRCT"):
                senior_discount += invoice_get.grand_total

        if(invoice_get.status=="Draft"):
            if(len(void_count_array)==0):
                first_void = invoice_get.name
            void_count_array.append(invoice_get.name)

        if(total == 1):
            first_invoice = invoice_get.name
        if(total==array_length): 
            last_invoice = invoice_get.name

        for item in invoice_get.payments:
            if(item.mode_of_payment == "Cash"):
                total_cash = total_cash + item.amount
            if(item.mode_of_payment == "Credit Card" or item.mode_of_payment == "Debit Card"):
                total_card = total_card + item.amount
 

    closing_shift_doc.first_void_no = first_void
    if(len(void_count_array)!=0):
        closing_shift_doc.last_void_no = void_count_array[-1]
    closing_shift_doc.void_count = len(void_count_array)
    closing_shift_doc.gross_amount = gross_amount
    closing_shift_doc.no_of_invoices = total
    closing_shift_doc.total_cash = total_cash
    closing_shift_doc.total_card = total_card
    closing_shift_doc.pwd_discount = pwd_discount
    closing_shift_doc.senior_discount = senior_discount
    closing_shift_doc.last_sales_invoice = last_invoice
    closing_shift_doc.first_sales_invoice = first_invoice
    # closing_shift_doc.submit()