<template>
	<div v-if="activity.data">
		<div class="bg-surface-orange-1 space-y-2 py-2 px-3 mb-4 rounded-md text-sm text-ink-gray-8 leading-5">
			<div>
				{{ __('Match each answer card to the correct blank.') }}
			</div>
			<div>
				{{ __('This activity has {0} blanks.').format(items.length) }}
			</div>
			<div v-if="activity.data.passing_percentage">
				{{ __('You need {0}% to pass.').format(activity.data.passing_percentage) }}
			</div>
			<div v-if="activity.data.max_attempts">
				{{ __('You can attempt this activity {0}.').format(activity.data.max_attempts == 1 ? '1 time' : `${activity.data.max_attempts} times`) }}
			</div>
		</div>

		<div v-if="activity.data.duration" class="flex flex-col space-x-1 my-4">
			<div class="mb-2">
				<span class="text-ink-gray-9"> {{ __('Time') }}: </span>
				<span class="font-semibold text-ink-gray-9">
					{{ formatTimer(timer) }}
				</span>
			</div>
			<ProgressBar :progress="timerProgress" />
		</div>

		<div v-if="started && !submission.data" class="space-y-6">
			<div class="rounded-lg border bg-surface-gray-2 p-4">
				<div class="mb-2 text-sm font-medium text-ink-gray-7">
					{{ __('Answer Bank') }}
				</div>
				<div class="flex flex-wrap gap-3">
					<button
						v-for="answer in availableAnswers"
						:key="answer.id"
						type="button"
						draggable="true"
						class="rounded-md bg-surface-blue-5 px-4 py-2 text-white"
						@click="selectAnswer(answer)"
						@dragstart="dragStart(answer)"
					>
						{{ answer.label }}
					</button>
				</div>
			</div>

			<div class="space-y-4">
				<div
					v-for="item in items"
					:key="item.name"
					class="rounded-lg border p-4 text-ink-gray-9"
				>
					<div class="flex flex-wrap items-center gap-2 leading-7">
						<span>{{ item.prompt_before }}</span>
						<button
							type="button"
							class="min-w-28 rounded-md border-b-2 border-outline-gray-3 px-3 py-1 text-center"
							:class="{ 'bg-surface-orange-2': placements[item.name] }"
							@click="placeSelected(item.name)"
							@dragover.prevent
							@drop.prevent="dropAnswer(item.name)"
						>
							{{ placements[item.name]?.label || __('Drop here') }}
						</button>
						<span>{{ item.prompt_after }}</span>
					</div>
					<div class="mt-2 text-xs text-ink-gray-6">
						{{ __('Marks: {0}').format(item.marks) }}
					</div>
					<Button
						v-if="placements[item.name]"
						class="mt-3"
						size="sm"
						@click="removePlacement(item.name)"
					>
						{{ __('Remove') }}
					</Button>
				</div>
			</div>

			<div class="flex items-center gap-3">
				<Button variant="solid" @click="submitActivity()">
					{{ __('Submit') }}
				</Button>
				<Button @click="resetActivity()">
					{{ __('Reset') }}
				</Button>
			</div>
		</div>

		<div v-else-if="submission.data" class="border rounded-md p-10 text-center space-y-3">
			<div class="text-lg font-semibold text-ink-gray-9">
				{{ __('Activity Summary') }}
			</div>
			<div class="text-ink-gray-7">
				{{ __('You scored {0} out of {1} ({2}%).').format(submission.data.score, submission.data.score_out_of, Math.ceil(submission.data.percentage)) }}
			</div>
			<div class="space-x-2">
				<Button
					v-if="!activity.data.max_attempts || attempts.data?.length < activity.data.max_attempts"
					@click="resetActivity()"
				>
					{{ __('Try Again') }}
				</Button>
			</div>
		</div>

		<div v-else class="border text-center p-20 rounded-md">
			<div class="font-semibold text-lg text-ink-gray-9">
				{{ activity.data.title }}
			</div>
			<div class="flex items-center justify-center space-x-2 mt-4">
				<Button
					v-if="!activity.data.max_attempts || attempts.data?.length < activity.data.max_attempts"
					variant="solid"
					@click="startActivity"
				>
					{{ __('Start') }}
				</Button>
			</div>
			<div
				v-if="activity.data.max_attempts && attempts.data?.length >= activity.data.max_attempts"
				class="leading-5 text-ink-gray-7 mt-3"
			>
				{{ __('You have already exceeded the maximum number of attempts allowed for this activity.') }}
			</div>
		</div>

		<div
			v-if="activity.data.show_submission_history && attempts?.data && attempts.data.length > 0"
			class="mt-10"
		>
			<ListView
				:columns="submissionColumns"
				:rows="attempts.data"
				row-key="name"
				:options="{
					selectable: false,
					showTooltip: false,
					emptyState: { title: __('No submissions found') },
				}"
			/>
		</div>
	</div>
</template>
<script setup>
import { Button, createResource, ListView, toast, call } from 'frappe-ui'
import { computed, inject, reactive, ref, watch } from 'vue'
import { timeAgo } from '@/utils'
import ProgressBar from '@/components/ProgressBar.vue'

const user = inject('$user')
const draggedAnswer = ref(null)
const selectedAnswer = ref(null)
const started = ref(false)
const timer = ref(0)
const answerBank = ref([])
let timerInterval = null

const props = defineProps({
	activityName: {
		type: String,
		required: true,
	},
})

const placements = reactive({})

const activity = createResource({
	url: 'frappe.client.get',
	makeParams() {
		return {
			doctype: 'LMS Drag Drop Activity',
			name: props.activityName,
		}
	},
	auto: true,
	transform(data) {
		data.duration = parseInt(data.duration)
	},
	onSuccess() {
		resetAnswerBank()
		setupTimer()
		attempts.reload()
	},
})

const items = computed(() => activity.data?.items || [])

const availableAnswers = computed(() =>
	answerBank.value.filter(
		(answer) => !Object.values(placements).some((placed) => placed?.id === answer.id)
	)
)

const attempts = createResource({
	url: 'frappe.client.get_list',
	makeParams() {
		return {
			doctype: 'LMS Drag Drop Submission',
			filters: {
				member: user.data?.name,
				activity: activity.data?.name,
			},
			fields: ['name', 'creation', 'score', 'score_out_of', 'percentage'],
			order_by: 'creation desc',
		}
	},
	transform(data) {
		data.forEach((row, index) => {
			row.creation = timeAgo(row.creation)
			row.idx = index + 1
		})
	},
})

const submission = createResource({
	url: 'lms.lms.doctype.lms_drag_drop_activity.lms_drag_drop_activity.submit_activity',
	makeParams() {
		return {
			activity: activity.data.name,
			answers: JSON.stringify(
				items.value.map((item) => ({
					item: item.name,
					idx: item.idx,
					submitted_answer: placements[item.name]?.label || '',
				}))
			),
		}
	},
})

watch(
	() => props.activityName,
	() => {
		activity.reload()
		resetActivity()
	}
)

const resetAnswerBank = () => {
	let answers = items.value.map((item) => item.correct_answer)
	if (activity.data?.shuffle_answers) {
		answers = [...answers].sort(() => Math.random() - 0.5)
	}
	answerBank.value = answers.map((answer, index) => ({
		id: `${index}-${answer}`,
		label: answer,
	}))
}

const submissionColumns = [
	{ label: 'No.', key: 'idx' },
	{ label: 'Date', key: 'creation' },
	{ label: 'Score', key: 'score', align: 'center' },
	{ label: 'Score out of', key: 'score_out_of', align: 'center' },
	{ label: 'Percentage', key: 'percentage', align: 'center' },
]

const setupTimer = () => {
	if (activity.data?.duration) {
		timer.value = activity.data.duration * 60
	}
}

const timerProgress = computed(() => {
	if (!activity.data?.duration) return 0
	return (timer.value / (activity.data.duration * 60)) * 100
})

const formatTimer = (seconds) => {
	const mins = Math.floor((seconds % 3600) / 60)
		.toString()
		.padStart(2, '0')
	const secs = (seconds % 60).toString().padStart(2, '0')
	return `${mins}:${secs}`
}

const startTimer = () => {
	timerInterval = setInterval(() => {
		timer.value--
		if (timer.value <= 0) {
			clearInterval(timerInterval)
			submitActivity()
		}
	}, 1000)
}

const startActivity = () => {
	started.value = true
	if (activity.data?.duration) startTimer()
}

const dragStart = (answer) => {
	draggedAnswer.value = answer
}

const selectAnswer = (answer) => {
	selectedAnswer.value = answer
}

const placeAnswer = (itemName, answer) => {
	if (!answer) return

	Object.keys(placements).forEach((key) => {
		if (placements[key]?.id === answer.id) {
			delete placements[key]
		}
	})
	placements[itemName] = answer
	draggedAnswer.value = null
	selectedAnswer.value = null
}

const dropAnswer = (itemName) => {
	placeAnswer(itemName, draggedAnswer.value)
}

const placeSelected = (itemName) => {
	placeAnswer(itemName, selectedAnswer.value)
}

const removePlacement = (itemName) => {
	delete placements[itemName]
}

const resetActivity = () => {
	Object.keys(placements).forEach((key) => delete placements[key])
	selectedAnswer.value = null
	draggedAnswer.value = null
	started.value = false
	submission.reset()
	resetAnswerBank()
	if (timerInterval) clearInterval(timerInterval)
	setupTimer()
}

const submitActivity = () => {
	if (items.value.length && Object.keys(placements).length !== items.value.length) {
		toast.warning(__('Please place all answers before submitting.'))
		return
	}

	submission.submit(
		{},
		{
			onSuccess() {
				attempts.reload()
				if (timerInterval) clearInterval(timerInterval)
				markLessonProgress()
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
			},
		}
	)
}

const markLessonProgress = () => {
	let pathname = window.location.pathname.split('/')
	if (!pathname.includes('courses')) {
		pathname = window.parent.location.pathname.split('/')
	}
	if (!pathname.includes('courses')) return
	let lessonIndex = pathname.pop().split('-')

	if (lessonIndex.length == 2) {
		call('lms.lms.api.mark_lesson_progress', {
			course: pathname[3],
			chapter_number: lessonIndex[0],
			lesson_number: lessonIndex[1],
		})
	}
}
</script>
