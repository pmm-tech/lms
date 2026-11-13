import frappe


def execute():
	"""Index `(member, exam)` on LMS Exam Submission (T3.4).

	The submission list filters by exam and groups by member, and the table
	carried only `PRIMARY` and `modified` — so every per-student lookup was a
	full scan, growing with every attempt ever recorded. `max_attempts = 0`
	means attempts accumulate without limit, which is what made this worth an
	index rather than a note.

	Column order is `(member, exam)` to match how the list reads: it filters to
	one exam and then groups within it.

	`add_index` is idempotent — it checks `has_index` first and the DDL is
	`ADD INDEX IF NOT EXISTS` — so a re-run or a partially-applied migration is
	safe. It is deliberately two fields, not one: the single-field path in
	frappe's implementation also writes a `search_index` Property Setter, which
	is not wanted here.
	"""
	frappe.db.add_index("LMS Exam Submission", ["member", "exam"])
