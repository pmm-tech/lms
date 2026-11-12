# Copyright (c) 2026, Frappe and Contributors
# See license.txt
"""Regression tests for the course-progress completeness gates (T2.1).

These reproduce the `progress == 100` / `progress < 100` defects recorded in
`clients/bahaso-exam-certificate-findings.md`, against the fork source that
carries them. Every test below **fails on the code as found on 2026-11-03**,
for the reason named in its docstring. The fixes are T2.2 and T2.3.

Run with:

	bench --site <site> run-tests --module lms.lms.test_course_progress_gates
"""

import frappe

from lms.lms.report.course_progress_summary.course_progress_summary import get_charts
from lms.lms.test_helpers import BaseTestUtils
from lms.lms.utils import get_course_completion_stats, get_course_progress


class TestCourseProgressGates(BaseTestUtils):
	def setUp(self):
		super().setUp()
		self.student = self._create_user("prog-student@example.com", "Prog", "Student", ["LMS Student"])
		self.other = self._create_user("prog-other@example.com", "Other", "Student", ["LMS Student"])

		self.course = self._create_course("Progress Gate Course")
		self.course.db_set("enable_certification", 1)

		# Two chapters' worth of lesson *references* is the denominator
		# (`get_lessons(..., get_details=False)` counts Lesson Reference rows).
		self.chapter = self._create_chapter("Gate Chapter", self.course.name)
		self._create_chapter_reference(self.course.name, self.chapter.name)
		self.lessons = []
		for index in (1, 2):
			lesson = self._create_lesson(f"Gate Lesson {index}", self.chapter.name, self.course.name)
			self._create_lesson_reference(self.chapter.name, lesson.name)
			self.lessons.append(lesson)

		self._create_enrollment(self.student.email, self.course.name)
		self._create_enrollment(self.other.email, self.course.name)

	def tearDown(self):
		frappe.set_user("Administrator")
		super().tearDown()

	def test_progress_counts_distinct_lessons_not_rows(self):
		"""T2.3: three Complete rows over two lessons must read 100, not 150.

		`get_course_progress` divides the *row* count by the lesson count, so a
		duplicate or stray row takes a course past 100. Production's 101.613%
		student is exactly this shape. Fails today at 150.0.
		"""
		for lesson in self.lessons:
			self._create_progress(self.student.email, self.course.name, lesson.name)
		# a second row for a lesson already complete: two rows, one lesson
		self._create_progress(self.student.email, self.course.name, self.lessons[0].name)

		self.assertEqual(get_course_progress(self.course.name, self.student.email), 100.0)

	def test_progress_clamps_at_100_for_an_unreferenced_lesson(self):
		"""T2.3: a completed lesson outside the lesson set must not push past 100.

		A `Course Lesson` that exists but is referenced by no `Lesson Reference`
		row is not in the denominator, so completing it must not be in the
		numerator either. Fails today at 150.0.
		"""
		for lesson in self.lessons:
			self._create_progress(self.student.email, self.course.name, lesson.name)

		unreferenced = self._create_lesson(
			"Gate Lesson 3 (unreferenced)", self.chapter.name, self.course.name
		)
		self._create_progress(self.student.email, self.course.name, unreferenced.name)

		progress = get_course_progress(self.course.name, self.student.email)
		self.assertEqual(progress, 100.0)
		self.assertLessEqual(progress, 100.0)

	def test_batch_completion_stats_counts_over_100_as_completed(self):
		"""T2.2: `utils.py:1659` counts `progress == 100`, so a >100 student is lost.

		The 101.613% student who did the most work is the one this counter drops.
		Fails today: the value is 0.
		"""
		batch = self._create_batch(self.course.name)
		self._create_batch_enrollment(self.student.email, batch.name)
		self._set_stored_progress(101.613)

		stats = get_course_completion_stats(batch.name)
		self.assertEqual(stats[0]["value"], 1)

	def test_report_buckets_a_course_at_over_100_as_complete(self):
		"""T2.2: the report's `== 100` puts 101 in the 71-99 bucket, not 100.

		`course_progress_summary.py:94`. Fails today: `completed` is 0 and the
		71-99 bucket holds the student.
		"""
		charts = get_charts([frappe._dict({"progress": 101})])
		values = charts["data"]["datasets"][0]["values"]

		# labels: ["0-10", "11-40", "41-70", "71-99", "100"]
		self.assertEqual(values[-1], 1, "101% must land in the 100 bucket")
		self.assertEqual(sum(values), 1, "and in no other bucket")

	def _set_stored_progress(self, value):
		name = frappe.db.get_value(
			"LMS Enrollment", {"course": self.course.name, "member": self.student.email}
		)
		frappe.db.set_value("LMS Enrollment", name, "progress", value)
