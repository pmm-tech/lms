<template>
	<div v-if="examContext.data?.exam">
		<div
			class="bg-surface-blue-2 text-ink-blue-3 space-y-2 p-3 mb-4 rounded-lg leading-5"
		>
			<div class="font-medium">
				{{
					__(
						'Please read the following instructions carefully before starting the exam'
					)
				}}
			</div>
			<ol class="list-decimal list-inside space-y-2">
				<li>
					{{
						__(
							'Do not refresh the page or close this window. If you do, the exam will be submitted automatically.'
						)
					}}
				</li>
				<li>
					{{
						__('This exam consists of {0} questions.').format(questions.length)
					}}
				</li>
				<li v-if="examContext.data.exam.duration">
					{{
						__(
							'Please ensure that you complete all the questions in {0} minutes.'
						).format(examContext.data.exam.duration)
					}}
				</li>
				<li v-if="examContext.data.exam.passing_percentage">
					{{
						__(
							'You will have to get {0}% correct answers in order to pass the exam.'
						).format(examContext.data.exam.passing_percentage)
					}}
				</li>
				<li v-if="examContext.data.status.max_attempts">
					{{
						__('You can attempt this exam {0}.').format(
							examContext.data.status.max_attempts == 1
								? '1 time'
								: `${examContext.data.status.max_attempts} times`
						)
					}}
				</li>
			</ol>
		</div>

		<div
			v-if="!examContext.data.status.can_attempt && !examSubmission.data"
			class="rounded-xl border border-outline-gray-2 bg-surface-white p-6 mb-4"
		>
			<div class="text-lg font-semibold text-ink-gray-9">
				{{ examContext.data.exam.title }}
			</div>
			<div class="mt-3 text-sm text-ink-gray-7">
				{{ examContext.data.status.locked_reason }}
			</div>
			<div
				v-if="examContext.data.status.prerequisites?.length"
				class="mt-5 space-y-2"
			>
				<div class="text-sm font-medium text-ink-gray-8">
					{{ __('Prerequisites') }}
				</div>
				<div
					v-for="item in examContext.data.status.prerequisites"
					:key="item.label"
					class="flex items-center justify-between rounded-lg bg-surface-gray-2 px-3 py-2 text-sm"
				>
					<span>{{ item.label }}</span>
					<Badge
						:theme="item.satisfied ? 'green' : 'orange'"
						:label="item.satisfied ? __('Ready') : __('Pending')"
					/>
				</div>
			</div>
		</div>

		<div
			v-if="examContext.data.exam.duration"
			class="flex flex-col space-x-1 my-4"
		>
			<div class="mb-2">
				<span class="text-ink-gray-9">{{ __('Time') }}:</span>
				<span class="font-semibold text-ink-gray-9">{{
					formatTimer(timer)
				}}</span>
			</div>
			<ProgressBar :progress="timerProgress" />
		</div>

		<div
			v-if="
				activeQuestion == 0 &&
				!examSubmission.data &&
				examContext.data.status.can_attempt
			"
		>
			<div class="border text-center p-20 rounded-md">
				<div class="font-semibold text-lg text-ink-gray-9">
					{{ examContext.data.exam.title }}
				</div>
				<div class="flex items-center justify-center space-x-2 mt-4">
					<Button
						v-if="
							!examContext.data.status.max_attempts ||
							examContext.data.status.attempts_used <
								examContext.data.status.max_attempts
						"
						variant="solid"
						@click="startExam"
					>
						{{ __('Start') }}
					</Button>
				</div>
			</div>
		</div>

		<div
			v-else-if="!examSubmission.data && examContext.data.status.can_attempt"
		>
			<div v-for="(question, qtidx) in questions" :key="question.question">
				<div
					v-if="qtidx == activeQuestion - 1 && questionDetails.data"
					class="border rounded-lg p-5"
				>
					<div class="flex justify-between">
						<div class="text-sm text-ink-gray-5">
							{{ __('Question {0}').format(activeQuestion) }} -
							{{ getInstructions(questionDetails.data) }}
						</div>
						<div class="text-ink-gray-9 text-sm font-semibold">
							{{ question.marks }}
							{{ question.marks == 1 ? __('Mark') : __('Marks') }}
						</div>
					</div>
					<div
						class="text-ink-gray-9 font-semibold mt-2 leading-5 [&_img]:max-h-[400px] [&_img]:w-auto [&_img]:object-contain"
						v-html="questionDetails.data.question"
					></div>
					<div
						v-if="questionDetails.data.type == 'Choices'"
						v-for="index in 4"
						:key="index"
					>
						<label
							v-if="questionDetails.data[`option_${index}`]"
							class="flex items-center bg-surface-gray-3 rounded-md p-3 mt-4 w-full cursor-pointer"
						>
							<input
								v-if="!showAnswers.length && !questionDetails.data.multiple"
								type="radio"
								:name="encodeURIComponent(questionDetails.data.question)"
								class="w-3.5 h-3.5"
								@change="markAnswer(index)"
								:checked="selectedOptions[index - 1]"
							/>
							<input
								v-else-if="!showAnswers.length && questionDetails.data.multiple"
								type="checkbox"
								:name="encodeURIComponent(questionDetails.data.question)"
								class="w-3.5 h-3.5"
								@change="markAnswer(index)"
								:checked="selectedOptions[index - 1]"
							/>
							<div
								v-else-if="examContext.data.exam.show_answers"
								v-for="(answer, idx) in showAnswers"
								:key="idx"
							>
								<div v-if="index - 1 == idx">
									<CheckCircle
										v-if="answer == 1"
										class="w-4 h-4 text-ink-green-2"
									/>
									<MinusCircle
										v-else-if="answer == 2"
										class="w-4 h-4 text-ink-green-2"
									/>
									<XCircle
										v-else-if="answer == 0"
										class="w-4 h-4 text-ink-red-3"
									/>
									<MinusCircle v-else class="w-4 h-4" />
								</div>
							</div>
							<span
								class="ml-2 text-ink-gray-9"
								v-html="questionDetails.data[`option_${index}`]"
							></span>
						</label>
						<div
							v-if="questionDetails.data[`explanation_${index}`]"
							class="mt-2 text-xs text-ink-gray-7"
							v-show="showAnswers.length"
						>
							{{ questionDetails.data[`explanation_${index}`] }}
						</div>
					</div>
					<div v-else-if="questionDetails.data.type == 'User Input'">
						<FormControl
							v-model="possibleAnswer"
							type="textarea"
							class="my-2"
						/>
						<div v-if="showAnswers.length">
							<Badge v-if="showAnswers[0]" :label="__('Correct')" theme="green">
								<template #prefix>
									<CheckCircle class="w-4 h-4 text-ink-green-2 mr-1" />
								</template>
							</Badge>
							<Badge v-else theme="red" :label="__('Incorrect')">
								<template #prefix>
									<XCircle class="w-4 h-4 text-ink-red-3 mr-1" />
								</template>
							</Badge>
						</div>
					</div>
					<div v-else>
						<TextEditor
							class="mt-4"
							:content="possibleAnswer"
							@change="(val) => (possibleAnswer = val)"
							:editable="true"
							:fixedMenu="true"
							editorClass="prose-sm max-w-none border-b border-x border-outline-gray-modals bg-surface-gray-2 rounded-b-md py-1 px-2 min-h-[7rem]"
						/>
					</div>
					<div class="flex items-center justify-between mt-8">
						<Checkbox
							:label="__('Mark for review')"
							:model-value="reviewQuestions.includes(activeQuestion) ? 1 : 0"
							@change="markForReview($event, activeQuestion)"
						/>
						<div class="flex items-center space-x-2">
							<Button
								@click="switchQuestion(activeQuestion - 1)"
								:disabled="activeQuestion == 1"
							>
								<template #icon>
									<ChevronLeft class="size-4 stroke-1.5" />
								</template>
							</Button>
							<span
								v-for="item in paginationWindow"
								:key="item"
								class="w-6 h-6 rounded-full flex items-center justify-center text-sm"
								:class="{
									'cursor-pointer': item !== '...',
									'bg-surface-gray-4 border border-outline-gray-5 font-medium':
										activeQuestion == item,
									'text-ink-gray-5': item === '...',
									'bg-surface-blue-3 text-ink-white':
										attemptedQuestions.includes(item) && activeQuestion != item,
									'bg-surface-gray-3 text-ink-gray-6':
										activeQuestion != item &&
										item !== '...' &&
										!attemptedQuestions.includes(item),
								}"
								@click="item !== '...' && switchQuestion(item)"
							>
								{{ item }}
							</span>
							<Button
								@click="switchQuestion(activeQuestion + 1)"
								:disabled="activeQuestion == questions.length"
							>
								<template #icon>
									<ChevronRight class="size-4 stroke-1.5" />
								</template>
							</Button>
						</div>
						<Button
							v-if="
								examContext.data.exam.show_answers &&
								!showAnswers.length &&
								questionDetails.data.type != 'Open Ended'
							"
							@click="checkAnswer"
						>
							{{ __('Check') }}
						</Button>
						<Button
							v-else-if="
								activeQuestion != questions.length &&
								examContext.data.exam.show_answers
							"
							@click="nextQuestion"
						>
							{{ __('Next') }}
						</Button>
						<Button v-else variant="solid" @click="handleSubmitClick()">
							{{ __('Submit') }}
						</Button>
					</div>
				</div>
			</div>
		</div>

		<div
			v-else-if="examSubmission.data"
			class="border rounded-lg p-20 text-center space-y-2"
		>
			<div class="text-2xl font-semibold text-ink-gray-9">
				{{
					examSubmission.data.pass ? __('Exam Passed') : __('Exam Submitted')
				}}
			</div>
			<div class="text-ink-gray-7">
				{{
					__('You scored {0} out of {1}.').format(
						examSubmission.data.score,
						examSubmission.data.score_out_of
					)
				}}
			</div>
			<div class="text-ink-gray-7">
				{{
					__('Percentage: {0}%').format(
						Math.round(examSubmission.data.percentage || 0)
					)
				}}
			</div>
		</div>
	</div>
</template>

<script setup>
import {
	Badge,
	Button,
	Checkbox,
	createResource,
	FormControl,
	TextEditor,
	toast,
} from 'frappe-ui'
import {
	CheckCircle,
	ChevronLeft,
	ChevronRight,
	MinusCircle,
	XCircle,
} from 'lucide-vue-next'
import { computed, inject, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { timeAgo } from '@/utils'
import ProgressBar from '@/components/ProgressBar.vue'

const props = defineProps({
	examName: {
		type: String,
		required: true,
	},
})

const user = inject('$user')
const activeQuestion = ref(0)
const currentQuestion = ref(null)
const selectedOptions = ref([0, 0, 0, 0])
const possibleAnswer = ref(null)
const reviewQuestions = ref([])
const attemptedQuestions = ref([])
const showAnswers = ref([])
const timer = ref(0)
let timerInterval = null
const questions = ref([])
const examContext = createResource({
	url: 'lms.lms.doctype.lms_exam.lms_exam.get_exam_context',
	makeParams() {
		return { exam: props.examName }
	},
	auto: true,
	cache: ['exam-context', props.examName],
	onSuccess(data) {
		populateQuestions(data.exam)
		setupTimer(data.exam)
	},
})

const answerCheck = createResource({
	url: 'lms.lms.doctype.lms_quiz.lms_quiz.check_answer',
	auto: false,
})

const attempts = createResource({
	url: 'frappe.client.get_list',
	makeParams() {
		return {
			doctype: 'LMS Exam Submission',
			filters: {
				member: user.data?.name,
				exam: props.examName,
			},
			fields: [
				'name',
				'creation',
				'score',
				'score_out_of',
				'percentage',
				'passing_percentage',
			],
			order_by: 'creation desc',
		}
	},
	transform(data) {
		data.forEach((submission, index) => {
			submission.creation = timeAgo(submission.creation)
			submission.idx = index + 1
		})
	},
})

const examSubmission = createResource({
	url: 'lms.lms.doctype.lms_exam.lms_exam.submit_exam',
	makeParams() {
		return {
			exam: props.examName,
			results: localStorage.getItem(storageKey.value),
		}
	},
	onSuccess() {
		examContext.reload()
		attempts.reload()
		if (timerInterval) clearInterval(timerInterval)
	},
	onError(err) {
		toast.error(err.messages?.[0] || err)
	},
})

const questionDetails = createResource({
	url: 'lms.lms.utils.get_question_details',
	makeParams() {
		return {
			question: currentQuestion.value,
		}
	},
})

const storageKey = computed(() => `exam:${props.examName}`)

const populateQuestions = (exam) => {
	if (!exam) return
	questions.value = exam.shuffle_questions
		? shuffleArray([...(exam.questions || [])])
		: exam.questions || []
	if (exam.shuffle_questions && exam.limit_questions_to) {
		questions.value = questions.value.slice(0, exam.limit_questions_to)
	}
}

const setupTimer = (exam) => {
	if (exam?.duration) {
		timer.value = parseInt(exam.duration) * 60
	}
}

const startTimer = () => {
	timerInterval = setInterval(() => {
		timer.value--
		if (timer.value <= 0) {
			clearInterval(timerInterval)
			submitExam()
		}
	}, 1000)
}

const timerProgress = computed(() => {
	const duration = parseInt(examContext.data?.exam?.duration || 0) * 60
	if (!duration) return 0
	return (timer.value / duration) * 100
})

const formatTimer = (seconds) => {
	const hrs = Math.floor(seconds / 3600)
		.toString()
		.padStart(2, '0')
	const mins = Math.floor((seconds % 3600) / 60)
		.toString()
		.padStart(2, '0')
	const secs = (seconds % 60).toString().padStart(2, '0')
	return hrs != '00' ? `${hrs}:${mins}:${secs}` : `${mins}:${secs}`
}

const shuffleArray = (array) => {
	for (let i = array.length - 1; i > 0; i--) {
		const j = Math.floor(Math.random() * (i + 1))
		;[array[i], array[j]] = [array[j], array[i]]
	}
	return array
}

watch(activeQuestion, (value) => {
	if (value > 0 && questions.value[value - 1]) {
		currentQuestion.value = questions.value[value - 1].question
		questionDetails.reload({}, { onSuccess: loadSavedAnswers })
	}
})

watch(
	() => props.examName,
	() => {
		examContext.reload()
		attempts.reload()
	}
)

const startExam = () => {
	activeQuestion.value = 1
	localStorage.removeItem(storageKey.value)
	if (examContext.data?.exam?.duration) startTimer()
}

const loadSavedAnswers = () => {
	let data = JSON.parse(localStorage.getItem(storageKey.value))
	if (!data) return
	let localQuestion = data.find((q) => q.question_name == currentQuestion.value)
	if (!localQuestion) return
	if (questionDetails.data.type == 'Choices') {
		localQuestion.answer.forEach((answer) => {
			for (let i = 1; i <= 4; i++) {
				if (questionDetails.data[`option_${i}`] == answer)
					selectedOptions.value[i - 1] = 1
			}
		})
	} else {
		possibleAnswer.value = localQuestion.answer[0]
	}
}

const markAnswer = (index) => {
	if (!questionDetails.data.multiple) {
		selectedOptions.value.splice(
			0,
			selectedOptions.value.length,
			...[0, 0, 0, 0]
		)
	}
	selectedOptions.value[index - 1] = selectedOptions.value[index - 1] ? 0 : 1
}

const getAnswers = () => {
	let answers = []
	if (questionDetails.data.type == 'Choices') {
		selectedOptions.value.forEach((value, index) => {
			if (value) answers.push(questionDetails.data[`option_${index + 1}`])
		})
	} else {
		answers.push(possibleAnswer.value)
	}
	return answers
}

const addToLocalStorage = () => {
	let examData = JSON.parse(localStorage.getItem(storageKey.value))
	let questionData = {
		question_name: currentQuestion.value,
		answer: getAnswers(),
	}
	if (examData) {
		let existingQuestion = examData.find(
			(q) => q.question_name == questionData.question_name
		)
		if (existingQuestion) existingQuestion.answer = questionData.answer
		else examData.push(questionData)
	} else {
		examData = [questionData]
	}
	localStorage.setItem(storageKey.value, JSON.stringify(examData))
}

const switchQuestion = (questionNumber) => {
	const answers = getAnswers()
	if (answers.length) {
		if (!attemptedQuestions.value.includes(activeQuestion.value)) {
			attemptedQuestions.value.push(activeQuestion.value)
		}
		addToLocalStorage()
		resetInputs()
	}
	if (questionNumber < 1 || questionNumber > questions.value.length) return
	activeQuestion.value = questionNumber
}

const resetInputs = () => {
	selectedOptions.value.splice(0, selectedOptions.value.length, ...[0, 0, 0, 0])
	showAnswers.value.length = 0
	possibleAnswer.value = null
}

const markForReview = (value, index) => {
	if (value && !reviewQuestions.value.includes(index))
		reviewQuestions.value.push(index)
	if (!value)
		reviewQuestions.value = reviewQuestions.value.filter(
			(item) => item !== index
		)
}

const handleSubmitClick = () => {
	if (
		questionDetails.data?.type == 'Open Ended' &&
		examContext.data.exam.show_answers
	) {
		addToLocalStorage()
	}
	submitExam()
}

const submitExam = () => {
	if (
		!examContext.data.exam.show_answers &&
		questionDetails.data?.type == 'Open Ended'
	) {
		addToLocalStorage()
	}
	examSubmission.submit()
}

const getInstructions = (question) => {
	if (question.type == 'Choices') {
		return question.multiple
			? __('Choose all correct options')
			: __('Choose the correct option')
	}
	if (question.type == 'User Input') return __('Type your answer')
	return __('Write your answer')
}

const checkAnswer = () => {
	const answers = getAnswers()
	if (!answers.length) {
		toast.warning(__('Please select an option'))
		return
	}

	answerCheck.submit(
		{
			question: currentQuestion.value,
			question_type: questionDetails.data.type,
			answers: JSON.stringify(answers),
		},
		{
			onSuccess(data) {
				if (questionDetails.data.type == 'Choices') {
					selectedOptions.value.forEach((option, index) => {
						if (option) {
							showAnswers.value[index] = option && data[index]
						} else if (data[index] == 2) {
							showAnswers.value[index] = 2
						} else {
							showAnswers.value[index] = undefined
						}
					})
				} else {
					showAnswers.value.push(data)
				}
				addToLocalStorage()
			},
		}
	)
}

const nextQuestion = () => {
	if (!examContext.data.exam.show_answers) return
	if (questionDetails.data?.type == 'Open Ended') addToLocalStorage()
	if (activeQuestion.value == questions.value.length) return
	activeQuestion.value = activeQuestion.value + 1
	resetInputs()
}

const paginationWindow = computed(() => {
	if (!questions.value.length) return []
	const total = questions.value.length
	const current = activeQuestion.value
	if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
	const pages = [1]
	const start = Math.max(2, current - 1)
	const end = Math.min(total - 1, current + 1)
	if (start > 2) pages.push('...')
	for (let i = start; i <= end; i++) pages.push(i)
	if (end < total - 1) pages.push('...')
	pages.push(total)
	return pages
})

const handleBeforeUnload = (event) => {
	if (activeQuestion.value > 0 && !examSubmission.data) {
		addToLocalStorage()
		event.preventDefault()
		event.returnValue = ''
	}
}

const handlePageHide = () => {
	if (activeQuestion.value > 0 && !examSubmission.data) {
		const params = new URLSearchParams({
			exam: props.examName,
			results: localStorage.getItem(storageKey.value),
		})
		navigator.sendBeacon(
			'/api/method/lms.lms.doctype.lms_exam.lms_exam.submit_exam?' +
				params.toString()
		)
	}
}

onMounted(() => {
	window.addEventListener('beforeunload', handleBeforeUnload)
	window.addEventListener('pagehide', handlePageHide)
	attempts.reload()
})

onBeforeUnmount(() => {
	window.removeEventListener('beforeunload', handleBeforeUnload)
	window.removeEventListener('pagehide', handlePageHide)
	if (timerInterval) clearInterval(timerInterval)
})
</script>
