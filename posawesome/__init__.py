# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

<<<<<<< HEAD
__version__ = "1.1.0"
=======
__version__ = "2.0.1"
>>>>>>> cf7fba39a6d58e2117efe254bfd06b221d37b6eb


def console(*data):
    frappe.publish_realtime("toconsole", data, user=frappe.session.user)
