# Copyright (c) 2026, Frappe and Contributors
# See license.txt
"""Progress must be recomputed when a course's lesson set changes (T2.6).

`recalculate_course_progress` was only ever reachable from `CourseLesson`
`after_insert` / `after_delete`. Editing a chapter's `Lesson Reference` rows —
which *is* the denominator of every member's progress — recomputed nothing,
leaving stored progress describing a lesson set that no longer exists.
Production carries the scar: the same course has stored values implying
denominators of 62, 63 and 70.

Run with:

	bench --site <site> run-tests --module lms.lms.test_progress_recalculation
"""

import frappe

from lms.lms.test_helpers import BaseTestUtils
from lms.lms.utils import recalculate_course_progress


class TestProgressRecalculation(BaseTestUtils):
	def setUp(self):
		super().setUp()
		self.student = self._create_user(
			"recalc-student@example.com", "Recalc", "Student", ["LMS Student"]
		)

		self.course = self._create_course("Recalculation Course")
		self._create_enrollment(self.student.email, self.course.name)

		self.chapter = self._create_chapter("Recalculation Chapter", self.course.name)
		self._create_chapter_reference(self.course.name, self.chapter.name)

		self.lessons = []
		for index in (1, 2):
			lesson = self._create_lesson(
				f"Recalc Lesson {index}", self.chapter.name, self.course.name
			)
			self._create_lesson_reference(self.chapter.name, lesson.name)
			self.lessons.append(lesson)

		# One of the two referenced lessons complete: stored progress is 50.
		self._create_progress(self.student.email, self.course.name, self.lessons[0].name)
		# Establish the correct stored value for the *current* lesson set, using
		# the real function rather than hand-writing a number — the tests below
		# are about the hook that keeps it correct, not about arithmetic.
		recalculate_course_progress(self.course.name, self.student.email)

	def _stored_progress(self):
		"""The value on the enrolment — not `get_course_progress`, which computes."""
		return frappe.db.get_value(
			"LMS Enrollment",
			{"course": self.course.name, "member": self.student.email},
			"progress",
		)

	def test_adding_a_lesson_reference_recomputes_stored_progress(self):
		"""T2.6: a third referenced lesson must move 50% to a third.

		Fails today: the stored value stays 50 while the denominator has moved to
		three, so the member reads two thirds further along than they are.
		"""
		self.assertEqual(self._stored_progress(), 50.0)

		third = self._create_lesson("Recalc Lesson 3", self.chapter.name, self.course.name)
		# Save through the *parent*, which is what a desk edit does; inserting the
		# child row standalone bypasses the chapter's hooks entirely.
		chapter = frappe.get_doc("Course Chapter", self.chapter.name)
		chapter.append("lessons", {"lesson": third.name})
		chapter.save(ignore_permissions=True)

		self.assertAlmostEqual(self._stored_progress(), 33.333, places=2)

	def test_removing_a_lesson_reference_recomputes_stored_progress(self):
		"""T2.6: dropping an unreferenced-by-progress lesson must move 50% up.

		Fails today: the stored value stays 50 while the denominator has moved to
		one, so the member looks half done on a course they have finished.
		"""
		self.assertEqual(self._stored_progress(), 50.0)

		chapter = frappe.get_doc("Course Chapter", self.chapter.name)
		# Drop the lesson they have *not* completed, leaving one they have.
		chapter.set(
			"lessons",
			[row for row in chapter.lessons if row.lesson != self.lessons[1].name],
		)
		chapter.save(ignore_permissions=True)

		self.assertEqual(self._stored_progress(), 100.0)

	def test_editing_a_chapter_title_does_not_recompute(self):
		"""A title edit leaves the lesson set alone and must not enqueue a recompute.

		Guards the `has_value_changed("lessons")` condition: recomputing every
		enrolment on every chapter save would be waste, not correctness.
		"""
		frappe.db.set_value(
			"LMS Enrollment",
			{"course": self.course.name, "member": self.student.email},
			"progress",
			42.0,
		)

		chapter = frappe.get_doc("Course Chapter", self.chapter.name)
		chapter.title = "Recalculation Chapter (renamed)"
		chapter.save(ignore_permissions=True)

		# The sentinel survives, proving nothing recomputed it back to 50.
		self.assertEqual(self._stored_progress(), 42.0)
