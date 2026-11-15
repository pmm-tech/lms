# Copyright (c) 2026, Frappe and Contributors
# See license.txt

import unittest

import frappe


class TestLMSDragDropActivity(unittest.TestCase):
	def test_total_marks_are_calculated(self):
		activity = frappe.get_doc(
			{
				"doctype": "LMS Drag Drop Activity",
				"title": f"Marks Activity {frappe.generate_hash(length=8)}",
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

	def test_image_item_is_valid_with_image(self):
		activity = frappe.get_doc(
			{
				"doctype": "LMS Drag Drop Activity",
				"title": f"Image Activity {frappe.generate_hash(length=8)}",
				"passing_percentage": 100,
				"items": [
					{
						"doctype": "LMS Drag Drop Item",
						"display_type": "Image",
						"image": "/files/example.png",
						"correct_answer": "Answer",
						"marks": 2,
					}
				],
			}
		)
		activity.insert()
		self.assertEqual(activity.total_marks, 2)

	def test_text_item_requires_prompt_text(self):
		activity = frappe.get_doc(
			{
				"doctype": "LMS Drag Drop Activity",
				"title": f"Invalid Text Activity {frappe.generate_hash(length=8)}",
				"passing_percentage": 100,
				"items": [
					{
						"doctype": "LMS Drag Drop Item",
						"display_type": "Text",
						"correct_answer": "Answer",
						"marks": 1,
					}
				],
			}
		)

		with self.assertRaises(frappe.ValidationError):
			activity.insert()

	def test_image_item_requires_image(self):
		activity = frappe.get_doc(
			{
				"doctype": "LMS Drag Drop Activity",
				"title": f"Invalid Image Activity {frappe.generate_hash(length=8)}",
				"passing_percentage": 100,
				"items": [
					{
						"doctype": "LMS Drag Drop Item",
						"display_type": "Image",
						"correct_answer": "Answer",
						"marks": 1,
					}
				],
			}
		)

		with self.assertRaises(frappe.ValidationError):
			activity.insert()
