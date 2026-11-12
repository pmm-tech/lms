# Copyright (c) 2026, Frappe and Contributors
# See license.txt
"""Boundary tests for the certificate eligibility gates (T2.1).

**These are not reproductions — they pass on the code as found.** They are here
to pin the boundary before T2.2 touches it, because reading the two backend
gates corrects a claim in the plan.

The plan lists `lms_certificate.py:94` (doctype) and `:227` (API) as `== 100`
sites needing `>= 100`. Both are in fact `if progress < 100`, which *already*
accepts a student past 100 — the findings doc says so outright ("the backend
would have *allowed* it"). The only gate that actually refuses the 101.613%
student is the UI's `progress == 100` in `CourseCardOverlay.vue:286`, which this
harness cannot exercise (no Vue unit runner; Cypress needs a separate site).

So T2.2's work on those two lines is a no-op for the over-100 class. What they
*did* need is the D1 threshold change, which is a decision, not a defect. The
tests below hold the line at 100 until that decision lands.

Run with:

	bench --site <site> run-tests --module lms.lms.test_certificate_eligibility
"""

import frappe

from lms.lms.doctype.lms_certificate.lms_certificate import (
	create_certificate,
	get_default_certificate_template,
	validate_certification_eligibility,
)
from lms.lms.test_helpers import BaseTestUtils


class TestCertificateEligibility(BaseTestUtils):
	def setUp(self):
		super().setUp()
		self.student = self._create_user("cert-student@example.com", "Cert", "Student", ["LMS Student"])

		self.course = self._create_course("Certificate Gate Course")
		self.course.db_set("enable_certification", 1)
		self._create_enrollment(self.student.email, self.course.name)

		frappe.set_user(self.student.email)

	def tearDown(self):
		frappe.set_user("Administrator")
		super().tearDown()

	def _set_progress(self, value):
		name = frappe.db.get_value(
			"LMS Enrollment", {"course": self.course.name, "member": self.student.email}
		)
		frappe.db.set_value("LMS Enrollment", name, "progress", value)

	def _create_exam(self, passing_percentage=80):
		"""A final exam attached to the course, so `get_course_exam` returns a status."""
		exam = frappe.new_doc("LMS Exam")
		exam.update(
			{
				"title": "Eligibility Boundary Exam",
				"course": self.course.name,
				"is_final_exam": 1,
				"passing_percentage": passing_percentage,
			}
		)
		exam.save(ignore_permissions=True)
		# `calculate_total_marks` forces an exam with no questions to 100%, so
		# the mark we asked for has to be pinned after save. Building a real
		# question set here would test exam construction, not the certificate
		# gate, and a question needs the naming-series workaround besides.
		exam.db_set("passing_percentage", passing_percentage)
		self.cleanup_items.append(("LMS Exam", exam.name))
		return exam

	def _record_submission(self, exam, percentage):
		"""A submission row is all `has_passed_exam` reads — no question plumbing."""
		submission = frappe.new_doc("LMS Exam Submission")
		submission.update(
			{
				"exam": exam.name,
				"member": self.student.email,
				"percentage": percentage,
				"passing_percentage": exam.passing_percentage,
				"score": percentage,
				"score_out_of": 100,
			}
		)
		submission.insert(ignore_permissions=True)
		self.cleanup_items.append(("LMS Exam Submission", submission.name))
		return submission

	def _assert_eligible(self):
		"""The gate must not throw. Reported as a failure, not an error."""
		try:
			validate_certification_eligibility(self.course.name)
		except frappe.exceptions.ValidationError as error:
			self.fail(f"expected eligible, but was refused: {error}")

	def test_api_eligibility_accepts_over_100(self):
		"""`lms_certificate.py:227` already accepts >100. Guards against a `>=` edit."""
		self._set_progress(101.613)
		self._assert_eligible()

	# --- D1: the threshold is 80, not 100 ---------------------------------
	#
	# D1 settled the rule as ">=80% progress AND a passed final exam". These
	# four pin that boundary. The first, third and fourth are RED until T2.2
	# replaces the hard-coded 100 with a configurable threshold.

	def test_exactly_80_with_a_passed_final_is_eligible(self):
		"""D1: exactly 80 plus a passed final must certify.

		Fails today: `lms_certificate.py:227` is `if progress < 100`, so 80 is
		refused with "You have not completed the course yet."
		"""
		exam = self._create_exam()
		self._record_submission(exam, 90)
		self._set_progress(80)
		self._assert_eligible()

	def test_79_9_with_a_passed_final_is_not_eligible(self):
		"""D1: 79.9 is below the threshold and must still be refused.

		Passes today and must keep passing. Asserting the message keeps it
		honest — it has to fail on *progress*, not slide through the exam gate.
		"""
		exam = self._create_exam()
		self._record_submission(exam, 90)
		self._set_progress(79.9)
		with self.assertRaises(frappe.exceptions.ValidationError) as caught:
			validate_certification_eligibility(self.course.name)
		self.assertIn("not completed", str(caught.exception))

	def test_over_80_with_a_failed_final_is_not_eligible(self):
		"""D1: progress alone is not enough; the final exam must be passed.

		Fails today, and diagnostically so: the throw is about progress, so the
		message says "not completed" rather than "final exam". Once the
		threshold is 80 this student clears progress and is stopped by the exam
		gate instead.
		"""
		self._create_exam()
		self._set_progress(90)
		with self.assertRaises(frappe.exceptions.ValidationError) as caught:
			validate_certification_eligibility(self.course.name)
		self.assertIn("final exam", str(caught.exception))

	def test_over_80_with_no_final_required_is_eligible(self):
		"""D1: a course with no final exam certifies on progress alone.

		Fails today: the course has no `LMS Exam`, so the exam gate is skipped
		and the only thing refusing this student is the hard-coded 100.
		"""
		self._set_progress(90)
		self._assert_eligible()

	def test_doctype_accepts_over_100(self):
		"""`lms_certificate.py:94` already accepts >100, so a manual issue works."""
		self._set_progress(101.613)

		certificate = frappe.new_doc("LMS Certificate")
		certificate.update(
			{
				"member": self.student.email,
				"course": self.course.name,
				"issue_date": frappe.utils.nowdate(),
				"template": get_default_certificate_template(),
			}
		)
		certificate.save(ignore_permissions=True)
		self.cleanup_items.append(("LMS Certificate", certificate.name))
		self.assertTrue(frappe.db.exists("LMS Certificate", certificate.name))

	def test_create_certificate_returns_for_an_over_100_student(self):
		"""End-to-end through the whitelisted API; also already succeeds today."""
		self._set_progress(101.613)

		certificate = create_certificate(self.course.name)
		self.cleanup_items.append(("LMS Certificate", certificate.name))
		self.assertTrue(certificate)
		self.assertTrue(
			frappe.db.exists(
				"LMS Certificate", {"course": self.course.name, "member": self.student.email}
			)
		)

	# --- T2.7: the enrolment -> certificate link --------------------------

	def test_issuing_a_certificate_links_it_from_the_enrolment(self):
		"""T2.7: `LMS Enrollment.certificate` must point at the issued certificate.

		The field exists and is NULL for every row — nothing has ever written it,
		so any "who is certified" query that joins on it under-reports. That
		matters before T3.6 issues certificates in bulk.

		Fails today: the link stays empty.
		"""
		self._set_progress(101.613)

		certificate = create_certificate(self.course.name)
		self.cleanup_items.append(("LMS Certificate", certificate.name))

		self.assertEqual(
			frappe.db.get_value(
				"LMS Enrollment",
				{"course": self.course.name, "member": self.student.email},
				"certificate",
			),
			certificate.name,
		)

	# --- T2.8: the inert autoname Property Setter -------------------------

	def test_certificate_names_are_hashes_not_a_property_setter_series(self):
		"""T2.8: the `autoname = ####` Property Setter is inert.

		`LMS Certificate.autoname()` is a controller *method*, and frappe's
		`set_new_name` runs a declared method before it ever consults the
		DocType's `autoname` property — so the setter never executes and live
		names are 10-character hashes.

		This one is a safety net rather than a reproducer: it passes before the
		setter is removed, and its job is to still pass afterwards, proving the
		removal changed nothing. Deleting stale configuration without that check
		is how naming silently changes.
		"""
		self._set_progress(101.613)

		certificate = create_certificate(self.course.name)
		self.cleanup_items.append(("LMS Certificate", certificate.name))

		self.assertRegex(certificate.name, r"^[a-z0-9]{10}$")
		self.assertNotRegex(certificate.name, r"^\d+$")
