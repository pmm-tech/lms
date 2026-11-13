<template>
	<header
		class="sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5"
	>
		<Breadcrumbs :items="breadcrumbs" />
	</header>
	<div v-if="groups.length" class="md:w-3/4 md:mx-auto py-5 mx-5">
		<div class="text-xl font-semibold mb-1 text-ink-gray-9">
			{{ submissions.data[0].exam_title }}
		</div>
		<!-- The exam's *current* pass mark, not the value frozen onto each
		     submission. 9 of 12 production rows store 100 while the exam says 80,
		     so a reader comparing a stored score against a stored pass mark is
		     comparing against a rule that no longer applies. -->
		<div class="text-sm text-ink-gray-6 mb-5">
			{{ __('Pass mark') }}: {{ passMark }}
			<span class="text-ink-gray-5">
				({{
					__('each attempt also records the pass mark in force at the time')
				}})
			</span>
		</div>

		<!-- Grouping happens in the browser over a single page of submissions, so
		     a page boundary silently corrupts every number below: a student outside
		     the window disappears, and everyone else's attempt count, best and last
		     are computed from a partial set. Saying so is the least this can do --
		     silently wrong per-student statistics are worse than a visible caveat. -->
		<div
			v-if="truncated"
			class="mb-4 rounded border border-outline-amber-2 bg-surface-amber-1 p-3 text-sm text-ink-amber-8"
		>
			{{
				__(
					'Showing the {0} most recent submissions only. Counts and best scores below cover just those, not the whole exam.',
					[submissions.data.length]
				)
			}}
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
				v-for="group in groups"
				:key="group.member"
				class="rounded border border-outline-gray-2 bg-surface-white"
			>
				<!-- One row per student, not per attempt. Attempts are nested
				     beneath so a student who sat the exam three times occupies one
				     row, which is what the list is read for. -->
				<!-- `data-testid` is deliberate. `aria-expanded` is already set for
				     accessibility, but frappe-ui's own components set it too, so it
				     cannot identify these rows in a test; and a layout class would
				     break on any restyle while proving nothing about behaviour. -->
				<button
					data-testid="exam-submission-student"
					class="grid w-full grid-cols-[2fr_1fr_1fr_1fr_auto] items-center gap-4 p-3 text-left hover:bg-surface-gray-2"
					:aria-expanded="expanded.has(group.member)"
					@click="toggle(group.member)"
				>
					<span class="truncate font-medium text-ink-gray-9">
						{{ group.member_name || group.member }}
					</span>
					<span class="text-center text-ink-gray-7">{{
						group.attempts.length
					}}</span>
					<span class="text-center text-ink-gray-7">{{ group.best }}%</span>
					<span class="text-center text-ink-gray-7"
						>{{ group.last.percentage }}%</span
					>
					<span class="text-ink-gray-5">
						{{ expanded.has(group.member) ? '−' : '+' }}
					</span>
				</button>

				<div
					v-if="expanded.has(group.member)"
					class="border-t border-outline-gray-1"
				>
					<div
						class="grid grid-cols-[2fr_1fr_1fr_1fr_auto] items-center gap-4 px-3 pt-2 text-xs font-medium text-ink-gray-5"
					>
						<span class="col-span-2">{{ __('Attempt') }}</span>
						<span class="text-center">{{ __('Score') }}</span>
						<span class="text-center">{{ __('Percentage') }}</span>
						<span class="text-right">{{ __('Pass mark') }}</span>
					</div>
					<div
						v-for="attempt in group.attempts"
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
							>{{ attempt.percentage }}%</span
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
import {
	Breadcrumbs,
	createListResource,
	createResource,
	usePageMeta,
} from 'frappe-ui'
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

const submissions = createListResource({
	doctype: 'LMS Exam Submission',
	filters: { exam: props.examID },
	fields: [
		'name',
		'member',
		'member_name',
		'score',
		'percentage',
		'passing_percentage',
		'exam_title',
		'attempt_number',
		'creation',
	],
	orderBy: 'creation desc',
	// Explicit, not the frappe-ui default of 20 that this previously inherited by
	// accident. `0` cannot mean "all" -- the source reads `options.pageLength || 20`,
	// so a falsy value falls back to 20. The bound is raised to cover every exam
	// this site has (A1 carries ~12 submissions) and is *surfaced* when reached
	// rather than trusted.
	pageLength: 500,
	auto: true,
})

// True when the page is full, which means the exam has at least this many
// submissions and the numbers below are computed over a subset.
const truncated = computed(() => (submissions.data?.length ?? 0) >= 500)

const exam = createResource({
	url: 'frappe.client.get_value',
	makeParams: () => ({
		doctype: 'LMS Exam',
		filters: { name: props.examID },
		fieldname: 'passing_percentage',
	}),
	auto: true,
})

const passMark = computed(() =>
	exam.data?.passing_percentage != null
		? `${exam.data.passing_percentage}%`
		: '—'
)

const expanded = ref(new Set())

function toggle(member) {
	// Reassigned rather than mutated: a Set mutated in place does not trigger a
	// re-render, so the row would silently refuse to open.
	const next = new Set(expanded.value)
	next.has(member) ? next.delete(member) : next.add(member)
	expanded.value = next
}

const groups = computed(() => {
	const byMember = new Map()
	for (const row of submissions.data || []) {
		if (!byMember.has(row.member)) byMember.set(row.member, [])
		byMember.get(row.member).push(row)
	}

	return [...byMember.entries()]
		.map(([member, attempts]) => {
			// `orderBy: creation desc` already, but sorting here keeps the values
			// correct if that ever changes upstream.
			const ordered = [...attempts].sort((a, b) =>
				String(b.creation).localeCompare(String(a.creation))
			)
			return {
				member,
				member_name: ordered[0].member_name,
				attempts: ordered,
				last: ordered[0],
				best: Math.max(...ordered.map((attempt) => attempt.percentage ?? 0)),
			}
		})
		.sort((a, b) => b.best - a.best)
})

const breadcrumbs = computed(() => [{ label: __('Exam Submissions') }])

usePageMeta(() => ({ title: __('Exam Submissions'), icon: brand.favicon }))
</script>
