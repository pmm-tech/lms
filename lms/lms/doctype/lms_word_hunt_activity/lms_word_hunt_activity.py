# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import json
import re

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint

from ..course_lesson.course_lesson import save_progress
from ...utils import generate_slug

BLANK_PATTERN = re.compile(r"_+")


class LMSWordHuntActivity(Document):
	def validate(self):
		self.validate_passage()
		self.validate_items()
		self.validate_placeholders()
		self.calculate_total_marks()

	def autoname(self):
		if not self.name:
			self.name = generate_slug(self.title, "LMS Word Hunt Activity")

	def validate_passage(self):
		if not self.passage or not self.passage.strip():
			frappe.throw(_("The passage is required."))

	def validate_items(self):
		if not self.items:
			frappe.throw(_("Add at least one blank to this activity."))

		for index, row in enumerate(self.items, start=1):
			row.placeholder = f"blank_{index}"
			if not row.correct_answer:
				frappe.throw(_("Each blank must have a correct answer."))

	def validate_placeholders(self):
		blank_count = count_blanks(self.passage)

		if not blank_count:
			frappe.throw(
				_("Add at least one blank in the passage using underscores like _ or _______.")
			)

		if blank_count != len(self.items):
			frappe.throw(
				_(
					"The passage contains {0} blanks, but you added {1} answers. The counts must match."
				).format(blank_count, len(self.items))
			)

	def calculate_total_marks(self):
		self.total_marks = sum(cint(row.marks) for row in self.items)
		if not self.items:
			self.total_marks = 0
			self.passing_percentage = 100


def normalize_answer(answer):
	return " ".join((answer or "").strip().split()).casefold()


def count_blanks(passage):
	return len(BLANK_PATTERN.findall(passage or ""))


@frappe.whitelist()
def submit_activity(activity: str, answers: str):
	answers = json.loads(answers or "[]")
	activity_doc = frappe.get_doc("LMS Word Hunt Activity", activity)

	results = []
	score = 0
	for item in activity_doc.items:
		submitted_answer = next(
			(
				row.get("submitted_answer")
				for row in answers
				if row.get("item") == item.name
				or row.get("idx") == item.idx
			),
			"",
		)
		is_correct = normalize_answer(submitted_answer) == normalize_answer(item.correct_answer)
		marks = cint(item.marks) if is_correct else 0
		score += marks
		results.append(
			{
				"item": item.name,
				"placeholder": item.placeholder,
				"submitted_answer": submitted_answer,
				"correct_answer": item.correct_answer,
				"is_correct": 1 if is_correct else 0,
				"marks": marks,
				"marks_out_of": item.marks,
			}
		)

	score_out_of = activity_doc.total_marks
	percentage = (score / score_out_of) * 100 if score_out_of else 0
	submission = create_submission(activity_doc, results, score, score_out_of, percentage)

	save_progress_after_activity(activity_doc, percentage)

	return {
		"score": score,
		"score_out_of": score_out_of,
		"submission": submission.name,
		"pass": percentage >= activity_doc.passing_percentage,
		"percentage": percentage,
	}


def create_submission(activity_doc, results, score, score_out_of, percentage):
	submission = frappe.new_doc("LMS Word Hunt Submission")
	submission.update(
		{
			"activity": activity_doc.name,
			"result": results,
			"score": score,
			"score_out_of": score_out_of,
			"member": frappe.session.user,
			"percentage": percentage,
			"passing_percentage": activity_doc.passing_percentage,
		}
	)
	submission.save(ignore_permissions=True)
	return submission


def save_progress_after_activity(activity_doc, percentage):
	if not activity_doc.lesson or not activity_doc.course:
		return

	if percentage >= activity_doc.passing_percentage or not activity_doc.passing_percentage:
		save_progress(activity_doc.lesson, activity_doc.course)
