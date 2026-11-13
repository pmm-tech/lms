import frappe


def execute():
	"""Index `(exam, member)` on LMS Exam Submission (T3.4).

	The submission list filters by exam, and the per-student lookups (attempt
	counts, last submission, pass check) constrain both exam and member; the
	table carried only `PRIMARY` and `modified` — so every per-student lookup
	was a full scan, growing with every attempt ever recorded. `max_attempts = 0`
	means attempts accumulate without limit, which is what made this worth an
	index rather than a note.

	Column order is `(exam, member)`: every query against this table constrains
	`exam` (the submission list by `exam` alone, the per-student lookups by both),
	so `exam` must lead for the list's filter to use the index. Grouping happens
	in the browser, so it does not constrain the column order.

	`add_index` is idempotent — it checks `has_index` first and the DDL is
	`ADD INDEX IF NOT EXISTS` — so a re-run or a partially-applied migration is
	safe. It is deliberately two fields, not one: the single-field path in
	frappe's implementation also writes a `search_index` Property Setter, which
	is not wanted here.
	"""
	frappe.db.add_index("LMS Exam Submission", ["exam", "member"])
