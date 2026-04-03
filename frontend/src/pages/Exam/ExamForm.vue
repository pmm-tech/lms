<template>
	<header class="sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5">
		<Breadcrumbs :items="breadcrumbs" />
		<div v-if="!readOnlyMode" class="flex items-center space-x-2">
			<Badge v-if="examDetails.isDirty" theme="orange">{{ __('Not Saved') }}</Badge>
			<router-link v-if="examDetails.doc?.name" :to="{ name: 'ExamPage', params: { examID: examDetails.doc.name } }">
				<Button>{{ __('Test Exam') }}</Button>
			</router-link>
			<router-link v-if="examDetails.doc?.name" :to="{ name: 'ExamSubmissionList', params: { examID: examDetails.doc.name } }">
				<Button>{{ __('Check Submissions') }}</Button>
			</router-link>
			<Button variant="solid" @click="submitExam">{{ __('Save') }}</Button>
		</div>
	</header>
	<div v-if="examDetails.doc" class="py-5">
		<div class="px-20 pb-5 space-y-5 border-b mb-5">
			<div class="text-lg text-ink-gray-9 font-semibold mb-4">{{ __('Details') }}</div>
			<div class="grid grid-cols-2 gap-5">
				<div class="space-y-5">
					<FormControl v-model="examDetails.doc.title" :label="__('Title')" :required="true" />
					<FormControl type="select" v-model="examDetails.doc.course" :options="courseOptions" :label="__('Course')" />
					<FormControl type="select" v-model="examDetails.doc.display_chapter" :options="chapterOptions" :label="__('Display Chapter')" />
					<FormControl type="number" v-model="examDetails.doc.max_attempts" :label="__('Maximum Attempts')" />
					<FormControl type="number" v-model="examDetails.doc.duration" :label="__('Duration (in minutes)')" />
					<FormControl type="datetime-local" v-model="examDetails.doc.available_from" :label="__('Available From')" />
				</div>
				<div class="space-y-5">
					<FormControl v-model="examDetails.doc.total_marks" :label="__('Total Marks')" disabled />
					<FormControl v-model="examDetails.doc.passing_percentage" :label="__('Passing Percentage')" :required="true" />
					<Switch v-model="examDetails.doc.is_final_exam" size="sm" :label="__('Final Exam')" />
					<Switch v-model="examDetails.doc.show_answers" size="sm" :label="__('Show Answers')" />
					<Switch v-model="examDetails.doc.show_submission_history" size="sm" :label="__('Show Submission History')" />
					<FormControl type="datetime-local" v-model="examDetails.doc.available_until" :label="__('Available Until')" />
				</div>
			</div>
			<div>
				<div class="text-sm text-ink-gray-5 mb-1">{{ __('Instructions') }}</div>
				<TextEditor
					:content="examDetails.doc.instructions || ''"
					@change="(val) => (examDetails.doc.instructions = val)"
					:editable="true"
					:fixedMenu="true"
					editorClass="prose-sm max-w-none border-b border-x border-outline-gray-modals bg-surface-gray-2 rounded-b-md py-1 px-2 min-h-[7rem]"
				/>
			</div>
		</div>

		<div class="px-20 pb-5 space-y-5 border-b mb-5">
			<div class="text-lg text-ink-gray-9 font-semibold mb-4">{{ __('Settings') }}</div>
			<div class="grid grid-cols-3 gap-5">
				<div class="flex flex-col space-y-5">
					<Switch v-model="examDetails.doc.shuffle_questions" size="sm" :label="__('Shuffle Questions')" />
					<FormControl
						v-if="examDetails.doc.shuffle_questions"
						v-model="examDetails.doc.limit_questions_to"
						:label="__('Limit Questions To')"
					/>
				</div>
				<div class="flex flex-col space-y-5">
					<Switch
						v-model="examDetails.doc.enable_negative_marking"
						size="sm"
						:label="__('Enable Negative Marking')"
					/>
					<FormControl
						v-if="examDetails.doc.enable_negative_marking"
						v-model="examDetails.doc.marks_to_cut"
						:label="__('Marks to Deduct')"
					/>
				</div>
				<div class="flex flex-col space-y-5">
					<div class="rounded-lg bg-surface-gray-2 p-4 text-sm text-ink-gray-6">
						{{ __('Prerequisites are checked before every attempt, and passing this exam is required for certification when the course has a final exam attached.') }}
					</div>
				</div>
			</div>
		</div>

		<div class="px-20 pb-5 space-y-5 border-b mb-5">
			<div class="text-lg text-ink-gray-9 font-semibold mb-4">{{ __('Prerequisites') }}</div>
			<div class="space-y-4">
				<div
					v-for="(row, index) in prerequisites"
					:key="index"
					class="grid grid-cols-4 gap-4 rounded-lg border p-4"
				>
					<FormControl type="select" v-model="row.requirement_type" :options="requirementTypeOptions" :label="__('Type')" />
					<FormControl
						v-if="row.requirement_type == 'Course Progress'"
						type="number"
						v-model="row.minimum_percentage"
						:label="__('Minimum %')"
					/>
					<FormControl
						v-else-if="row.requirement_type == 'Quiz'"
						type="select"
						v-model="row.quiz"
						:options="quizOptions"
						:label="__('Quiz')"
					/>
					<FormControl
						v-else
						type="select"
						v-model="row.drag_drop_activity"
						:options="dragDropOptions"
						:label="__('Drag & Drop Activity')"
					/>
					<FormControl
						v-if="row.requirement_type != 'Course Progress'"
						type="select"
						v-model="row.submission_requirement"
						:options="submissionRequirementOptions"
						:label="__('Requirement')"
					/>
					<div class="flex items-end">
						<Button theme="red" @click="removePrerequisite(index)">{{ __('Remove') }}</Button>
					</div>
				</div>
				<Button @click="addPrerequisite">{{ __('Add Prerequisite') }}</Button>
			</div>
		</div>

		<div class="px-20 pb-5 space-y-5 mb-5">
			<div class="flex items-center justify-between mb-4">
				<div class="text-lg font-semibold text-ink-gray-9">{{ __('Questions') }}</div>
				<Button v-if="!readOnlyMode" @click="openQuestionModal()">
					<template #prefix>
						<Plus class="w-4 h-4" />
					</template>
					{{ __('New Question') }}
				</Button>
			</div>
			<ListView v-if="questions.length" :columns="questionColumns" :rows="questions" row-key="question" :options="{ showTooltip: false }">
				<ListHeader class="mb-2 grid items-center space-x-4 rounded bg-surface-gray-2 p-2">
					<ListHeaderItem :item="item" v-for="item in questionColumns" :key="item.key" />
				</ListHeader>
				<ListRows>
					<ListRow v-for="row in questions" :key="row.question" :row="row" v-slot="{ column, item }" @click="openQuestionModal(row)" class="cursor-pointer">
						<ListRowItem :item="item">
							<div v-if="column.key == 'question_detail'" class="text-xs truncate h-4" v-html="item"></div>
							<div v-else class="text-xs">{{ item }}</div>
						</ListRowItem>
					</ListRow>
				</ListRows>
			</ListView>
			<div v-else class="text-ink-gray-6 text-sm">{{ __('No questions added yet') }}</div>
		</div>
	</div>

	<Question
		v-model="showQuestionModal"
		:questionDetail="currentQuestion"
		v-model:quiz="examDetails"
		:title="currentQuestion.question ? __('Edit Question') : __('Add Question')"
	/>
</template>

<script setup>
import {
	Badge,
	Breadcrumbs,
	Button,
	createDocumentResource,
	createResource,
	FormControl,
	ListHeader,
	ListHeaderItem,
	ListRow,
	ListRowItem,
	ListRows,
	ListView,
	Switch,
	TextEditor,
	toast,
	usePageMeta,
} from 'frappe-ui'
import { computed, inject, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { Plus } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { sessionStore } from '@/stores/session'
import { sanitizeHTML } from '@/utils'
import Question from '@/components/Modals/Question.vue'

const { brand } = sessionStore()
const user = inject('$user')
const router = useRouter()
const readOnlyMode = window.read_only_mode

const props = defineProps({
	examID: {
		type: String,
		required: true,
	},
})

const showQuestionModal = ref(false)
const currentQuestion = reactive({ question: '', marks: 0, name: '' })

const examDetails = createDocumentResource({
	doctype: 'LMS Exam',
	name: props.examID,
	auto: true,
})

const courses = createResource({
	url: 'frappe.client.get_list',
	params: {
		doctype: 'LMS Course',
		fields: ['name', 'title'],
		order_by: 'title asc',
	},
	auto: true,
})

const chapters = createResource({
	url: 'frappe.client.get_list',
	makeParams() {
		return {
			doctype: 'Course Chapter',
			fields: ['name', 'title'],
			filters: examDetails.doc?.course ? { course: examDetails.doc.course } : {},
			order_by: 'title asc',
		}
	},
	auto: false,
})

const quizzes = createResource({
	url: 'frappe.client.get_list',
	makeParams() {
		return {
			doctype: 'LMS Quiz',
			fields: ['name', 'title'],
			filters: examDetails.doc?.course ? { course: examDetails.doc.course } : {},
			order_by: 'title asc',
		}
	},
	auto: false,
})

const dragDrops = createResource({
	url: 'frappe.client.get_list',
	makeParams() {
		return {
			doctype: 'LMS Drag Drop Activity',
			fields: ['name', 'title'],
			filters: examDetails.doc?.course ? { course: examDetails.doc.course } : {},
			order_by: 'title asc',
		}
	},
	auto: false,
})

onMounted(() => {
	if (!user.data?.is_moderator && !user.data?.is_instructor) router.push({ name: 'Courses' })
	window.addEventListener('keydown', keyboardShortcut)
})

onBeforeUnmount(() => {
	window.removeEventListener('keydown', keyboardShortcut)
})

watch(
	() => examDetails.doc?.course,
	(course) => {
		if (course) {
			chapters.reload()
			quizzes.reload()
			dragDrops.reload()
		}
	}
)

const keyboardShortcut = (e) => {
	if (e.key === 's' && (e.ctrlKey || e.metaKey)) {
		submitExam()
		e.preventDefault()
	}
}

const questions = computed(() => examDetails.doc?.questions || [])
const prerequisites = computed(() => examDetails.doc?.prerequisites || [])
const courseOptions = computed(() => (courses.data || []).map((row) => ({ label: row.title, value: row.name })))
const chapterOptions = computed(() => [{ label: __('None'), value: '' }, ...(chapters.data || []).map((row) => ({ label: row.title, value: row.name }))])
const quizOptions = computed(() => (quizzes.data || []).map((row) => ({ label: row.title, value: row.name })))
const dragDropOptions = computed(() => (dragDrops.data || []).map((row) => ({ label: row.title, value: row.name })))
const requirementTypeOptions = [
	{ label: __('Course Progress'), value: 'Course Progress' },
	{ label: __('Quiz'), value: 'Quiz' },
	{ label: __('Drag Drop'), value: 'Drag Drop' },
]
const submissionRequirementOptions = [
	{ label: __('Attempted'), value: 'Attempted' },
	{ label: __('Passed'), value: 'Passed' },
]

const validateTitle = () => {
	examDetails.doc.title = sanitizeHTML((examDetails.doc.title || '').trim())
}

const calculateTotalMarks = () => {
	if (examDetails.doc?.limit_questions_to && examDetails.doc?.questions.length > 0) {
		return examDetails.doc.questions[0].marks * examDetails.doc.limit_questions_to
	}
	return (examDetails.doc?.questions || []).reduce((sum, question) => sum + parseInt(question.marks || 0), 0)
}

const submitExam = () => {
	validateTitle()
	examDetails.setValue.submit(
		{
			...examDetails.doc,
			total_marks: calculateTotalMarks(),
		},
		{
			onSuccess(data) {
				examDetails.doc.total_marks = data.total_marks
				toast.success(__('Exam updated successfully'))
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
			},
		}
	)
}

const openQuestionModal = (question = null) => {
	currentQuestion.question = question?.question || ''
	currentQuestion.marks = question?.marks || 0
	currentQuestion.name = question?.name || ''
	showQuestionModal.value = true
}

const addPrerequisite = () => {
	if (!examDetails.doc.prerequisites) examDetails.doc.prerequisites = []
	examDetails.doc.prerequisites.push({
		requirement_type: 'Course Progress',
		submission_requirement: 'Attempted',
		minimum_percentage: 100,
	})
}

const removePrerequisite = (index) => {
	examDetails.doc.prerequisites.splice(index, 1)
}

const questionColumns = computed(() => [
	{ label: __('Question'), key: 'question_detail', width: 4 },
	{ label: __('Marks'), key: 'marks', width: 1, align: 'center' },
	{ label: __('Type'), key: 'type', width: 1, align: 'center' },
])

const breadcrumbs = computed(() => [
	{ label: __('Exams'), route: { name: 'Exams' } },
	{ label: examDetails.doc?.title || props.examID },
])

usePageMeta(() => ({ title: examDetails.doc?.title || __('Exam'), icon: brand.favicon }))
</script>
