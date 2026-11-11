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

	def test_api_eligibility_accepts_over_100(self):
		"""`lms_certificate.py:227` already accepts >100. Guards against a `>=` edit."""
		self._set_progress(101.613)
		validate_certification_eligibility(self.course.name)  # must not throw

	def test_api_eligibility_still_refuses_below_100(self):
		"""The gate must still hold below 100 until D1 decides the real threshold."""
		self._set_progress(99.0)
		with self.assertRaises(frappe.exceptions.ValidationError):
			validate_certification_eligibility(self.course.name)

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
