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
			{{ __('Pass mark') }}: {{ exam.data?.passing_percentage ?? '—' }}%
			<span class="text-ink-gray-5">
				({{
					__('each attempt also records the pass mark in force at the time')
				}})
			</span>
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
							class="truncate text-ink-gray-6 underline"
						>
							{{ __('Attempt') }} {{ attempt.attempt_number }}
						</router-link>
						<span class="text-center text-ink-gray-5"></span>
						<span class="text-center text-ink-gray-6">{{ attempt.score }}</span>
						<span class="text-center text-ink-gray-6"
							>{{ attempt.percentage }}%</span
						>
						<span class="text-ink-gray-4"
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
	auto: true,
})

const exam = createResource({
	url: 'frappe.client.get_value',
	makeParams: () => ({
		doctype: 'LMS Exam',
		filters: { name: props.examID },
		fieldname: 'passing_percentage',
	}),
	auto: true,
})

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
