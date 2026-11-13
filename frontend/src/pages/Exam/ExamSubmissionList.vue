<template>
	<header
		class="sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5"
	>
		<Breadcrumbs :items="breadcrumbs" />
	</header>
	<div v-if="groups.data?.length" class="md:w-3/4 md:mx-auto py-5 mx-5">
		<div class="text-xl font-semibold mb-1 text-ink-gray-9">
			{{ exam.data?.title || '' }}
		</div>
		<!-- The exam's *current* title and pass mark, not the values frozen onto
		     each submission. 9 of 12 production rows store a pass mark of 100 while
		     the exam says 80, and a renamed exam shows its old title on every row —
		     so reading either off a submission compares against a rule that no
		     longer applies. -->
		<div class="text-sm text-ink-gray-6 mb-5">
			{{ __('Pass mark') }}: {{ passMark }}
			<span class="text-ink-gray-5">
				({{
					__('each attempt also records the pass mark in force at the time')
				}})
			</span>
		</div>

		<div
			class="grid grid-cols-[2fr_1fr_1fr_1fr_auto] items-center gap-4 px-3 pb-1 text-xs font-medium text-ink-gray-5"
		>
			<span>{{ __('Student') }}</span>
			<span class="text-center">{{ __('Attempts') }}</span>
			<span class="text-center">{{ __('Best') }}</span>
			<span class="text-center">{{ __('Last attempt') }}</span>
			<span></span>
		</div>

		<div class="space-y-2">
			<div
				v-for="group in groups.data"
				:key="group.member"
				class="rounded border border-outline-gray-2 bg-surface-white"
			>
				<!-- One row per student, not per attempt. The row and its numbers come
				     from the server already grouped: aggregating in the browser meant
				     aggregating over a single page, so past that boundary a student
				     vanished and everyone else's numbers were computed from a partial
				     set. -->
				<!-- `data-testid` is deliberate. `aria-expanded` is already set for
				     accessibility, but frappe-ui's own components set it too, so it
				     cannot identify these rows in a test; and a layout class would
				     break on any restyle while proving nothing about behaviour. -->
				<button
					data-testid="exam-submission-student"
					class="grid w-full grid-cols-[2fr_1fr_1fr_1fr_auto] items-center gap-4 p-3 text-left hover:bg-surface-gray-2"
					:aria-expanded="expandedMember === group.member"
					@click="toggle(group.member)"
				>
					<span class="truncate font-medium text-ink-gray-9">
						{{ group.member_name || group.member }}
					</span>
					<span class="text-center text-ink-gray-7">{{ group.attempts }}</span>
					<span class="text-center text-ink-gray-7"
						>{{ round(group.best) }}%</span
					>
					<span class="text-center text-ink-gray-7"
						>{{ round(group.last_percentage) }}%</span
					>
					<span class="text-ink-gray-5">
						{{ expandedMember === group.member ? '−' : '+' }}
					</span>
				</button>

				<div
					v-if="expandedMember === group.member"
					class="border-t border-outline-gray-1"
				>
					<!-- Attempts are fetched for the expanded student only. Including
					     them in the grouped payload would make it grow with every
					     attempt ever recorded, which `max_attempts = 0` leaves
					     unbounded — the whole point of grouping on the server. -->
					<div
						class="grid grid-cols-[2fr_1fr_1fr_1fr_auto] items-center gap-4 px-3 pt-2 text-xs font-medium text-ink-gray-5"
					>
						<span class="col-span-2">{{ __('Attempt') }}</span>
						<span class="text-center">{{ __('Score') }}</span>
						<span class="text-center">{{ __('Percentage') }}</span>
						<span class="text-right">{{ __('Pass mark') }}</span>
					</div>
					<div
						v-for="attempt in attempts.data || []"
						:key="attempt.name"
						data-testid="exam-submission-attempt"
						class="grid grid-cols-[2fr_1fr_1fr_1fr_auto] items-center gap-4 px-3 py-2 text-sm"
					>
						<router-link
							:to="{
								name: 'ExamSubmission',
								params: { submission: attempt.name },
							}"
							class="col-span-2 truncate text-ink-gray-6 underline"
						>
							{{ __('Attempt') }} {{ attempt.attempt_number }}
						</router-link>
						<span class="text-center text-ink-gray-6">{{ attempt.score }}</span>
						<span class="text-center text-ink-gray-6"
							>{{ round(attempt.percentage) }}%</span
						>
						<span class="text-right text-ink-gray-4"
							>{{ attempt.passing_percentage }}%</span
						>
					</div>
				</div>
			</div>
		</div>
	</div>
	<EmptyState v-else type="Exam Submissions" />
</template>

<script setup>
import { Breadcrumbs, createResource, usePageMeta } from 'frappe-ui'
import { computed, inject, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { sessionStore } from '@/stores/session'
import EmptyState from '@/components/EmptyState.vue'

const { brand } = sessionStore()
const router = useRouter()
const user = inject('$user')

onMounted(() => {
	if (!user.data?.is_instructor && !user.data?.is_moderator)
		router.push({ name: 'Courses' })
})

const props = defineProps({
	examID: {
		type: String,
		required: true,
	},
})

// One row per student, aggregated server-side. Not `createListResource`: that
// pages, and a page boundary is exactly what corrupted the numbers when the
// grouping happened in the browser.
const groups = createResource({
	url: 'lms.lms.api.get_exam_submission_groups',
	makeParams: () => ({ exam: props.examID }),
	auto: true,
})

const exam = createResource({
	url: 'frappe.client.get_value',
	makeParams: () => ({
		doctype: 'LMS Exam',
		filters: { name: props.examID },
		// JSON-encoded: `get_value` mis-parses a bare array in frappe v15.
		fieldname: JSON.stringify(['passing_percentage', 'title']),
	}),
	auto: true,
})

// A student's own attempts, fetched when their row is opened. Bounded by that
// student's history rather than by the exam's total.
const attempts = createResource({
	url: 'frappe.client.get_list',
	makeParams: ({ member }) => ({
		doctype: 'LMS Exam Submission',
		filters: { exam: props.examID, member },
		fields: [
			'name',
			'score',
			'percentage',
			'passing_percentage',
			'attempt_number',
			'creation',
		],
		order_by: 'creation desc',
		limit_page_length: 0,
	}),
})

// `exam.data` is `{ message: {...} }` for `frappe.client.get_value`.
const passMark = computed(() => {
	const value =
		exam.data?.message?.passing_percentage ?? exam.data?.passing_percentage
	return value != null ? `${round(value)}%` : '—'
})

const expandedMember = ref(null)

function toggle(member) {
	if (expandedMember.value === member) {
		expandedMember.value = null
		return
	}
	expandedMember.value = member
	attempts.fetch({ member })
}

// `Math.max` returns the raw float, so a best of 2/3 would read
// "66.66666666666667%". One decimal is enough to distinguish a pass from a near
// miss and short enough to sit in a column.
function round(value) {
	if (value == null) return '—'
	return Math.round(Number(value) * 10) / 10
}

const breadcrumbs = computed(() => [{ label: __('Exam Submissions') }])

usePageMeta(() => ({ title: __('Exam Submissions'), icon: brand.favicon }))
</script>
