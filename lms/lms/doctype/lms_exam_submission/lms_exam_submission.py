# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint

from lms.lms.utils import get_exam_attempt_count, get_exam_status


class LMSExamSubmission(Document):
	def validate(self):
		self.validate_attempt_access()
		self.validate_marks()
		self.set_percentage()
		self.set_attempt_number()

	def validate_attempt_access(self):
		if not self.is_new():
			return
		status = get_exam_status(self.exam, self.member or frappe.session.user)
		if not status.get("can_attempt"):
			frappe.throw(status.get("locked_reason") or _("You cannot attempt this exam yet."))

	def validate_marks(self):
		self.score = 0
		for row in self.result:
			if cint(row.marks) > cint(row.marks_out_of):
				frappe.throw(
					_(
						"Marks for question number {0} cannot be greater than the marks allotted for that question."
					).format(row.idx)
				)
			self.score += cint(row.marks)

	def set_percentage(self):
		if self.score_out_of:
			self.percentage = (self.score / self.score_out_of) * 100

	def set_attempt_number(self):
		if self.attempt_number:
			return
		self.attempt_number = get_exam_attempt_count(self.exam) + 1


class MaximumExamAttemptsExceededError(frappe.DuplicateEntryError):
	pass
