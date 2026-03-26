# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint

from lms.lms.doctype.course_lesson.course_lesson import save_progress
from lms.lms.utils import generate_slug


class LMSDragDropActivity(Document):
	def validate(self):
		self.validate_items()
		self.calculate_total_marks()

	def autoname(self):
		if not self.name:
			self.name = generate_slug(self.title, "LMS Drag Drop Activity")

	def validate_items(self):
		for row in self.items:
			display_type = (row.display_type or "Text").strip().lower()

			if display_type == "image":
				if not row.image:
					frappe.throw(_("Each image row must contain an image."))
			elif not row.prompt_before and not row.prompt_after:
				frappe.throw(_("Each text row must contain prompt text before or after the blank."))

			answer_type = (row.answer_type or "Text").strip().lower()
			if answer_type == "image":
				if not row.answer_image:
					frappe.throw(_("Each image answer row must contain an answer image."))
			else:
				if not row.correct_answer:
					frappe.throw(_("Each text answer row must have a correct answer."))

	def calculate_total_marks(self):
		self.total_marks = sum(cint(row.marks) for row in self.items)
		if not self.items:
			self.total_marks = 0
			self.passing_percentage = 100


def normalize_answer(answer):
	return " ".join((answer or "").strip().split()).casefold()


@frappe.whitelist()
def submit_activity(activity: str, answers: str):
	answers = json.loads(answers or "[]")
	activity_doc = frappe.get_doc("LMS Drag Drop Activity", activity)

	results = []
	score = 0
	for item in activity_doc.items:
		submitted_answer = next(
			(
				row.get("submitted_answer")
				for row in answers
				if row.get("item") == item.name or row.get("idx") == item.idx
			),
			"",
		)
		answer_type = item.answer_type or "Text"
		is_correct = False
		if answer_type == "Image":
			is_correct = normalize_answer(submitted_answer) == normalize_answer(item.answer_image)
		else:
			is_correct = normalize_answer(submitted_answer) == normalize_answer(item.correct_answer)

		marks = cint(item.marks) if is_correct else 0
		score += marks
		results.append(
			{
				"item": item.name,
				"display_type": item.display_type,
				"image": item.image,
				"prompt_before": item.prompt_before,
				"prompt_after": item.prompt_after,
				"answer_type": answer_type,
				"submitted_answer": submitted_answer if answer_type == "Text" else "",
				"submitted_answer_image": submitted_answer if answer_type == "Image" else "",
				"correct_answer": item.correct_answer if answer_type == "Text" else "",
				"correct_answer_image": item.answer_image if answer_type == "Image" else "",
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
	submission = frappe.new_doc("LMS Drag Drop Submission")
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
