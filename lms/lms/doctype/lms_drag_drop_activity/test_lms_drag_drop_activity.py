# Copyright (c) 2026, Frappe and Contributors
# See license.txt

import unittest

import frappe


class TestLMSDragDropActivity(unittest.TestCase):
	def test_total_marks_are_calculated(self):
		activity = frappe.get_doc(
			{
				"doctype": "LMS Drag Drop Activity",
				"title": "Marks Activity",
				"passing_percentage": 100,
				"items": [
					{
						"doctype": "LMS Drag Drop Item",
						"prompt_before": "This is",
						"prompt_after": "a test.",
						"correct_answer": "Answer",
						"marks": 2,
					},
					{
						"doctype": "LMS Drag Drop Item",
						"prompt_before": "This is another",
						"prompt_after": "test.",
						"correct_answer": "Another",
						"marks": 3,
					},
				],
			}
		)
		activity.insert()
		self.assertEqual(activity.total_marks, 5)
