# Copyright (c) 2026, Frappe and Contributors
# See license.txt
"""Regression tests for exam attempt bookkeeping and idempotent submission (T2.1).

Reproduces the omitted-`member` defect recorded in
`clients/bahaso-exam-certificate-findings.md` §2: `get_exam_attempt_count` reads
as an exam-wide count whenever its caller forgets the member, and two callers do
exactly that (`lms_exam.py:231`, `lms_exam_submission.py:44`).

Run with:

	bench --site <site> run-tests --module lms.lms.test_exam_attempts
"""

import json

import frappe

from lms.lms.doctype.lms_exam.lms_exam import submit_exam
from lms.lms.test_helpers import BaseTestUtils
from lms.lms.utils import get_exam_attempt_count


class TestExamAttemptBookkeeping(BaseTestUtils):
	def setUp(self):
		super().setUp()
		self.student = self._create_user("exam-student@example.com", "Exam", "Student", ["LMS Student"])
		self.other = self._create_user("exam-other@example.com", "Other", "Student", ["LMS Student"])

		self.course = self._create_course("Exam Attempt Course")
		self._create_enrollment(self.student.email, self.course.name)
		self._create_enrollment(self.other.email, self.course.name)

		self.questions = self._create_quiz_questions()
		self.exam = frappe.new_doc("LMS Exam")
		self.exam.update(
			{
				"title": "Attempt Counting Exam",
				"course": self.course.name,
				"is_final_exam": 1,
				"passing_percentage": 80,
			}
		)
		for question in self.questions:
			self.exam.append("questions", {"question": question.name, "marks": 1})
		self.exam.save()
		self.cleanup_items.append(("LMS Exam", self.exam.name))
		self.exam.reload()
		self.exam.db_set("available_from", "2020-01-01 00:00:00")

	def tearDown(self):
		frappe.set_user("Administrator")
		super().tearDown()

	def _full_marks_results(self):
		return json.dumps([{"question_name": q.name, "answer": [q.option_1]} for q in self.questions])

	# --- the defect -------------------------------------------------------

	def test_attempt_count_is_per_member_not_exam_wide(self):
		"""T2.4: `get_exam_attempt_count(exam)` must not silently be exam-wide.

		`utils.py:339` defaults `member` to `frappe.session.user`, so a caller
		that omits it inherits an *exam-wide* count as its default. The fix is to
		remove the default; then calling with one argument is a `TypeError`.

		Fails today: the call returns 1 (the other student's submission) and no
		TypeError is raised.
		"""
		self._submit_as(self.student.email)

		with self.assertRaises(TypeError):
			get_exam_attempt_count(self.exam.name)

	def test_attempt_count_is_member_scoped(self):
		"""Passing the member explicitly is already correct and must stay correct."""
		self._submit_as(self.student.email)
		self.assertEqual(get_exam_attempt_count(self.exam.name, self.student.email), 1)
		self.assertEqual(get_exam_attempt_count(self.exam.name, self.other.email), 0)

	def test_set_attempt_number_uses_the_submission_member(self):
		"""T2.4: `lms_exam_submission.py:44` computes the number for the wrong member.

		`set_attempt_number` calls `get_exam_attempt_count(self.exam)` with no
		member, so the count comes from `frappe.session.user` rather than from the
		submission's own `member` field. The two agree whenever the session user
		*is* the person the submission is for — which is why the first version of
		this test could not fail: it set the session user to the member, so the
		wrong source and the right source returned the same number.

		Here they disagree. `other` has one attempt and stays the session user,
		while the submission is for `student`, who has none. The number must be
		derived from the submission's member. Fails today: 2, not 1.
		"""
		self._submit_as(self.other.email)

		frappe.set_user(self.other.email)
		submission = frappe.new_doc("LMS Exam Submission")
		submission.update(
			{
				"exam": self.exam.name,
				"member": self.student.email,
				"score": 1,
				"score_out_of": self.exam.total_marks,
				"passing_percentage": self.exam.passing_percentage,
			}
		)
		submission.insert(ignore_permissions=True)
		self.cleanup_items.append(("LMS Exam Submission", submission.name))

		self.assertEqual(submission.attempt_number, 1)

	# --- idempotent submission (T2.5) ------------------------------------

	def test_second_immediate_submission_is_not_a_new_attempt(self):
		"""T2.5: a `pagehide` re-post must not create a second attempt.

		The client re-sends the same answers on `pagehide`
		(`Exam.vue:699-710`). The server has no token guard, so today it creates a
		*second* `LMS Exam Submission`. Fails today: two submissions exist.

		This pins the server-side half of the fix. If T2.5 lands the client-side
		guard instead (only beacon when not already submitted), this test should
		be reconsidered rather than deleted.
		"""
		frappe.set_user(self.student.email)

		first = submit_exam(self.exam.name, self._full_marks_results())
		self._track(first)
		self.assertTrue(first.get("submission"))

		second = submit_exam(self.exam.name, self._full_marks_results())
		self._track(second)

		count = frappe.db.count("LMS Exam Submission", {"exam": self.exam.name, "member": self.student.email})
		self.assertEqual(count, 1, "a duplicate pagehide re-post must not create a second submission")
		self.assertEqual(second.get("submission"), first.get("submission"))

	# --- helper -----------------------------------------------------------

	def _submit_as(self, member):
		frappe.set_user(member)
		result = submit_exam(self.exam.name, self._full_marks_results())
		frappe.set_user("Administrator")
		self._track(result)
		return result

	def _track(self, result):
		name = (result or {}).get("submission")
		if name:
			self.cleanup_items.append(("LMS Exam Submission", name))

	# --- T3.4: the index the submission list needs ------------------------

	def test_exam_submission_has_an_exam_member_index(self):
		"""T3.4: `(exam, member)` must be indexed.

		The submission list filters by `exam` alone, and the per-student lookups
		constrain both `exam` and `member`; the table carried only `PRIMARY` and
		`modified`, so every per-student lookup was a full scan that grows with
		every attempt ever recorded.

		Column *order* is asserted, not just membership: `(member, exam)` would
		serve the per-student lookups but not the list's exam-only filter, and an
		index that only partly covers the query would look like a pass.
		"""
		rows = frappe.db.sql("SHOW INDEX FROM `tabLMS Exam Submission`", as_dict=True)
		by_index = {}
		for row in rows:
			by_index.setdefault(row["Key_name"], []).append((row["Seq_in_index"], row["Column_name"]))

		leading_pairs = [tuple(column for _, column in sorted(columns))[:2] for columns in by_index.values()]

		self.assertIn(
			("exam", "member"),
			leading_pairs,
			f"no (exam, member) index; found: {sorted(by_index)}",
		)
