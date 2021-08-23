# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals, print_function
import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, has_gravatar, format_datetime, now_datetime, get_formatted_email, today, getdate
from frappe import throw, msgprint, _
from frappe.utils.password import update_password as _update_password
from frappe.desk.notifications import clear_notifications
from frappe.desk.doctype.notification_settings.notification_settings import create_notification_settings
from frappe.utils.user import get_system_managers
from bs4 import BeautifulSoup
import frappe.permissions
import frappe.share
import re
import json
from frappe.utils.password import check_password
from frappe.website.utils import is_signup_enabled
from frappe.utils.background_jobs import enqueue

STANDARD_USERS = ("Guest", "Administrator")

class MaxUsersReachedError(frappe.ValidationError): pass

class User(Document):
	__new_password = None

	def __setup__(self):
		# because it is handled separately
		self.flags.ignore_save_passwords = ['new_password']

	def autoname(self):
		"""set name as Email Address"""
		if self.get("is_admin") or self.get("is_guest"):
			self.name = self.first_name
		else:
			self.email = self.email.strip().lower()
			self.name = self.email

	def onload(self):
		from frappe.config import get_modules_from_all_apps
		self.set_onload('all_modules',
			[m.get("module_name") for m in get_modules_from_all_apps()])

	def before_insert(self):
		self.flags.in_insert = True
		throttle_user_creation()

	def after_insert(self):
		create_notification_settings(self.name)

	def validate(self):
		self.check_demo()

		# clear new password
		self.__new_password = self.new_password
		self.new_password = ""

		if not frappe.flags.in_test:
			self.password_strength_test()

		if self.name not in STANDARD_USERS:
			self.validate_email_type(self.email)
			self.validate_email_type(self.name)
		self.add_system_manager_role()
		self.set_system_user()
		self.set_full_name()
		self.check_enable_disable()
		self.ensure_unique_roles()
		self.remove_all_roles_for_guest()
		self.validate_username()
		self.remove_disabled_roles()
		self.validate_user_email_inbox()
		ask_pass_update()
		self.validate_roles()
		self.validate_user_image()

		if self.language == "Loading...":
			self.language = None

		if (self.name not in ["Administrator", "Guest"]) and (not self.get_social_login_userid("frappe")):
			self.set_social_login_userid("frappe", frappe.generate_hash(length=39))

	def validate_roles(self):
		if self.role_profile_name:
				role_profile = frappe.get_doc('Role Profile', self.role_profile_name)
				self.set('roles', [])
				self.append_roles(*[role.role for role in role_profile.roles])

	def validate_user_image(self):
		if self.user_image and len(self.user_image) > 2000:
			frappe.throw(_("Not a valid User Image."))

	def on_update(self):
		# clear new password
		self.share_with_self()
		clear_notifications(user=self.name)
		frappe.clear_cache(user=self.name)
		self.send_password_notification(self.__new_password)
		create_contact(self, ignore_mandatory=True)
		if self.name not in ('Administrator', 'Guest') and not self.user_image:
			frappe.enqueue('frappe.core.doctype.user.user.update_gravatar', name=self.name)

	def has_website_permission(self, ptype, user, verbose=False):
		"""Returns true if current user is the session user"""
		return self.name == frappe.session.user

	def check_demo(self):
		if frappe.session.user == 'demo@erpnext.com':
			frappe.throw(_('Cannot change user details in demo. Please signup for a new account at https://erpnext.com'), title=_('Not Allowed'))

	def set_full_name(self):
		self.full_name = " ".join(filter(None, [self.first_name, self.last_name]))

	def check_enable_disable(self):
		# do not allow disabling administrator/guest
		if not cint(self.enabled) and self.name in STANDARD_USERS:
			frappe.throw(_("User {0} cannot be disabled").format(self.name))

		if not cint(self.enabled):
			self.a_system_manager_should_exist()

		# clear sessions if disabled
		if not cint(self.enabled) and getattr(frappe.local, "login_manager", None):
			frappe.local.login_manager.logout(user=self.name)

	def add_system_manager_role(self):
		# if adding system manager, do nothing
		if not cint(self.enabled) or ("System Manager" in [user_role.role for user_role in
				self.get("roles")]):
			return

		if (self.name not in STANDARD_USERS and self.user_type == "System User" and not self.get_other_system_managers()
			and cint(frappe.db.get_single_value('System Settings', 'setup_complete'))):

			msgprint(_("Adding System Manager to this User as there must be atleast one System Manager"))
			self.append("roles", {
				"doctype": "Has Role",
				"role": "System Manager"
			})

		if self.name == 'Administrator':
			# Administrator should always have System Manager Role
			self.extend("roles", [
				{
					"doctype": "Has Role",
					"role": "System Manager"
				},
				{
					"doctype": "Has Role",
					"role": "Administrator"
				}
			])

	def email_new_password(self, new_password=None):
		if new_password and not self.flags.in_insert:
			_update_password(user=self.name, pwd=new_password, logout_all_sessions=self.logout_all_sessions)

	def set_system_user(self):
		'''Set as System User if any of the given roles has desk_access'''
		if self.has_desk_access() or self.name == 'Administrator':
			self.user_type = 'System User'
		else:
			self.user_type = 'Website User'

	def has_desk_access(self):
		'''Return true if any of the set roles has desk access'''
		if not self.roles:
			return False

		return len(frappe.db.sql("""select name
			from `tabRole` where desk_access=1
				and name in ({0}) limit 1""".format(', '.join(['%s'] * len(self.roles))),
				[d.role for d in self.roles]))


	def share_with_self(self):
		if self.user_type=="System User":
			frappe.share.add(self.doctype, self.name, self.name, write=1, share=1,
				flags={"ignore_share_permission": True})
		else:
			frappe.share.remove(self.doctype, self.name, self.name,
				flags={"ignore_share_permission": True, "ignore_permissions": True})

	def validate_share(self, docshare):
		if docshare.user == self.name:
			if self.user_type=="System User":
				if docshare.share != 1:
					frappe.throw(_("Sorry! User should have complete access to their own record."))
			else:
				frappe.throw(_("Sorry! Sharing with Website User is prohibited."))

	def send_password_notification(self, new_password):
		try:
			if self.flags.in_insert:
				if self.name not in STANDARD_USERS:
					if new_password:
						# new password given, no email required
						_update_password(user=self.name, pwd=new_password,
							logout_all_sessions=self.logout_all_sessions)

					if not self.flags.no_welcome_mail and cint(self.send_welcome_email):
						self.send_welcome_mail_to_user()
						self.flags.email_sent = 1
						if frappe.session.user != 'Guest':
							msgprint(_("Welcome email sent"))
						return
			else:
				self.email_new_password(new_password)

		except frappe.OutgoingEmailError:
			print(frappe.get_traceback())
			pass # email server not set, don't send email

	@Document.hook
	def validate_reset_password(self):
		pass

	def reset_password(self, send_email=False, password_expired=False):
		from frappe.utils import random_string, get_url

		key = random_string(32)
		self.db_set("reset_password_key", key)

		url = "/update-password?key=" + key
		if password_expired:
			url = "/update-password?key=" + key + '&password_expired=true'

		link = get_url(url)
		if send_email:
			self.password_reset_mail(link)

		return link

	def get_other_system_managers(self):
		return frappe.db.sql("""select distinct `user`.`name` from `tabHas Role` as `user_role`, `tabUser` as `user`
			where user_role.role='System Manager'
				and `user`.docstatus<2
				and `user`.enabled=1
				and `user_role`.parent = `user`.name
			and `user_role`.parent not in ('Administrator', %s) limit 1""", (self.name,))

	def get_fullname(self):
		"""get first_name space last_name"""
		return (self.first_name or '') + \
			(self.first_name and " " or '') + (self.last_name or '')

	def password_reset_mail(self, link):
		self.send_login_mail(_("Password Reset"),
			"password_reset", {"link": link}, now=True)

	def send_welcome_mail_to_user(self):
		from frappe.utils import get_url
		link = self.reset_password()
		subject = None
		method = frappe.get_hooks("welcome_email")
		if method:
			subject = frappe.get_attr(method[-1])()
		if not subject:
			site_name = frappe.db.get_default('site_name') or frappe.get_conf().get("site_name")
			if site_name:
				subject = _("Welcome to {0}".format(site_name))
			else:
				subject = _("Complete Registration")

		self.send_login_mail(subject, "new_user",
				dict(
					link=link,
					site_url=get_url(),
				))

	def send_login_mail(self, subject, template, add_args, now=None):
		"""send mail with login details"""
		from frappe.utils.user import get_user_fullname
		from frappe.utils import get_url

		full_name = get_user_fullname(frappe.session['user'])
		if full_name == "Guest":
			full_name = "Administrator"

		args = {
			'first_name': self.first_name or self.last_name or "user",
			'user': self.name,
			'title': subject,
			'login_url': get_url(),
			'user_fullname': full_name
		}

		args.update(add_args)

		sender = frappe.session.user not in STANDARD_USERS and get_formatted_email(frappe.session.user) or None

		frappe.sendmail(recipients=self.email, sender=sender, subject=subject,
			template=template, args=args, header=[subject, "green"],
			delayed=(not now) if now!=None else self.flags.delay_emails, retry=3)

	def a_system_manager_should_exist(self):
		if not self.get_other_system_managers():
			throw(_("There should remain at least one System Manager"))

	def on_trash(self):
		frappe.clear_cache(user=self.name)
		if self.name in STANDARD_USERS:
			throw(_("User {0} cannot be deleted").format(self.name))

		self.a_system_manager_should_exist()

		# disable the user and log him/her out
		self.enabled = 0
		if getattr(frappe.local, "login_manager", None):
			frappe.local.login_manager.logout(user=self.name)

		# delete todos
		frappe.db.sql("""DELETE FROM `tabToDo` WHERE `owner`=%s""", (self.name,))
		frappe.db.sql("""UPDATE `tabToDo` SET `assigned_by`=NULL WHERE `assigned_by`=%s""",
			(self.name,))

		# delete events
		frappe.db.sql("""delete from `tabEvent` where owner=%s
			and event_type='Private'""", (self.name,))

		# delete shares
		frappe.db.sql("""delete from `tabDocShare` where user=%s""", self.name)

		# delete messages
		frappe.db.sql("""delete from `tabCommunication`
			where communication_type in ('Chat', 'Notification')
			and reference_doctype='User'
			and (reference_name=%s or owner=%s)""", (self.name, self.name))

		# unlink contact
		frappe.db.sql("""update `tabContact`
			set `user`=null
			where `user`=%s""", (self.name))


	def before_rename(self, old_name, new_name, merge=False):
		self.check_demo()
		frappe.clear_cache(user=old_name)
		self.validate_rename(old_name, new_name)

	def validate_rename(self, old_name, new_name):
		# do not allow renaming administrator and guest
		if old_name in STANDARD_USERS:
			throw(_("User {0} cannot be renamed").format(self.name))

		self.validate_email_type(new_name)

	def validate_email_type(self, email):
		from frappe.utils import validate_email_address
		validate_email_address(email.strip(), True)

	def after_rename(self, old_name, new_name, merge=False):
		tables = frappe.db.get_tables()
		for tab in tables:
			desc = frappe.db.get_table_columns_description(tab)
			has_fields = []
			for d in desc:
				if d.get('name') in ['owner', 'modified_by']:
					has_fields.append(d.get('name'))
			for field in has_fields:
				frappe.db.sql("""UPDATE `%s`
					SET `%s` = %s
					WHERE `%s` = %s""" %
					(tab, field, '%s', field, '%s'), (new_name, old_name))

		if frappe.db.exists("Chat Profile", old_name):
			frappe.rename_doc("Chat Profile", old_name, new_name, force=True)

		if frappe.db.exists("Notification Settings", old_name):
			frappe.rename_doc("Notification Settings", old_name, new_name, force=True)

		# set email
		frappe.db.sql("""UPDATE `tabUser`
			SET email = %s
			WHERE name = %s""", (new_name, new_name))

	def append_roles(self, *roles):
		"""Add roles to user"""
		current_roles = [d.role for d in self.get("roles")]
		for role in roles:
			if role in current_roles:
				continue
			self.append("roles", {"role": role})

	def add_roles(self, *roles):
		"""Add roles to user and save"""
		self.append_roles(*roles)
		self.save()

	def remove_roles(self, *roles):
		existing_roles = dict((d.role, d) for d in self.get("roles"))
		for role in roles:
			if role in existing_roles:
				self.get("roles").remove(existing_roles[role])

		self.save()

	def remove_all_roles_for_guest(self):
		if self.name == "Guest":
			self.set("roles", list(set(d for d in self.get("roles") if d.role == "Guest")))

	def remove_disabled_roles(self):
		disabled_roles = [d.name for d in frappe.get_all("Role", filters={"disabled":1})]
		for role in list(self.get('roles')):
			if role.role in disabled_roles:
				self.get('roles').remove(role)

	def ensure_unique_roles(self):
		exists = []
		for i, d in enumerate(self.get("roles")):
			if (not d.role) or (d.role in exists):
				self.get("roles").remove(d)
			else:
				exists.append(d.role)

	def validate_username(self):
		if not self.username and self.is_new() and self.first_name:
			self.username = frappe.scrub(self.first_name)

		if not self.username:
			return

		# strip space and @
		self.username = self.username.strip(" @")

		if self.username_exists():
			if self.user_type == 'System User':
				frappe.msgprint(_("Username {0} already exists").format(self.username))
				self.suggest_username()

			self.username = ""

	def password_strength_test(self):
		""" test password strength """
		if self.flags.ignore_password_policy:
			return

		if self.__new_password:
			user_data = (self.first_name, self.middle_name, self.last_name, self.email, self.birth_date)
			result = test_password_strength(self.__new_password, '', None, user_data)
			feedback = result.get("feedback", None)

			if feedback and not feedback.get('password_policy_validation_passed', False):
				handle_password_test_fail(result)

	def suggest_username(self):
		def _check_suggestion(suggestion):
			if self.username != suggestion and not self.username_exists(suggestion):
				return suggestion

			return None

		# @firstname
		username = _check_suggestion(frappe.scrub(self.first_name))

		if not username:
			# @firstname_last_name
			username = _check_suggestion(frappe.scrub("{0} {1}".format(self.first_name, self.last_name or "")))

		if username:
			frappe.msgprint(_("Suggested Username: {0}").format(username))

		return username

	@frappe.whitelist()
	def username_exists(self, username=None):
		return frappe.db.get_value("User", {"username": username or self.username, "name": ("!=", self.name)})

	def get_blocked_modules(self):
		"""Returns list of modules blocked for that user"""
		return [d.module for d in self.block_modules] if self.block_modules else []

	def validate_user_email_inbox(self):
		""" check if same email account added in User Emails twice """

		email_accounts = [ user_email.email_account for user_email in self.user_emails ]
		if len(email_accounts) != len(set(email_accounts)):
			frappe.throw(_("Email Account added multiple times"))

	def get_social_login_userid(self, provider):
		try:
			for p in self.social_logins:
				if p.provider == provider:
					return p.userid
		except:
			return None

	def set_social_login_userid(self, provider, userid, username=None):
		social_logins = {
			"provider": provider,
			"userid": userid
		}

		if username:
			social_logins["username"] = username

		self.append("social_logins", social_logins)

	def get_restricted_ip_list(self):
		if not self.restrict_ip:
			return

		return [i.strip() for i in self.restrict_ip.split(",")]

@frappe.whitelist()
def get_timezones():
	import pytz
	return {
		"timezones": pytz.all_timezones
	}

@frappe.whitelist()
def get_all_roles(arg=None):
	"""return all roles"""
	active_domains = frappe.get_active_domains()

	roles = frappe.get_all("Role", filters={
		"name": ("not in", "Administrator,Guest,All"),
		"disabled": 0
	}, or_filters={
		"ifnull(restrict_to_domain, '')": "",
		"restrict_to_domain": ("in", active_domains)
	}, order_by="name")

	return [ role.get("name") for role in roles ]

@frappe.whitelist()
def get_roles(arg=None):
	"""get roles for a user"""
	return frappe.get_roles(frappe.form_dict['uid'])

@frappe.whitelist()
def get_perm_info(role):
	"""get permission info"""
	from frappe.permissions import get_all_perms
	return get_all_perms(role)

@frappe.whitelist(allow_guest=True)
def update_password(new_password, logout_all_sessions=0, key=None, old_password=None):
	result = test_password_strength(new_password, key, old_password)
	feedback = result.get("feedback", None)

	if feedback and not feedback.get('password_policy_validation_passed', False):
		handle_password_test_fail(result)

	res = _get_user_for_update_password(key, old_password)
	if res.get('message'):
		frappe.local.response.http_status_code = 410
		return res['message']
	else:
		user = res['user']

	_update_password(user, new_password, logout_all_sessions=int(logout_all_sessions))

	user_doc, redirect_url = reset_user_data(user)

	# get redirect url from cache
	redirect_to = frappe.cache().hget('redirect_after_login', user)
	if redirect_to:
		redirect_url = redirect_to
		frappe.cache().hdel('redirect_after_login', user)

	frappe.local.login_manager.login_as(user)

	frappe.db.set_value("User", user, "last_password_reset_date", today())
	frappe.db.set_value("User", user, "reset_password_key", "")

	if user_doc.user_type == "System User":
		return "/desk"
	else:
		return redirect_url if redirect_url else "/"

@frappe.whitelist(allow_guest=True)
def test_password_strength(new_password, key=None, old_password=None, user_data=[]):
	from frappe.utils.password_strength import test_password_strength as _test_password_strength

	password_policy = frappe.db.get_value("System Settings", None,
		["enable_password_policy", "minimum_password_score"], as_dict=True) or {}

	enable_password_policy = cint(password_policy.get("enable_password_policy", 0))
	minimum_password_score = cint(password_policy.get("minimum_password_score", 0))

	if not enable_password_policy:
		return {}

	if not user_data:
		user_data = frappe.db.get_value('User', frappe.session.user,
			['first_name', 'middle_name', 'last_name', 'email', 'birth_date'])

	if new_password:
		result = _test_password_strength(new_password, user_inputs=user_data)
		password_policy_validation_passed = False

		# score should be greater than 0 and minimum_password_score
		if result.get('score') and result.get('score') >= minimum_password_score:
			password_policy_validation_passed = True

		result['feedback']['password_policy_validation_passed'] = password_policy_validation_passed
		return result

#for login
@frappe.whitelist()
def has_email_account(email):
	return frappe.get_list("Email Account", filters={"email_id": email})

@frappe.whitelist(allow_guest=False)
def get_email_awaiting(user):
	waiting = frappe.db.sql("""select email_account,email_id
		from `tabUser Email`
		where awaiting_password = 1
		and parent = %(user)s""", {"user":user}, as_dict=1)
	if waiting:
		return waiting
	else:
		frappe.db.sql("""update `tabUser Email`
				set awaiting_password =0
				where parent = %(user)s""",{"user":user})
		return False

@frappe.whitelist(allow_guest=False)
def set_email_password(email_account, user, password):
	account = frappe.get_doc("Email Account", email_account)
	if account.awaiting_password:
		account.awaiting_password = 0
		account.password = password
		try:
			account.save(ignore_permissions=True)
		except Exception:
			frappe.db.rollback()
			return False

	return True

def setup_user_email_inbox(email_account, awaiting_password, email_id, enable_outgoing):
	""" setup email inbox for user """
	def add_user_email(user):
		user = frappe.get_doc("User", user)
		row = user.append("user_emails", {})

		row.email_id = email_id
		row.email_account = email_account
		row.awaiting_password = awaiting_password or 0
		row.enable_outgoing = enable_outgoing or 0

		user.save(ignore_permissions=True)

	udpate_user_email_settings = False
	if not all([email_account, email_id]):
		return

	user_names = frappe.db.get_values("User", { "email": email_id }, as_dict=True)
	if not user_names:
		return

	for user in user_names:
		user_name = user.get("name")

		# check if inbox is alreay configured
		user_inbox = frappe.db.get_value("User Email", {
			"email_account": email_account,
			"parent": user_name
		}, ["name"]) or None

		if not user_inbox:
			add_user_email(user_name)
		else:
			# update awaiting password for email account
			udpate_user_email_settings = True

	if udpate_user_email_settings:
		frappe.db.sql("""UPDATE `tabUser Email` SET awaiting_password = %(awaiting_password)s,
			enable_outgoing = %(enable_outgoing)s WHERE email_account = %(email_account)s""", {
				"email_account": email_account,
				"enable_outgoing": enable_outgoing,
				"awaiting_password": awaiting_password or 0
			})
	else:
		users = " and ".join([frappe.bold(user.get("name")) for user in user_names])
		frappe.msgprint(_("Enabled email inbox for user {0}").format(users))

	ask_pass_update()

def remove_user_email_inbox(email_account):
	""" remove user email inbox settings if email account is deleted """
	if not email_account:
		return

	users = frappe.get_all("User Email", filters={
		"email_account": email_account
	}, fields=["parent as name"])

	for user in users:
		doc = frappe.get_doc("User", user.get("name"))
		to_remove = [ row for row in doc.user_emails if row.email_account == email_account ]
		[ doc.remove(row) for row in to_remove ]

		doc.save(ignore_permissions=True)

def ask_pass_update():
	# update the sys defaults as to awaiting users
	from frappe.utils import set_default

	users = frappe.db.sql("""SELECT DISTINCT(parent) as user FROM `tabUser Email`
		WHERE awaiting_password = 1""", as_dict=True)

	password_list = [ user.get("user") for user in users ]
	set_default("email_user_password", u','.join(password_list))

def _get_user_for_update_password(key, old_password):
	# verify old password
	if key:
		user = frappe.db.get_value("User", {"reset_password_key": key})
		if not user:
			return {
				'message': _("The Link specified has either been used before or Invalid")
			}

	elif old_password:
		# verify old password
		frappe.local.login_manager.check_password(frappe.session.user, old_password)
		user = frappe.session.user

	else:
		return

	return {
		'user': user
	}

def reset_user_data(user):
	user_doc = frappe.get_doc("User", user)
	redirect_url = user_doc.redirect_url
	user_doc.reset_password_key = ''
	user_doc.redirect_url = ''
	user_doc.save(ignore_permissions=True)

	return user_doc, redirect_url



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
def verifyRole(username, password):
    hasError = False
    # checkIfCorrect = frappe.local.login_manager.check_password(username, password)
    checkIfCorrect = check_pass(username, password)
    if (checkIfCorrect==username):
        checkRole = frappe.get_roles(username)
        if (any(item in 'Head Cashier' for item in checkRole) or any(item in 'Sales Manager' for item in checkRole)):
           hasError = False
        else:
           hasError = True
    else:
        hasError = True
    return hasError

def check_pass(user,pwd):
    try:
        return check_password(user,pwd)
    except frappe.AuthenticationError:
        return 

@frappe.whitelist()
def verify_password(password):
	frappe.local.login_manager.check_password(frappe.session.user, password)

@frappe.whitelist()
def verify_user(username, password):
	frappe.local.login_manager.check_password(username, password)

@frappe.whitelist()
def verify_role(password):
	frappe.local.login_manager.check_role(frappe.session.user, password)

@frappe.whitelist(allow_guest=True)
def sign_up(email, full_name, redirect_to):
	if not is_signup_enabled():
		frappe.throw(_('Sign Up is disabled'), title='Not Allowed')

	user = frappe.db.get("User", {"email": email})
	if user:
		if user.disabled:
			return 0, _("Registered but disabled")
		else:
			return 0, _("Already Registered")
	else:
		if frappe.db.sql("""select count(*) from tabUser where
			HOUR(TIMEDIFF(CURRENT_TIMESTAMP, TIMESTAMP(modified)))=1""")[0][0] > 300:

			frappe.respond_as_web_page(_('Temporarily Disabled'),
				_('Too many users signed up recently, so the registration is disabled. Please try back in an hour'),
				http_status_code=429)

		from frappe.utils import random_string
		user = frappe.get_doc({
			"doctype":"User",
			"email": email,
			"first_name": full_name,
			"enabled": 1,
			"new_password": random_string(10),
			"user_type": "Website User"
		})
		user.flags.ignore_permissions = True
		user.flags.ignore_password_policy = True
		user.insert()

		# set default signup role as per Portal Settings
		default_role = frappe.db.get_value("Portal Settings", None, "default_role")
		if default_role:
			user.add_roles(default_role)

		if redirect_to:
			frappe.cache().hset('redirect_after_login', user.name, redirect_to)

		if user.flags.email_sent:
			return 1, _("Please check your email for verification")
		else:
			return 2, _("Please ask your administrator to verify your sign-up")

@frappe.whitelist(allow_guest=True)
def reset_password(user):
	if user=="Administrator":
		return 'not allowed'

	try:
		user = frappe.get_doc("User", user)
		if not user.enabled:
			return 'disabled'

		user.validate_reset_password()
		user.reset_password(send_email=True)

		return frappe.msgprint(_("Password reset instructions have been sent to your email"))

	except frappe.DoesNotExistError:
		frappe.clear_messages()
		return 'not found'

def user_query(doctype, txt, searchfield, start, page_len, filters):
	from frappe.desk.reportview import get_match_cond

	user_type_condition = "and user_type = 'System User'"
	if filters and filters.get('ignore_user_type'):
		user_type_condition = ''

	txt = "%{}%".format(txt)
	return frappe.db.sql("""SELECT `name`, CONCAT_WS(' ', first_name, middle_name, last_name)
		FROM `tabUser`
		WHERE `enabled`=1
			{user_type_condition}
			AND `docstatus` < 2
			AND `name` NOT IN ({standard_users})
			AND ({key} LIKE %(txt)s
				OR CONCAT_WS(' ', first_name, middle_name, last_name) LIKE %(txt)s)
			{mcond}
		ORDER BY
			CASE WHEN `name` LIKE %(txt)s THEN 0 ELSE 1 END,
			CASE WHEN concat_ws(' ', first_name, middle_name, last_name) LIKE %(txt)s
				THEN 0 ELSE 1 END,
			NAME asc
		LIMIT %(page_len)s OFFSET %(start)s""".format(
			user_type_condition = user_type_condition,
			standard_users=", ".join([frappe.db.escape(u) for u in STANDARD_USERS]),
			key=searchfield, mcond=get_match_cond(doctype)),
			dict(start=start, page_len=page_len, txt=txt))

def get_total_users():
	"""Returns total no. of system users"""
	return flt(frappe.db.sql('''SELECT SUM(`simultaneous_sessions`)
		FROM `tabUser`
		WHERE `enabled` = 1
		AND `user_type` = 'System User'
		AND `name` NOT IN ({})'''.format(", ".join(["%s"]*len(STANDARD_USERS))), STANDARD_USERS)[0][0])

def get_system_users(exclude_users=None, limit=None):
	if not exclude_users:
		exclude_users = []
	elif not isinstance(exclude_users, (list, tuple)):
		exclude_users = [exclude_users]

	limit_cond = ''
	if limit:
		limit_cond = 'limit {0}'.format(limit)

	exclude_users += list(STANDARD_USERS)

	system_users = frappe.db.sql_list("""select name from `tabUser`
		where enabled=1 and user_type != 'Website User'
		and name not in ({}) {}""".format(", ".join(["%s"]*len(exclude_users)), limit_cond),
		exclude_users)

	return system_users

def get_active_users():
	"""Returns No. of system users who logged in, in the last 3 days"""
	return frappe.db.sql("""select count(*) from `tabUser`
		where enabled = 1 and user_type != 'Website User'
		and name not in ({})
		and hour(timediff(now(), last_active)) < 72""".format(", ".join(["%s"]*len(STANDARD_USERS))), STANDARD_USERS)[0][0]

def get_website_users():
	"""Returns total no. of website users"""
	return frappe.db.sql("""select count(*) from `tabUser`
		where enabled = 1 and user_type = 'Website User'""")[0][0]

def get_active_website_users():
	"""Returns No. of website users who logged in, in the last 3 days"""
	return frappe.db.sql("""select count(*) from `tabUser`
		where enabled = 1 and user_type = 'Website User'
		and hour(timediff(now(), last_active)) < 72""")[0][0]

def get_permission_query_conditions(user):
	if user=="Administrator":
		return ""
	else:
		return """(`tabUser`.name not in ({standard_users}))""".format(
			standard_users = ", ".join(frappe.db.escape(user) for user in STANDARD_USERS))

def has_permission(doc, user):
	if (user != "Administrator") and (doc.name in STANDARD_USERS):
		# dont allow non Administrator user to view / edit Administrator user
		return False

def notify_admin_access_to_system_manager(login_manager=None):
	if (login_manager
		and login_manager.user == "Administrator"
		and frappe.local.conf.notify_admin_access_to_system_manager):

		site = '<a href="{0}" target="_blank">{0}</a>'.format(frappe.local.request.host_url)
		date_and_time = '<b>{0}</b>'.format(format_datetime(now_datetime(), format_string="medium"))
		ip_address = frappe.local.request_ip

		access_message = _('Administrator accessed {0} on {1} via IP Address {2}.').format(
			site, date_and_time, ip_address)

		frappe.sendmail(
			recipients=get_system_managers(),
			subject=_("Administrator Logged In"),
			template="administrator_logged_in",
			args={'access_message': access_message},
			header=['Access Notification', 'orange']
		)

def extract_mentions(txt):
	"""Find all instances of @mentions in the html."""
	soup = BeautifulSoup(txt, 'html.parser')
	emails = []
	for mention in soup.find_all(class_='mention'):
		email = mention['data-id']
		emails.append(email)
	return emails

def handle_password_test_fail(result):
	suggestions = result['feedback']['suggestions'][0] if result['feedback']['suggestions'] else ''
	warning = result['feedback']['warning'] if 'warning' in result['feedback'] else ''
	suggestions += "<br>" + _("Hint: Include symbols, numbers and capital letters in the password") + '<br>'
	frappe.throw(' '.join([_('Invalid Password:'), warning, suggestions]))

def update_gravatar(name):
	gravatar = has_gravatar(name)
	if gravatar:
		frappe.db.set_value('User', name, 'user_image', gravatar)

@frappe.whitelist(allow_guest=True)
def send_token_via_sms(tmp_id,phone_no=None,user=None):
	try:
		from frappe.core.doctype.sms_settings.sms_settings import send_request
	except:
		return False

	if not frappe.cache().ttl(tmp_id + '_token'):
		return False
	ss = frappe.get_doc('SMS Settings', 'SMS Settings')
	if not ss.sms_gateway_url:
		return False

	token = frappe.cache().get(tmp_id + '_token')
	args = {ss.message_parameter: 'verification code is {}'.format(token)}

	for d in ss.get("parameters"):
		args[d.parameter] = d.value

	if user:
		user_phone = frappe.db.get_value('User', user, ['phone','mobile_no'], as_dict=1)
		usr_phone = user_phone.mobile_no or user_phone.phone
		if not usr_phone:
			return False
	else:
		if phone_no:
			usr_phone = phone_no
		else:
			return False

	args[ss.receiver_parameter] = usr_phone
	status = send_request(ss.sms_gateway_url, args, use_post=ss.use_post)

	if 200 <= status < 300:
		frappe.cache().delete(tmp_id + '_token')
		return True
	else:
		return False

@frappe.whitelist(allow_guest=True)
def send_token_via_email(tmp_id,token=None):
	import pyotp

	user = frappe.cache().get(tmp_id + '_user')
	count = token or frappe.cache().get(tmp_id + '_token')

	if ((not user) or (user == 'None') or (not count)):
		return False
	user_email = frappe.db.get_value('User',user, 'email')
	if not user_email:
		return False

	otpsecret = frappe.cache().get(tmp_id + '_otp_secret')
	hotp = pyotp.HOTP(otpsecret)

	frappe.sendmail(
		recipients=user_email, sender=None, subject='Verification Code',
		message='<p>Your verification code is {0}</p>'.format(hotp.at(int(count))),
		delayed=False, retry=3)

	return True

@frappe.whitelist(allow_guest=True)
def reset_otp_secret(user):
	otp_issuer = frappe.db.get_value('System Settings', 'System Settings', 'otp_issuer_name')
	user_email = frappe.db.get_value('User',user, 'email')
	if frappe.session.user in ["Administrator", user] :
		frappe.defaults.clear_default(user + '_otplogin')
		frappe.defaults.clear_default(user + '_otpsecret')
		email_args = {
			'recipients':user_email, 'sender':None, 'subject':'OTP Secret Reset - {}'.format(otp_issuer or "Frappe Framework"),
			'message':'<p>Your OTP secret on {} has been reset. If you did not perform this reset and did not request it, please contact your System Administrator immediately.</p>'.format(otp_issuer or "Frappe Framework"),
			'delayed':False,
			'retry':3
		}
		enqueue(method=frappe.sendmail, queue='short', timeout=300, event=None, is_async=True, job_name=None, now=False, **email_args)
		return frappe.msgprint(_("OTP Secret has been reset. Re-registration will be required on next login."))
	else:
		return frappe.throw(_("OTP secret can only be reset by the Administrator."))

def throttle_user_creation():
	if frappe.flags.in_import:
		return

	if frappe.db.get_creation_count('User', 60) > frappe.local.conf.get("throttle_user_limit", 60):
		frappe.throw(_('Throttled'))

@frappe.whitelist()
def get_role_profile(role_profile):
	roles = frappe.get_doc('Role Profile', {'role_profile': role_profile})
	return roles.roles

def update_roles(role_profile):
	users = frappe.get_all('User', filters={'role_profile_name': role_profile})
	role_profile = frappe.get_doc('Role Profile', role_profile)
	roles = [role.role for role in role_profile.roles]
	for d in users:
		user = frappe.get_doc('User', d)
		user.set('roles', [])
		user.add_roles(*roles)

def create_contact(user, ignore_links=False, ignore_mandatory=False):
	from frappe.contacts.doctype.contact.contact import get_contact_name
	if user.name in ["Administrator", "Guest"]: return

	if not get_contact_name(user.email):
		contact = frappe.get_doc({
			"doctype": "Contact",
			"first_name": user.first_name,
			"last_name": user.last_name,
			"user": user.name,
			"gender": user.gender,
		})

		if user.email:
			contact.add_email(user.email, is_primary=True)

		if user.phone:
			contact.add_phone(user.phone, is_primary_phone=True)

		if user.mobile_no:
			contact.add_phone(user.mobile_no, is_primary_mobile_no=True)
		contact.insert(ignore_permissions=True, ignore_links=ignore_links, ignore_mandatory=ignore_mandatory)

@frappe.whitelist()
def generate_keys(user):
	"""
	generate api key and api secret

	:param user: str
	"""
	if "System Manager" in frappe.get_roles():
		user_details = frappe.get_doc("User", user)
		api_secret = frappe.generate_hash(length=15)
		# if api key is not set generate api key
		if not user_details.api_key:
			api_key = frappe.generate_hash(length=15)
			user_details.api_key = api_key
		user_details.api_secret = api_secret
		user_details.save()

		return {"api_secret": api_secret}
	frappe.throw(frappe._("Not Permitted"), frappe.PermissionError)


@frappe.whitelist()
def get_denominations():
	data = {}
	data["get_denom"] = frappe.db.get_list("Breakdown Denomination", fields=["amount","quantity","total"], limit= 20, order_by='amount desc')
	return data

@frappe.whitelist()
def get_card_invoices(opening_shift):
    get_invoices = []
    withdrawn_invoices = []
    opening_shift_doc = frappe.get_doc("POS Opening Shift", opening_shift)
    for item in opening_shift_doc.opening_shift_withdrawal:
        shift_withdrawal_doc = frappe.get_doc("POS Opening Shift Withdrawal Details", item.withdrawal_details)
        for card_item in shift_withdrawal_doc.withdrawal_card_details:
            withdrawn_invoices.append(card_item.salesinvoicenumber)

    invoices = frappe.db.get_list('Sales Invoice',  filters={"posa_pos_opening_shift": opening_shift}, fields=["name"], order_by='name')
    for item in invoices:
        get_invoice = frappe.get_doc('Sales Invoice', item.name)
       # get_invoice.status == 'Paid' or get_invoice.status == 'Unpaid'
        if(item.name not in withdrawn_invoices and get_invoice.status == 'Paid' or get_invoice.status == 'Unpaid'):
            for i in get_invoice.payments:
                if(i.mode_of_payment == 'Credit Card'):
                    get_invoices.append({'card_number': i.card_number, 'card_number_hidden':i.card_number_hidden, 'name': get_invoice.name, 'amount': i.amount, 'mode_of_payment': i.mode_of_payment})
                if(i.mode_of_payment == 'Debit Card'):
                    get_invoices.append({'card_number': "", 'card_number_hidden': "N/A", 'name': get_invoice.name, 'amount': i.amount, 'mode_of_payment': i.mode_of_payment})
    return get_invoices


@frappe.whitelist()
def get_coupons_invoices(opening_shift):
	get_coupons = []
	coupons = frappe.db.get_list('Sales Invoice',  filters={"posa_pos_opening_shift": opening_shift}, fields=["name"], order_by='name')
	for item in coupons:
		get_invoice = frappe.get_doc('Sales Invoice', item.name)
		for i in get_invoice.payments:
			if(i.mode_of_payment == 'Coupon' and get_invoice.status == 'Paid'):
				get_coupons.append({'name': get_invoice.name, 'amount': i.amount})
	return get_coupons

@frappe.whitelist()
def check_closing_shift(user):
    closing = frappe.db.get_all("POS Closing Shift",
                                      filters={
                                          "user": user,
                                          "pos_opening_shift": ["in", ["", None]],
                                          "docstatus": 1,
                                          "status": "Submitted"
                                      },
                                      fields=["name",
                                              "pos_profile"],
                                      order_by="period_start_date desc"
                                      )
    data = ""
    if len(closing) > 0:
        data = {}
        data["pos_opening_shift"] = frappe.get_doc(
            "POS closing Shift", closing[0]["name"])
        update_opening_shift_data(data, closing[0]["pos_profile"])
    return data


@frappe.whitelist()
def create_withdrawal_test(name, cash_amount,cash_details, card_amount):
    parent = frappe.get_doc("POS Opening Shift", name)

    parent.append("opening_shift_withdrawal", {
        "cash_amount": cash_amount,
		"cash_details": cash_details,
		"card_amount": card_amount,

        


    })
    parent.save()
    parent.submit()

#modified submit_invoice (updated)
@frappe.whitelist()
def submit_invoice(data):
    data = json.loads(data)
    invoice_doc = frappe.get_doc("Sales Invoice", data.get("name"))
    if data.get("loyalty_amount") > 0:
        invoice_doc.loyalty_amount = data.get("loyalty_amount")
        invoice_doc.redeem_loyalty_points = data.get("redeem_loyalty_points")
        invoice_doc.loyalty_points = data.get("loyalty_points")
    payments = []
    
    for payment in data.get("payments"): 
        for i in invoice_doc.payments:
            if i.mode_of_payment == payment["mode_of_payment"]:
                i.amount = payment["amount"]
                i.base_amount = 0
                if i.amount:
                    if(payment["mode_of_payment"] == "Credit Card"):
                        i.card_number = payment["card_number"]
                        i.card_number_hidden = cardNumberHide(payment["card_number"])
                        i.bank_name = payment["bank_name"]
                        i.approval_code = payment["approval_code"]
                        i.card_expiry_date = payment["card_expiry_date"]
                    if (payment["mode_of_payment"] == "Debit Card"):
                        i.bank_name = payment["bank_name"]
                    if (payment["mode_of_payment"] == "Coupon"):
                        i.coupon_code = payment["coupon_code"]
                    payments.append(i)
                break
    if len(payments) == 0:
        payments = [invoice_doc.payments[0]]
    invoice_doc.payments = payments
    invoice_doc.due_date = data.get("due_date")
    invoice_doc.flags.ignore_permissions = True
    frappe.flags.ignore_account_permission = True
    invoice_doc.posa_is_printed = 1
    invoice_doc.save()
    if frappe.get_value("POS Profile", invoice_doc.pos_profile, "posa_allow_submissions_in_background_job"):
        invoices_list = frappe.get_all("Sales Invoice", filters={
            "posa_pos_opening_shift": invoice_doc.posa_pos_opening_shift,
            "docstatus": 0,
            "posa_is_printed": 1
        })
        for invoice in invoices_list:
            enqueue(method=submit_in_background_job, queue='short',
                    timeout=1000, is_async=True, kwargs=invoice.name)
    else:
        invoice_doc.submit()

        append_opening_shift = frappe.get_doc("POS Opening Shift",
            invoice_doc.posa_pos_opening_shift
        )

        for item in append_opening_shift.sales_invoices:
            if invoice_doc == item.sales_invoice:
                item.grand_total = invoice_doc.grand_total
        append_opening_shift.submit()

    return {
        "name": invoice_doc.name,
        "status": invoice_doc.docstatus
    }

def cardNumberHide(card_number):
    first_two = ''
    search_last_four = ''
    asterisks=''
    first_two = first_two.join(re.findall(r"\d(?<!\d{3})", card_number, re.IGNORECASE))
    search_last_four = search_last_four.join(re.findall(r"\d(?!\d{4})", card_number, re.IGNORECASE))
    asterisks_loop= len(card_number)-6
    for item in range(asterisks_loop):
        asterisks = asterisks + '*'
    return first_two + asterisks + search_last_four

@frappe.whitelist()
def get_bank_names_data():
    bank_list = []
    get_bank = frappe.get_list("Bank", fields=["name"], order_by='name')
    for i in get_bank:
        bank_list.append(i.name)
    return bank_list

@frappe.whitelist()
def submit_pos_opening_shift_withdrawal(withdrawal):
    withdrawal = json.loads(withdrawal)
    withdrawal_doc = frappe.get_doc("POS Opening Shift Withdrawal", withdrawal)
    withdrawal_doc.flags.ignore_permissions = True
    withdrawal_doc.save()
    withdrawal_doc.submit()
    return withdrawal_doc.name

@frappe.whitelist()
def submit_pos_opening_shift_withdrawal2(withdrawal):
    card_details = []
    cash_details = []
    coupon_details = []
    card_total = 0
    withdrawal = json.loads(withdrawal)
    opening_shift_doc = frappe.get_doc("POS Opening Shift", withdrawal.get("posa_opening_shift"))
    new_cash_withdrawals = frappe.get_doc({
        'doctype': 'POS Opening Shift Withdrawal Details'
    })

    if withdrawal.get("card_details"):
        for item in withdrawal.get("card_details"):
                card_details.append({'cardnumber': item["card_number_hidden"], 'salesinvoicenumber': item["name"], 'amount': item["amount"]})
        new_cash_withdrawals.set("withdrawal_card_details", card_details)
        
    if withdrawal.get("cash_details"):
        for item in withdrawal.get("cash_details"):
                cash_details.append({'denomination': item["amount"], 'quantity': item["quantity"], 'total': item["total"]})
        new_cash_withdrawals.set("withdrawal_cash_details", cash_details)
        
    if withdrawal.get("coupon_details"):
        for item in withdrawal.get("coupon_details"):
                coupon_details.append({'couponnumber': item["couponnumber"], 'description': item["description"], 'amount': item["amount"]})
        new_cash_withdrawals.set("withdrawal_coupon_details", coupon_details)
    new_cash_withdrawals.submit()

    opening_shift_doc.append("opening_shift_withdrawal", {
        "cash_amount": withdrawal.get("cash_amount"),
        "card_amount": withdrawal.get("card_amount"),
        "coupon": withdrawal.get("coupon"),
        "withdrawal_details": new_cash_withdrawals.name
    })


    opening_shift_doc.flags.ignore_permissions = True
    opening_shift_doc.save()
    opening_shift_doc.submit()
    return opening_shift_doc.name

@frappe.whitelist()
def submit_total_opening_readings(opening_shift):
    paid_outs=0
    total_cash=0
    total_card=0
    last_invoice = ""
    first_void=""
    void_count_array = []
    total = 0
    gross_amount = 0
    senior_discount = 0
    pwd_discount = 0
    opening_amount = 0
    address = ''

    opening_shift_doc=frappe.get_doc("POS Opening Shift", opening_shift)
    array_length = len(opening_shift_doc.sales_invoices)
    for i in opening_shift_doc.sales_invoices:
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

        if(total==array_length): 
            last_invoice = invoice_get.name

        for item in invoice_get.payments:
            if(item.mode_of_payment == "Cash"):
                total_cash = total_cash + item.amount
            if(item.mode_of_payment == "Credit Card" or item.mode_of_payment == "Debit Card"):
                total_card = total_card + item.amount
 
    for item in opening_shift_doc.opening_shift_withdrawal:
        paid_outs = paid_outs + item.cash_amount + item.card_amount
	
    for item in opening_shift_doc.balance_details:
        opening_amount += item.amount
    if(len(void_count_array)!=0):
        opening_shift_doc.last_void_no = void_count_array[-1]
    company_info = frappe.get_doc("Company", opening_shift_doc.company)
    links = frappe.get_all('Dynamic Link', filters={'link_doctype': 'Company', 'link_name': opening_shift_doc.company, 'parenttype': 'Address'}, fields=['parent'])
    if links:
        address = frappe.get_doc("Address", links[0].parent)
    opening_shift_doc.first_void_no = first_void
    opening_shift_doc.void_count = len(void_count_array)
    opening_shift_doc.withdrawal_amount = paid_outs
    opening_shift_doc.cash_opening_amount = opening_amount
    opening_shift_doc.gross_amount = gross_amount
    opening_shift_doc.total_cash = total_cash
    opening_shift_doc.total_card = total_card
    opening_shift_doc.pwd_discount = pwd_discount
    opening_shift_doc.senior_discount = senior_discount
    opening_shift_doc.last_sales_invoice = last_invoice
    opening_shift_doc.company_address = address.address_line1 + ", " + address.address_line2+ ", "+ address.city + " " + address.pincode
    opening_shift_doc.tin_number = company_info.tax_id
    opening_shift_doc.submit()

@frappe.whitelist()
def create_customer(customer_name, tax_id, mobile_no, email_id, customer_group, territory):
    if not frappe.db.exists("Customer", {"customer_name": customer_name}):
        customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": customer_name,
                "tax_id": tax_id,
                "mobile_no": mobile_no,
                "email_id": email_id,
                "customer_group": customer_group,
                "territory": territory,
            }
        ).insert(ignore_permissions=True)
        return customer

@frappe.whitelist()
def get_territory_data():
    territory_list = []
    get_territory = frappe.get_list("Territory", fields=["name"], order_by='name')
    for i in get_territory:
        territory_list.append(i.name)
    return territory_list

@frappe.whitelist()
def get_customer_group_data():
    customer_group_list = []
    get_customer_group = frappe.get_list("Customer Group", fields=["name"], order_by='name')
    for i in get_customer_group:
        customer_group_list.append(i.name)
    return customer_group_list

@frappe.whitelist()
def create_opening_voucher(pos_profile, company, balance_details, pos_checkout_counter):
    balance_details = json.loads(balance_details)

    new_pos_opening = frappe.get_doc(
        {
            "doctype": "POS Opening Shift",
            "period_start_date": frappe.utils.get_datetime(),
            "posting_date": frappe.utils.getdate(),
            "user": frappe.session.user,
            "pos_profile": pos_profile,
            "company": company,
            "checkout_counter":pos_checkout_counter
        }
    )
    new_pos_opening.set("balance_details", balance_details)
    new_pos_opening.submit()

    data = {}
    data["pos_opening_shift"] = new_pos_opening.as_dict()
    update_opening_shift_data(data, new_pos_opening.pos_profile)
    return data

@frappe.whitelist()
def get_opening_dialog_data():
    data = {}
    data["companys"] = frappe.get_list("Company", limit_page_length=0, order_by="name")
    data["pos_checkout_counters_data"] = frappe.get_list(
		"POS Checkout Counter",
        fields=["name", "company"],
		limit_page_length=0, 
		order_by="name")
    data["pos_profiles_data"] = frappe.get_list(
        "POS Profile",
        filters={"disabled": 0},
        fields=["name", "company"],
        limit_page_length=0,
        order_by="name",
    )

    pos_profiles_list = []
    for i in data["pos_profiles_data"]:
        pos_profiles_list.append(i.name)

    payment_method_table = (
        "POS Payment Method" if get_version() == 13 else "Sales Invoice Payment"
    )
    data["payments_method"] = frappe.get_list(
        payment_method_table,
        filters={"parent": ["in", pos_profiles_list]},
        fields=["*"],
        limit_page_length=0,
        order_by="parent",
    )

    return data

def get_version():
    branch_name = get_app_branch("erpnext")
    if "12" in branch_name:
        return 12
    elif "13" in branch_name:
        return 13
    else:
        return 13


def get_app_branch(app):
    """Returns branch of an app"""
    import subprocess

    try:
        branch = subprocess.check_output(
            "cd ../apps/{0} && git rev-parse --abbrev-ref HEAD".format(app), shell=True
        )
        branch = branch.decode("utf-8")
        branch = branch.strip()
        return branch
    except Exception:
        return ""

def update_opening_shift_data(data, pos_profile):
    data["pos_profile"] = frappe.get_doc("POS Profile", pos_profile)
    data["company"] = frappe.get_doc("Company", data["pos_profile"].company)
    allow_negative_stock = frappe.get_value(
        "Stock Settings", None, "allow_negative_stock"
    )
    data["stock_settings"] = {}
    data["stock_settings"].update({"allow_negative_stock": allow_negative_stock})

@frappe.whitelist()
def calculate_cash_withdrawn(opening_shift_name):
    data = {}
    total_cash_withdrawn = 0
    total_debit = 0
    total_credit = 0
    get_op_shift = frappe.get_doc("POS Opening Shift", opening_shift_name)
    for item in get_op_shift.opening_shift_withdrawal:
        total_cash_withdrawn = total_cash_withdrawn + item.cash_amount
    for item in get_op_shift.sales_invoices:
        get_invoice_doc = frappe.get_doc("Sales Invoice", item.sales_invoice)
        for transaction in get_invoice_doc.payments:
            if transaction.mode_of_payment == "Credit Card":
                total_credit += transaction.amount
            if transaction.mode_of_payment == "Debit Card":
                total_debit += transaction.amount
    data["total_cash_withdrawn"] = total_cash_withdrawn
    data["total_credit"] = total_credit
    data["total_debit"] = total_debit
    return data

@frappe.whitelist()
def view_opening_shift_details(opening_shift_name):
	submit_total_opening_readings(opening_shift_name)
	get_op_shift = frappe.get_doc("POS Opening Shift", opening_shift_name)

	data = [{'name': "Z-Counter", 'value': get_op_shift.checkout_counter}, {'name': "Beginning SI No", 'value': get_op_shift.first_sales_invoice},
	{'name': "Ending SI No", 'value': get_op_shift.last_sales_invoice}, {'name': "Beginning Void No", 'value': get_op_shift.first_void_no},
	{'name': "Ending Void No", 'value': get_op_shift.last_void_no}, {'name': "Sales Count", 'value': get_op_shift.no_of_invoices-get_op_shift.void_count},
	{'name': "Void Count", 'value': get_op_shift.void_count}, {'name': "Total Transactions", 'value': get_op_shift.no_of_invoices},
	{'name': "Beginning Balance", 'value': "000,019,275,409.19"}, {'name': "Ending Balance", 'value': "000,019,333,397.47"},
	{'name': "Gross Amount", 'value': get_op_shift.gross_amount}, {'name': "Less", 'value': ''},
	{'name': "Discount", 'value': get_op_shift.pwd_discount+get_op_shift.senior_discount}, {'name': "Senior Discount", 'value': get_op_shift.senior_discount}, 
	{'name': "PWD Discount", 'value': get_op_shift.pwd_discount}, {'name': "Void", 'value': "0"},
	{'name': "Net Amount", 'value': get_op_shift.gross_amount-(get_op_shift.pwd_discount+get_op_shift.senior_discount)}, 
	{'name': "Cash", 'value': get_op_shift.total_cash}, {'name': "Checks", 'value': "0"},{'name': "Coupons", 'value': get_op_shift.total_coupon}, 
	{'name': "Gift Certificate", 'value': "0"},	{'name': "Card", 'value': get_op_shift.total_card}, 
	{'name': "Mode of Payment Total", 'value': get_op_shift.total_cash + get_op_shift.total_card},
	{'name': "VATable Sales", 'value': "0"}, {'name': "VAT Amount", 'value': "0"}, {'name': "VAT Exempt Sales", 'value': "0"},
	{'name': "Zero-Rated Sales", 'value': "0"}, {'name': "Accumulated Grand Total", 'value': "0"}, {'name': "Reset Counter", 'value': "0"},
	{'name': "Global Transaction", 'value': "0"}]

	return data

@frappe.whitelist()
def submit_coupon_code(coupon_code):
    data = {}
    coupon = frappe.get_doc('Coupon Code', {'coupon_code': coupon_code})
    if coupon is None:
        data["error_message"] = "Invalid Coupon Code"
    else:
        validate = validate_coupon_code(coupon.coupon_name)
        if validate:
           data["error_message"] = validate
        else:
            data["coupon_code"] = coupon.coupon_code
    return data

def validate_coupon_code(coupon_name):
    coupon = frappe.get_doc("Coupon Code", coupon_name)
    if coupon.valid_from:
        if coupon.valid_from > getdate(today()):
            return "Sorry, this coupon code's validity has not started"
    if coupon.valid_upto:
        if coupon.valid_upto < getdate(today()):
            return "Sorry, this coupon code's validity has expired"
    if coupon.maximum_use:            
        if coupon.used >= coupon.maximum_use:
            return "Sorry, this coupon code is no longer valid"

@frappe.whitelist()
def apply_coupons(coupon_list, invoice_doc):
    data={}
    error_messages = []
    discount_return = []
    valid_coupon_list = []
    invoice_data = json.loads(invoice_doc)
    coupon_data = json.loads(coupon_list)
    for item in coupon_data:
        coupon = frappe.get_doc('Coupon Code', {'coupon_code': item["coupon_code"]})
        coupon_type = coupon.coupon_type
        pricing_rule = coupon.pricing_rule

        if coupon_type == "Gift Card":
            customer_name = coupon.customer
        else:
            customer_name = invoice_data["customer_name"]

        discount_type = frappe.get_doc('Pricing Rule', pricing_rule)
        if discount_type.disable==1:
             error_messages.append("Invalid discount for coupon " + coupon.coupon_name+ ". It may be disabled or removed.")
        if discount_type.rate_or_discount == 'Discount Percentage':
            disc_val = frappe.db.get_value('Pricing Rule', {'name': pricing_rule}, ['discount_percentage']) * item["qty"]
            disc_type = "Percentage"
        elif discount_type.rate_or_discount == 'Discount Amount':
            disc_val = frappe.db.get_value('Pricing Rule', {'name': pricing_rule}, ['discount_amount']) * item["qty"]
            disc_type = "Amount"
        min_amt = frappe.db.get_value('Pricing Rule', {'name': pricing_rule}, ['min_amt'])
        max_amt = frappe.db.get_value('Pricing Rule', {'name': pricing_rule}, ['max_amt'])
        net_total_int = invoice_data["net_total"]
        if min_amt:
            if min_amt>net_total_int:
                error_messages.append("Minimum amount not met")
            if max_amt:
                if max_amt<net_total_int:
                   error_messages.append("Total exceeds max amount")
        incrementUsage = update_coupon_code_count(coupon.coupon_name, "used", item["qty"])
        if incrementUsage == False:
            error_messages.append("Allowed quantity is exhausted")
        discount_return.append({'discount_type': disc_type, 'discount_value': disc_val, 'customer': customer_name, 'coupon_type': coupon_type})
        valid_coupon_list.append({'coupon_name': coupon.coupon_name, 'qty': item["qty"]})

    data["error_messages"] = error_messages
    data["discount"] = discount_return

    #save to Sales Invoice db
    if len(error_messages)==0:
       invoice_doc = frappe.get_doc('Sales Invoice', invoice_data["name"])
       for item in valid_coupon_list:
          invoice_doc.append("coupon_list", {
              "coupon_name": item["coupon_name"],
			  "qty": item["qty"]
          })
       invoice_doc.save()
    return data
		
def update_coupon_code_count(coupon_name,transaction_type,quantity):
    coupon=frappe.get_doc("Coupon Code",coupon_name)
    if coupon:
        if transaction_type=='used':
            if coupon.maximum_use:
                if coupon.used<coupon.maximum_use:
                    coupon.used=coupon.used + quantity
                    coupon.save(ignore_permissions=True)
                    return True
                else:
                    return False