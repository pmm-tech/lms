# Copyright (c) 2026, Frappe and Contributors
# See license.txt

import unittest

import frappe


class TestLMSWordHuntActivity(unittest.TestCase):
	def test_total_marks_are_calculated(self):
		activity = frappe.get_doc(
			{
				"doctype": "LMS Word Hunt Activity",
				"title": "Word Hunt Marks Activity",
				"passing_percentage": 100,
				"passage": "I _______ to school and _______ lunch there.",
				"items": [
					{
						"doctype": "LMS Word Hunt Item",
						"correct_answer": "go",
						"marks": 2,
					},
					{
						"doctype": "LMS Word Hunt Item",
						"correct_answer": "eat",
						"marks": 3,
					},
				],
			}
		)
		activity.insert()
		self.assertEqual(activity.total_marks, 5)

	def test_passage_blank_count_must_match_items(self):
		activity = frappe.get_doc(
			{
				"doctype": "LMS Word Hunt Activity",
				"title": "Mismatched Blank Count Activity",
				"passing_percentage": 100,
				"passage": "I _______ to school and _______ lunch there.",
				"items": [
					{
						"doctype": "LMS Word Hunt Item",
						"correct_answer": "go",
						"marks": 1,
					}
				],
			}
		)

		with self.assertRaises(frappe.ValidationError):
			activity.insert()

	def test_requires_passage_blank(self):
		activity = frappe.get_doc(
			{
				"doctype": "LMS Word Hunt Activity",
				"title": "Invalid Passage Activity",
				"passing_percentage": 100,
				"passage": "This passage has no blanks.",
				"items": [
					{
						"doctype": "LMS Word Hunt Item",
						"correct_answer": "go",
						"marks": 1,
					}
				],
			}
		)

		with self.assertRaises(frappe.ValidationError):
			activity.insert()

	def test_single_underscore_counts_as_blank(self):
		activity = frappe.get_doc(
			{
				"doctype": "LMS Word Hunt Activity",
				"title": "Single Underscore Activity",
				"passing_percentage": 100,
				"passage": "I _ to school.",
				"items": [
					{
						"doctype": "LMS Word Hunt Item",
						"correct_answer": "go",
						"marks": 1,
					}
				],
			}
		)
		activity.insert()
		self.assertEqual(activity.total_marks, 1)
