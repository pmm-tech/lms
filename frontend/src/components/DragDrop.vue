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
			<div class="overflow-hidden rounded-2xl border border-transparent bg-gradient-to-br from-surface-blue-1 via-surface-orange-1 to-surface-green-1 p-1 shadow-sm">
				<div class="rounded-[calc(1rem-1px)] bg-surface-white/90 p-4 backdrop-blur-sm">
					<div class="mb-1 text-sm font-semibold text-ink-gray-8">
					{{ __('Answer Bank') }}
					</div>
					<div class="mb-4 text-sm leading-5 text-ink-gray-7">
						{{ interactionHint }}
					</div>
					<div
						v-if="selectedAnswer"
						class="mb-4 flex flex-col gap-3 rounded-2xl border border-green-200 bg-surface-green-1 px-4 py-3 text-sm text-ink-gray-8 sm:flex-row sm:items-center sm:justify-between"
					>
						<div class="flex items-center gap-2">
							<span class="font-medium">{{ __('Selected answer:') }}</span>
							<span>{{ selectedAnswer.label }}</span>
						</div>
						<Button size="sm" @click="clearSelectedAnswer()">
							{{ __('Clear Selection') }}
						</Button>
					</div>
					<div class="flex flex-wrap gap-3">
						<button
							v-for="answer in availableAnswers"
							:key="answer.id"
							type="button"
							:draggable="!isTouchDevice"
							class="min-h-12 rounded-xl px-4 py-3 text-sm font-semibold text-white shadow-sm transition duration-150 ease-out hover:-translate-y-0.5 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-offset-2"
							:class="{
								'ring-2 ring-offset-2 scale-[1.02]': selectedAnswer?.id === answer.id,
								'cursor-grabbing opacity-80 scale-[0.98]': draggedAnswer?.id === answer.id,
								'cursor-pointer': draggedAnswer?.id !== answer.id,
							}"
							:style="answerButtonStyle(answer)"
							:aria-pressed="selectedAnswer?.id === answer.id"
							:aria-label="__('Select answer {0}').format(answer.label)"
							@click="selectAnswer(answer)"
							@dragstart="dragStart(answer)"
							@dragend="dragEnd"
						>
							{{ answer.label }}
						</button>
					</div>
				</div>
			</div>

			<div class="rounded-2xl border border-outline-gray-2 bg-surface-white p-4 shadow-sm space-y-4">
				<div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
					<div>
						<div class="text-sm font-medium text-ink-gray-8">
							{{ __('Item {0} of {1}').format(currentItemIndex + 1, items.length) }}
						</div>
						<div class="mt-1 text-sm text-ink-gray-6">
							{{ __('{0} of {1} answered').format(answeredCount, items.length) }}
						</div>
					</div>
					<div class="text-sm" :class="currentItemAnswered ? 'text-ink-green-3' : 'text-ink-orange-3'">
						{{ currentItemAnswered ? __('Answered') : __('Unanswered') }}
					</div>
				</div>
				<ProgressBar :progress="itemProgress" />
			</div>

			<div v-if="currentItem" class="space-y-4">
				<div
					:key="currentItem.name"
					class="rounded-xl border border-outline-gray-2 bg-surface-white p-4 text-ink-gray-9 shadow-sm"
				>
					<div v-if="getItemDisplayType(currentItem) === 'Image'" class="space-y-4">
						<div class="overflow-hidden rounded-2xl border border-outline-gray-2 bg-surface-gray-1">
							<img
								:src="currentItem.image"
								:alt="currentItem.correct_answer"
								class="h-56 w-full object-contain bg-surface-white sm:h-72"
							/>
						</div>
						<div v-if="imagePromptText(currentItem)" class="text-sm leading-6 text-ink-gray-7">
							{{ imagePromptText(currentItem) }}
						</div>
						<button
							type="button"
							class="min-h-16 w-full rounded-2xl border-2 px-4 py-4 text-center text-sm font-medium transition duration-150 ease-out"
							:class="dropTargetClass(currentItem.name)"
							:aria-label="dropTargetAriaLabel(currentItem.name)"
							@click="placeSelected(currentItem.name)"
							@dragover.prevent
							@dragenter.prevent="activeDropTarget = currentItem.name"
							@dragleave.prevent="clearDropTarget(currentItem.name)"
							@drop.prevent="dropAnswer(currentItem.name)"
						>
							{{ placements[currentItem.name]?.label || __('Drop here') }}
						</button>
					</div>
					<div v-else class="flex flex-wrap items-center gap-2 leading-7">
						<span>{{ currentItem.prompt_before }}</span>
						<button
							type="button"
							class="min-h-12 min-w-36 rounded-xl border-2 px-4 py-3 text-center text-sm font-medium transition duration-150 ease-out"
							:class="dropTargetClass(currentItem.name)"
							:aria-label="dropTargetAriaLabel(currentItem.name)"
							@click="placeSelected(currentItem.name)"
							@dragover.prevent
							@dragenter.prevent="activeDropTarget = currentItem.name"
							@dragleave.prevent="clearDropTarget(currentItem.name)"
							@drop.prevent="dropAnswer(currentItem.name)"
						>
							{{ placements[currentItem.name]?.label || __('Drop here') }}
						</button>
						<span>{{ currentItem.prompt_after }}</span>
					</div>
					<div class="mt-2 text-xs text-ink-gray-6">
						{{ __('Marks: {0}').format(currentItem.marks) }}
					</div>
					<Button
						v-if="placements[currentItem.name]"
						class="mt-3"
						size="sm"
						@click="removePlacement(currentItem.name)"
					>
						{{ __('Remove') }}
					</Button>
				</div>
			</div>

			<div class="flex flex-wrap items-center justify-between gap-3">
				<div class="flex items-center gap-3">
					<Button v-if="!isFirstItem" @click="goToPreviousItem()">
						{{ __('Previous') }}
					</Button>
					<Button v-if="!isLastItem" variant="solid" @click="goToNextItem()">
						{{ __('Next') }}
					</Button>
				</div>
				<Button v-if="isLastItem" variant="solid" @click="submitActivity()">
					{{ __('Submit') }}
				</Button>
			</div>

			<div v-if="unansweredItems.length" class="rounded-2xl border border-outline-gray-2 bg-surface-gray-1 p-4 text-sm text-ink-gray-7">
				{{ __('Unanswered items: {0}').format(unansweredItems.join(', ')) }}
			</div>

			<div class="flex items-center gap-3">
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
import { computed, inject, onMounted, onBeforeUnmount, reactive, ref, watch } from 'vue'
import { timeAgo } from '@/utils'
import ProgressBar from '@/components/ProgressBar.vue'

const user = inject('$user')
const draggedAnswer = ref(null)
const selectedAnswer = ref(null)
const started = ref(false)
const timer = ref(0)
const answerBank = ref([])
const activeDropTarget = ref(null)
const isTouchDevice = ref(false)
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
const currentItemIndex = ref(0)

const getItemDisplayType = (item) => item.display_type || 'Text'

const imagePromptText = (item) => [item.prompt_before, item.prompt_after].filter(Boolean).join(' ')

const currentItem = computed(() => items.value[currentItemIndex.value] || null)

const answeredCount = computed(
	() => items.value.filter((item) => Boolean(placements[item.name])).length
)

const unansweredItems = computed(() =>
	items.value
		.filter((item) => !placements[item.name])
		.map((item, index) => index + 1)
)

const currentItemAnswered = computed(() =>
	currentItem.value ? Boolean(placements[currentItem.value.name]) : false
)

const isFirstItem = computed(() => currentItemIndex.value === 0)

const isLastItem = computed(() => currentItemIndex.value === Math.max(items.value.length - 1, 0))

const itemProgress = computed(() => {
	if (!items.value.length) return 0
	return ((currentItemIndex.value + 1) / items.value.length) * 100
})

const interactionHint = computed(() => {
	return isTouchDevice.value
		? __('Tap an answer, then tap the correct blank to place it.')
		: __('Choose an answer, then click a blank or drag it into place.')
})

const availableAnswers = computed(() =>
	answerBank.value.filter(
		(answer) => !Object.values(placements).some((placed) => placed?.id === answer.id)
	)
)

const answerPalette = [
	{
		background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
		borderColor: '#1d4ed8',
		ringColor: '#93c5fd',
		shadowColor: 'rgba(37, 99, 235, 0.28)',
	},
	{
		background: 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)',
		borderColor: '#ea580c',
		ringColor: '#fdba74',
		shadowColor: 'rgba(249, 115, 22, 0.28)',
	},
	{
		background: 'linear-gradient(135deg, #16a34a 0%, #15803d 100%)',
		borderColor: '#15803d',
		ringColor: '#86efac',
		shadowColor: 'rgba(22, 163, 74, 0.28)',
	},
	{
		background: 'linear-gradient(135deg, #db2777 0%, #be185d 100%)',
		borderColor: '#be185d',
		ringColor: '#f9a8d4',
		shadowColor: 'rgba(219, 39, 119, 0.28)',
	},
	{
		background: 'linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)',
		borderColor: '#6d28d9',
		ringColor: '#c4b5fd',
		shadowColor: 'rgba(124, 58, 237, 0.28)',
	},
	{
		background: 'linear-gradient(135deg, #0891b2 0%, #0e7490 100%)',
		borderColor: '#0e7490',
		ringColor: '#67e8f9',
		shadowColor: 'rgba(8, 145, 178, 0.28)',
	},
]

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

const detectTouchDevice = () => {
	if (typeof window === 'undefined') return

	isTouchDevice.value =
		window.matchMedia?.('(pointer: coarse)')?.matches ||
		window.matchMedia?.('(hover: none)')?.matches ||
		navigator.maxTouchPoints > 0
}

onMounted(() => {
	detectTouchDevice()
	window.addEventListener('resize', detectTouchDevice)
})

onBeforeUnmount(() => {
	window.removeEventListener('resize', detectTouchDevice)
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
	currentItemIndex.value = 0
	if (activity.data?.duration) startTimer()
}

const goToNextItem = () => {
	if (currentItemIndex.value < items.value.length - 1) {
		currentItemIndex.value++
	}
}

const goToPreviousItem = () => {
	if (currentItemIndex.value > 0) {
		currentItemIndex.value--
	}
}

const dragStart = (answer) => {
	draggedAnswer.value = answer
}

const dragEnd = () => {
	draggedAnswer.value = null
	activeDropTarget.value = null
}

const selectAnswer = (answer) => {
	selectedAnswer.value = selectedAnswer.value?.id === answer.id ? null : answer
}

const clearSelectedAnswer = () => {
	selectedAnswer.value = null
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
	activeDropTarget.value = null
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

const clearDropTarget = (itemName) => {
	if (activeDropTarget.value === itemName) {
		activeDropTarget.value = null
	}
}

const dropTargetAriaLabel = (itemName) => {
	if (placements[itemName]) {
		return __('Placed answer: {0}').format(placements[itemName].label)
	}

	if (selectedAnswer.value) {
		return __('Tap to place selected answer here')
	}

	return __('Drop or place an answer here')
}

const answerButtonStyle = (answer) => {
	const index = answerBank.value.findIndex((item) => item.id === answer.id)
	const palette = answerPalette[(index >= 0 ? index : 0) % answerPalette.length]
	const isSelected = selectedAnswer.value?.id === answer.id

	return {
		background: palette.background,
		border: `1px solid ${palette.borderColor}`,
		boxShadow: isSelected
			? `0 0 0 3px ${palette.ringColor}, 0 12px 24px ${palette.shadowColor}`
			: `0 10px 22px ${palette.shadowColor}`,
	}
}

const dropTargetClass = (itemName) => {
	if (placements[itemName]) {
		return 'border-orange-300 bg-surface-orange-1 text-ink-gray-9 shadow-sm'
	}

	if (activeDropTarget.value === itemName && draggedAnswer.value) {
		return 'border-blue-400 bg-surface-blue-1 text-ink-blue-3 border-dashed'
	}

	if (selectedAnswer.value) {
		return 'border-green-300 bg-surface-green-1 text-ink-gray-8'
	}

	return 'border-outline-gray-3 bg-surface-gray-1 text-ink-gray-5 border-dashed'
}

const resetActivity = () => {
	Object.keys(placements).forEach((key) => delete placements[key])
	selectedAnswer.value = null
	draggedAnswer.value = null
	activeDropTarget.value = null
	currentItemIndex.value = 0
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
