# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import json
import re

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, comma_and, cstr, get_datetime, now_datetime

from lms.lms.doctype.lms_quiz.lms_quiz import _save_file, get_corrupted_image_msg, verify_answer
from lms.lms.utils import (
	generate_slug,
	get_exam_attempt_count,
	get_exam_status,
)


class LMSExam(Document):
	def validate(self):
		self.validate_course_and_display_chapter()
		self.validate_one_final_exam_per_course()
		self.validate_duplicate_questions()
		self.validate_limit()
		self.calculate_total_marks()
		self.validate_open_ended_questions()
		self.validate_prerequisites()
		self.validate_availability_window()

	def validate_course_and_display_chapter(self):
		if not self.display_chapter:
			return

		chapter_course = frappe.db.get_value("Course Chapter", self.display_chapter, "course")
		if not chapter_course:
			frappe.throw(_("Invalid display chapter."))
		if chapter_course != self.course:
			frappe.throw(_("Display chapter must belong to the selected course."))

	def validate_one_final_exam_per_course(self):
		if not cint(self.is_final_exam):
			return

		filters = {
			"course": self.course,
			"is_final_exam": 1,
			"name": ["!=", self.name or ""],
		}
		if frappe.db.exists("LMS Exam", filters):
			frappe.throw(_("Only one final exam is allowed per course."))

	def validate_duplicate_questions(self):
		questions = [row.question for row in self.questions]
		rows = [i + 1 for i, x in enumerate(questions) if questions.count(x) > 1]
		if rows:
			frappe.throw(_("Rows {0} have duplicate questions.").format(frappe.bold(comma_and(rows))))

	def validate_limit(self):
		if not self.shuffle_questions and self.limit_questions_to:
			self.limit_questions_to = 0

		if self.limit_questions_to and cint(self.limit_questions_to) >= len(self.questions):
			frappe.throw(_("Limit cannot be greater than or equal to the number of questions in the exam."))

		if self.limit_questions_to and cint(self.limit_questions_to) < len(self.questions):
			marks = [question.marks for question in self.questions]
			if len(set(marks)) > 1:
				frappe.throw(_("All questions should have the same marks if the limit is set."))

	def calculate_total_marks(self):
		if not self.questions:
			self.total_marks = 0
			self.passing_percentage = 100
			return

		if self.limit_questions_to:
			self.total_marks = sum(
				question.marks for question in self.questions[: cint(self.limit_questions_to)]
			)
			return

		self.total_marks = sum(cint(question.marks) for question in self.questions)

	def validate_open_ended_questions(self):
		types = {question.type for question in self.questions}

		if "Open Ended" in types:
			if len(types) > 1:
				frappe.throw(
					_(
						"If you want open ended questions then make sure each question in the exam is of open ended type."
					)
				)
			self.show_answers = 0

	def validate_prerequisites(self):
		for row in self.prerequisites:
			if row.requirement_type == "Course Progress":
				if row.minimum_percentage is None:
					frappe.throw(_("Row {0}: Minimum percentage is required.").format(row.idx))
				continue

			if row.requirement_type == "Quiz":
				if not row.quiz:
					frappe.throw(_("Row {0}: Quiz is required.").format(row.idx))
				if frappe.db.get_value("LMS Quiz", row.quiz, "course") != self.course:
					frappe.throw(_("Row {0}: Quiz must belong to the selected course.").format(row.idx))
				continue

			if row.requirement_type == "Drag Drop":
				if not row.drag_drop_activity:
					frappe.throw(_("Row {0}: Drag and drop activity is required.").format(row.idx))
				if (
					frappe.db.get_value("LMS Drag Drop Activity", row.drag_drop_activity, "course")
					!= self.course
				):
					frappe.throw(
						_("Row {0}: Drag and drop activity must belong to the selected course.").format(
							row.idx
						)
					)

	def validate_availability_window(self):
		if self.available_from and self.available_until:
			if get_datetime(self.available_from) >= get_datetime(self.available_until):
				frappe.throw(_("Available Until must be after Available From."))

	def autoname(self):
		if not self.name:
			self.name = generate_slug(self.title, "LMS Exam")

	def get_last_submission_details(self):
		user = frappe.session.user
		if not user or user == "Guest":
			return None

		result = frappe.get_all(
			"LMS Exam Submission",
			fields=["*"],
			filters={"member": user, "exam": self.name},
			order_by="creation desc",
			page_length=1,
		)
		return result[0] if result else None


@frappe.whitelist()
def get_exam_context(exam: str):
	doc = frappe.get_doc("LMS Exam", exam)
	status = get_exam_status(exam)
	return {
		"exam": doc.as_dict(),
		"status": status,
	}


@frappe.whitelist()
def submit_exam(exam: str, results: str):
	results = results and json.loads(results)
	exam_doc = frappe.get_doc("LMS Exam", exam)
	status = get_exam_status(exam)

	if not status.get("can_attempt"):
		frappe.throw(status.get("locked_reason") or _("You cannot attempt this exam yet."))

	data = process_results(results, exam_doc)
	results = data["results"]
	score = data["score"]
	is_open_ended = data["is_open_ended"]
	score_out_of = exam_doc.total_marks
	percentage = (score / score_out_of) * 100 if score_out_of else 0

	submission = create_submission(exam_doc, results, score_out_of, exam_doc.passing_percentage)
	return {
		"score": score,
		"score_out_of": score_out_of,
		"submission": submission.name,
		"pass": percentage >= exam_doc.passing_percentage,
		"percentage": percentage,
		"is_open_ended": is_open_ended,
		"status": get_exam_status(exam),
	}


def process_results(results: list, exam_doc: LMSExam):
	score = 0
	is_open_ended = False

	for result in results:
		question_details = frappe.db.get_value(
			"LMS Exam Question",
			{"parent": exam_doc.name, "question": result["question_name"]},
			["question", "marks", "question_detail", "type"],
			as_dict=1,
		)
		result["question_name"] = question_details.question
		result["question"] = question_details.question_detail
		result["marks_out_of"] = question_details.marks

		if question_details.type != "Open Ended":
			correct = verify_answer(question_details.question, result["answer"])
			result["answer"] = ", ".join(result["answer"])
			if correct:
				result["marks"] = question_details.marks
			else:
				result["marks"] = -exam_doc.marks_to_cut if exam_doc.enable_negative_marking else 0

			score += result["marks"]
			result["is_correct"] = 1 if correct else 0
		else:
			is_open_ended = True
			result["is_correct"] = 0
			result["answer"] = re.sub(
				r'<img[^>]*src\s*=\s*["\'](?=data:)(.*?)["\']',
				_save_file,
				result["answer"][0],
			)
			if frappe.flags.has_dataurl:
				frappe.msgprint(get_corrupted_image_msg(), alert=True)

	return {
		"results": results,
		"score": score,
		"is_open_ended": is_open_ended,
	}


def create_submission(exam_doc: LMSExam, results: list, score_out_of: int, passing_percentage: float):
	submission = frappe.new_doc("LMS Exam Submission")
	attempt_number = get_exam_attempt_count(exam_doc.name) + 1
	submission.update(
		{
			"doctype": "LMS Exam Submission",
			"exam": exam_doc.name,
			"result": results,
			"score": 0,
			"score_out_of": score_out_of,
			"member": frappe.session.user,
			"percentage": 0,
			"passing_percentage": passing_percentage,
			"attempt_number": attempt_number,
		}
	)
	submission.save(ignore_permissions=True)
	return submission
