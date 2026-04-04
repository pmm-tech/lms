<template>
	<div v-if="activity.data">
		<div
			class="bg-surface-orange-1 space-y-2 py-2 px-3 mb-4 rounded-md text-sm text-ink-gray-8 leading-5"
		>
			<div>
				{{
					__('Read the full passage and place each word in the correct blank.')
				}}
			</div>
			<div>
				{{ __('This activity has {0} blanks.').format(items.length) }}
			</div>
			<div v-if="activity.data.passing_percentage">
				{{
					__('You need {0}% to pass.').format(activity.data.passing_percentage)
				}}
			</div>
			<div v-if="activity.data.max_attempts">
				{{
					__('You can attempt this activity {0}.').format(
						activity.data.max_attempts == 1
							? '1 time'
							: `${activity.data.max_attempts} times`
					)
				}}
			</div>
		</div>

		<div v-if="started && !submission.data" class="space-y-6">
			<div
				class="overflow-hidden rounded-2xl border border-transparent bg-gradient-to-br from-surface-blue-1 via-surface-orange-1 to-surface-green-1 p-1 shadow-sm"
			>
				<div
					class="rounded-[calc(1rem-1px)] bg-surface-white/90 p-4 backdrop-blur-sm"
				>
					<div class="mb-2 flex items-start justify-between gap-3">
						<div class="flex-1 space-y-1">
							<div
								class="flex items-center gap-1 text-sm font-semibold text-ink-gray-8"
							>
								<button
									v-if="isMobileView"
									type="button"
									class="flex h-5 w-5 items-center justify-center rounded-full text-[11px] font-bold text-ink-gray-7"
									@click="showMobileHint = !showMobileHint"
									:aria-label="__('Show answer bank instructions')"
									:aria-expanded="showMobileHint"
								>
									<Info class="h-3.5 w-3.5 stroke-2" />
								</button>
								{{ __('Answer Bank') }}
							</div>
							<div
								v-if="isMobileView && showMobileHint"
								class="max-w-[15rem] rounded-lg border border-outline-gray-2 bg-surface-white px-2 py-1.5 text-[10px] leading-4 text-ink-gray-7 shadow-sm"
							>
								{{ interactionHint }}
							</div>
							<div
								v-else-if="!isMobileView"
								class="text-[10px] leading-4 text-ink-gray-7 sm:text-sm sm:leading-5"
							>
								{{ interactionHint }}
							</div>
						</div>
						<div
							v-if="activity.data.duration"
							class="-mt-1 flex shrink-0 items-center justify-center self-start whitespace-nowrap rounded-md px-1 py-1 text-center text-[11px] font-semibold sm:mt-0 sm:min-w-[124px] sm:rounded-xl sm:px-2 sm:py-2 sm:text-base"
							style="background-color: #2a2a2a; color: #ffffff"
						>
							<span
								class="text-[10px] uppercase tracking-[0.05em] sm:text-xs"
								style="color: rgba(255, 255, 255, 0.82)"
							>
								{{ __('Time') }}
							</span>
							<span
								class="ml-1.5 text-[13px] font-bold sm:ml-2 sm:text-[22px] sm:leading-6"
								style="color: #ffffff"
							>
								{{ formatTimer(timer) }}
							</span>
						</div>
					</div>
					<ProgressBar
						v-if="activity.data.duration"
						:progress="timerProgress"
						class="mb-2"
					/>
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
					<div class="flex flex-wrap gap-3 pt-1.5">
						<button
							v-for="answer in availableAnswers"
							:key="answer.id"
							type="button"
							:draggable="!isTouchDevice"
							class="flex min-h-14 min-w-28 max-w-full items-center justify-center rounded-2xl px-4 py-3 text-center text-sm font-semibold text-white shadow-sm transition duration-150 ease-out hover:-translate-y-0.5 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-offset-2"
							:class="{
								'ring-2 ring-offset-2 scale-[1.02]':
									selectedAnswer?.id === answer.id,
								'cursor-grabbing opacity-80 scale-[0.98]':
									draggedAnswer?.id === answer.id,
								'cursor-pointer': draggedAnswer?.id !== answer.id,
							}"
							:style="answerButtonStyle(answer)"
							:aria-pressed="selectedAnswer?.id === answer.id"
							:aria-label="__('Select answer {0}').format(answer.label)"
							@click="selectAnswer(answer)"
							@dragstart="dragStart(answer)"
							@dragend="dragEnd"
						>
							<span
								class="min-w-0 max-w-full whitespace-normal break-all text-center leading-tight"
							>
								{{ answer.label }}
							</span>
						</button>
						<div
							v-if="!availableAnswers.length"
							class="rounded-xl border border-dashed border-outline-gray-2 bg-surface-gray-1 px-4 py-3 text-sm text-ink-gray-6"
						>
							{{ __('All answers have been placed.') }}
						</div>
					</div>
				</div>
			</div>

			<div
				class="rounded-xl border border-outline-gray-2 bg-surface-white p-3 shadow-sm sm:rounded-2xl sm:p-4"
			>
				<div class="flex items-center justify-between gap-3">
					<div class="text-xs text-ink-gray-6 sm:text-sm">
						{{ `${answeredCount} of ${items.length} ${__('answered')}` }}
					</div>
					<div
						class="text-xs sm:text-sm"
						:class="isReadyToSubmit ? 'text-ink-green-3' : 'text-ink-orange-3'"
					>
						{{
							isReadyToSubmit
								? __('Ready to submit')
								: __('Complete all blanks')
						}}
					</div>
				</div>
				<ProgressBar class="mt-2" :progress="itemProgress" />
			</div>

			<div
				class="rounded-2xl border border-outline-gray-2 bg-surface-white p-4 text-ink-gray-9 shadow-sm sm:p-6"
			>
				<div class="mb-4 text-sm font-semibold text-ink-gray-8">
					{{ __('Passage') }}
				</div>
				<div class="space-y-4 text-sm leading-8 sm:text-base">
					<div
						v-for="(segments, lineIndex) in renderedPassageLines"
						:key="`line-${lineIndex}`"
						class="flex flex-wrap items-center gap-2"
					>
						<template v-for="segment in segments" :key="segment.key">
							<span v-if="segment.type === 'text'" class="whitespace-pre-wrap">
								{{ segment.value }}
							</span>
							<span v-else class="inline-flex items-center gap-2">
								<button
									type="button"
									class="min-h-12 min-w-32 rounded-xl border-2 px-4 py-3 text-center text-sm font-medium transition duration-150 ease-out"
									:class="dropTargetClass(segment.item.name)"
									:aria-label="dropTargetAriaLabel(segment.item.name)"
									@click="placeSelected(segment.item.name)"
									@dragover.prevent
									@dragenter.prevent="activeDropTarget = segment.item.name"
									@dragleave.prevent="clearDropTarget(segment.item.name)"
									@drop.prevent="dropAnswer(segment.item.name)"
								>
									<template v-if="placements[segment.item.name]">
										<span>{{ placements[segment.item.name].label }}</span>
									</template>
									<span v-else>{{ __('Drop here') }}</span>
								</button>
								<Button
									v-if="placements[segment.item.name]"
									size="sm"
									variant="ghost"
									@click="removePlacement(segment.item.name)"
								>
									{{ __('Remove') }}
								</Button>
							</span>
						</template>
					</div>
				</div>
			</div>

			<div class="flex flex-wrap items-start gap-3">
				<div>
					<Button @click="resetActivity()">
						{{ __('Reset') }}
					</Button>
				</div>
				<div>
					<Button
						variant="solid"
						:disabled="!isReadyToSubmit"
						@click="submitActivity()"
					>
						{{ __('Submit') }}
					</Button>
				</div>
			</div>
		</div>

		<div
			v-else-if="submission.data"
			class="border rounded-md p-10 text-center space-y-3"
		>
			<div class="text-lg font-semibold text-ink-gray-9">
				{{ __('Activity Summary') }}
			</div>
			<div class="text-ink-gray-7">
				{{
					__('You scored {0} out of {1} ({2}%).').format(
						submission.data.score,
						submission.data.score_out_of,
						Math.ceil(submission.data.percentage)
					)
				}}
			</div>
			<div class="space-x-2">
				<Button
					v-if="
						!activity.data.max_attempts ||
						attempts.data?.length < activity.data.max_attempts
					"
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
			<div class="text-sm text-ink-gray-6 mt-3">
				{{ __('Fill every blank in the passage before submitting.') }}
			</div>
			<div class="flex items-center justify-center space-x-2 mt-4">
				<Button
					v-if="
						!activity.data.max_attempts ||
						attempts.data?.length < activity.data.max_attempts
					"
					variant="solid"
					@click="startActivity"
				>
					{{ __('Start') }}
				</Button>
			</div>
			<div
				v-if="
					activity.data.max_attempts &&
					attempts.data?.length >= activity.data.max_attempts
				"
				class="leading-5 text-ink-gray-7 mt-3"
			>
				{{
					__(
						'You have already exceeded the maximum number of attempts allowed for this activity.'
					)
				}}
			</div>
		</div>

		<div
			v-if="
				activity.data.show_submission_history &&
				attempts?.data &&
				attempts.data.length > 0
			"
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
import {
	computed,
	inject,
	onMounted,
	onBeforeUnmount,
	reactive,
	ref,
	watch,
} from 'vue'
import { Info } from 'lucide-vue-next'
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
const isMobileView = ref(false)
const showMobileHint = ref(false)
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
			doctype: 'LMS Word Hunt Activity',
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

const renderedPassageLines = computed(() => {
	const passage = activity.data?.passage || ''
	let blankIndex = 0
	return passage.split('\n').map((line, lineIndex) => {
		const parts = line.split(/(_+)/g).filter((value) => value !== '')
		return parts
			.map((part, partIndex) => {
				const isBlank = /^_+$/.test(part)
				if (!isBlank) {
					return {
						key: `text-${lineIndex}-${partIndex}`,
						type: 'text',
						value: part,
					}
				}

				const item = items.value[blankIndex]
				blankIndex++
				return {
					key: `blank-${lineIndex}-${partIndex}-${blankIndex}`,
					type: 'blank',
					item,
				}
			})
			.filter((segment) => segment.type === 'text' || segment.item)
	})
})

const answeredCount = computed(() => Object.keys(placements).length)
const isReadyToSubmit = computed(
	() => items.value.length > 0 && answeredCount.value === items.value.length
)
const itemProgress = computed(() =>
	items.value.length ? (answeredCount.value / items.value.length) * 100 : 0
)

const interactionHint = computed(() => {
	return isTouchDevice.value
		? __('Tap an answer, then tap the matching blank to place it.')
		: __('Choose an answer, then click a blank or drag it into place.')
})

const availableAnswers = computed(() =>
	answerBank.value.filter(
		(answer) =>
			!Object.values(placements).some((placed) => placed?.id === answer.id)
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
			doctype: 'LMS Word Hunt Submission',
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
	url: 'lms.lms.doctype.lms_word_hunt_activity.lms_word_hunt_activity.submit_activity',
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

const detectMobileView = () => {
	if (typeof window === 'undefined') return
	isMobileView.value = window.innerWidth < 640
	if (!isMobileView.value) showMobileHint.value = false
}

onMounted(() => {
	detectTouchDevice()
	detectMobileView()
	window.addEventListener('resize', detectTouchDevice)
	window.addEventListener('resize', detectMobileView)
})

onBeforeUnmount(() => {
	window.removeEventListener('resize', detectTouchDevice)
	window.removeEventListener('resize', detectMobileView)
})

watch(
	() => props.activityName,
	() => {
		activity.reload()
		resetActivity()
	}
)

const resetAnswerBank = () => {
	let answers = items.value.map((item) => ({
		label: item.correct_answer,
	}))
	if (activity.data?.shuffle_answers) {
		answers = [...answers].sort(() => Math.random() - 0.5)
	}
	answerBank.value = answers.map((answer, index) => ({
		id: `${index}-${answer.label}`,
		...answer,
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
	const secs = Math.max(seconds % 60, 0)
		.toString()
		.padStart(2, '0')
	return `${mins}:${secs}`
}

const startTimer = () => {
	timerInterval = setInterval(() => {
		timer.value--
		if (timer.value <= 0) {
			clearInterval(timerInterval)
			if (isReadyToSubmit.value) {
				submitActivity()
			} else {
				toast.warning(
					__(
						'Time is up. Please start again and complete all blanks before submitting.'
					)
				)
				resetActivity()
			}
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
	const isSelected = selectedAnswer.value?.id === answer.id
	const index = answerBank.value.findIndex((item) => item.id === answer.id)
	const palette = answerPalette[(index >= 0 ? index : 0) % answerPalette.length]

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
	started.value = false
	submission.reset()
	resetAnswerBank()
	if (timerInterval) clearInterval(timerInterval)
	setupTimer()
}

const submitActivity = () => {
	if (!isReadyToSubmit.value) {
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
