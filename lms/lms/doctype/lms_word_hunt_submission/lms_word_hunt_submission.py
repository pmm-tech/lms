# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.desk.doctype.notification_log.notification_log import make_notification_logs
from frappe.model.document import Document
from frappe.utils import cint


class LMSWordHuntSubmission(Document):
	def validate(self):
		self.validate_if_max_attempts_exceeded()
		self.validate_marks()
		self.set_percentage()

	def on_update(self):
		self.notify_member()

	def validate_if_max_attempts_exceeded(self):
		max_attempts = frappe.db.get_value("LMS Word Hunt Activity", self.activity, "max_attempts")
		if max_attempts == 0:
			return

		current_user_submission_count = frappe.db.count(
			self.doctype, filters={"activity": self.activity, "member": frappe.session.user}
		)
		if current_user_submission_count >= max_attempts:
			frappe.throw(
				_("You have exceeded the maximum number of attempts ({0}) for this activity").format(
					max_attempts
				),
				MaximumAttemptsExceededError,
			)

	def validate_marks(self):
		self.score = 0
		for row in self.result:
			if cint(row.marks) > cint(row.marks_out_of):
				frappe.throw(
					_(
						"Marks for row number {0} cannot be greater than the marks allotted for that row."
					).format(row.idx)
				)
			self.score += cint(row.marks)

	def set_percentage(self):
		if self.score_out_of:
			self.percentage = (self.score / self.score_out_of) * 100

	def notify_member(self):
		if not self.has_value_changed("score"):
			return

		notification = frappe._dict(
			{
				"subject": _("Your score for {0} has been updated to {1}").format(
					frappe.bold(self.activity_title), frappe.bold(self.score)
				),
				"email_content": _(
					"There has been an update on your word hunt submission. Your latest score is {0}."
				).format(frappe.bold(self.score)),
				"document_type": self.doctype,
				"document_name": self.name,
				"for_user": self.member,
				"from_user": frappe.session.user,
				"type": "Alert",
				"link": "",
			}
		)
		make_notification_logs(notification, [self.member])


class MaximumAttemptsExceededError(frappe.DuplicateEntryError):
	pass
