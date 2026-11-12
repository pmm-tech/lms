# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from lms.lms.utils import get_lesson_count, recalculate_course_progress


class CourseChapter(Document):
	def after_insert(self):
		self.recalculate_progress()

	def after_delete(self):
		self.recalculate_progress()

	def on_update(self):
		self.update_lesson_count()
		# after_insert already covers a brand-new chapter's lesson set.
		if not self.flags.in_insert and self.lesson_set_changed():
			self.recalculate_progress()

	def lesson_set_changed(self):
		"""Whether the referenced lessons differ from the stored ones.

		`has_value_changed("lessons")` is not usable here: it does not deep-compare
		a child table, so it reports a change on any save — including a title edit,
		which would recompute every enrolment for nothing. Compared as a *set*,
		because progress is order-independent and a reorder is not a change.
		"""
		before = self.get_doc_before_save()
		if not before:
			return True
		return {row.lesson for row in self.lessons} != {row.lesson for row in before.lessons}

	def update_lesson_count(self):
		"""Update lesson count in the course"""
		frappe.db.set_value("LMS Course", self.course, "lessons", get_lesson_count(self.course))

	def recalculate_progress(self):
		"""Recompute every enrolment when this chapter's lesson set changes.

		A chapter's `Lesson Reference` rows are the denominator of every member's
		progress, so changing them invalidates all of it. Nothing did that:
		`recalculate_course_progress` was reachable only from `CourseLesson`, so
		editing a reference left stored progress describing a lesson set that no
		longer existed — production carries the scar as one course with stored
		values implying denominators of 62, 63 and 70.

		Enqueued rather than run inline, matching `CourseLesson`: a course can
		have many enrolments and this is not work the saving user should wait on.
		`now` under test is the idiom frappe core uses (Module Profile, Role
		Profile, Notification Log) so the effect is observable.
		"""
		if not self.course:
			return

		enrollments = frappe.db.get_all(
			"LMS Enrollment",
			filters={"course": self.course},
			fields=["name", "member"],
		)
		if not enrollments:
			return

		frappe.enqueue(
			method=recalculate_progress_for_enrollments,
			queue="long",
			is_async=True,
			now=frappe.flags.in_test,
			course=self.course,
			enrollments=enrollments,
		)


def recalculate_progress_for_enrollments(course: str, enrollments: list):
	for enrollment in enrollments:
		recalculate_course_progress(course, enrollment.member)
