# Copyright (c) 2026, Frappe and Contributors
# See license.txt
"""Regression test for idempotent quiz submission (T2.9).

T2.5 fixed a `pagehide` re-post creating a second `LMS Exam Submission`. The
same defect exists on the quiz path and that fix does not reach it: `Quiz.vue`
beacons to `lms_quiz.submit_quiz`, and `lms_quiz.create_submission` inserts a
new `LMS Quiz Submission` with no existence check.

Run with:

	bench --site <site> run-tests --module lms.lms.test_quiz_attempts
"""

import json

import frappe

from lms.lms.doctype.lms_quiz.lms_quiz import submit_quiz
from lms.lms.test_helpers import BaseTestUtils


class TestQuizSubmissionIdempotency(BaseTestUtils):
	def setUp(self):
		super().setUp()
		self.student = self._create_user(
			"quiz-student@example.com", "Quiz", "Student", ["LMS Student"]
		)

		self.course = self._create_course("Quiz Idempotency Course")
		self._create_enrollment(self.student.email, self.course.name)

		# `_create_quiz` reads `self.questions`, so they have to exist first.
		self.questions = self._create_quiz_questions()
		self.quiz = self._create_quiz("Idempotency Quiz")

		frappe.set_user(self.student.email)

	def tearDown(self):
		frappe.set_user("Administrator")
		super().tearDown()

	def _full_marks_results(self):
		return json.dumps([{"question_name": q.name, "answer": [q.option_1]} for q in self.questions])

	def _track(self, result):
		name = (result or {}).get("submission")
		if name:
			self.cleanup_items.append(("LMS Quiz Submission", name))

	def test_second_immediate_submission_is_not_a_new_attempt(self):
		"""T2.9: a `pagehide` re-post must not create a second quiz submission.

		Fails today: two submissions exist for one sitting.

		This is the exact shape of T2.5's exam test, deliberately — the two paths
		should behave the same way, and today they do not.
		"""
		first = submit_quiz(self.quiz.name, self._full_marks_results())
		self._track(first)
		self.assertTrue(first.get("submission"))

		second = submit_quiz(self.quiz.name, self._full_marks_results())
		self._track(second)

		count = frappe.db.count(
			"LMS Quiz Submission", {"quiz": self.quiz.name, "member": self.student.email}
		)
		self.assertEqual(count, 1, "a duplicate pagehide re-post must not create a second submission")
		self.assertEqual(second.get("submission"), first.get("submission"))
