<template>
	<header
		class="sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5"
	>
		<Breadcrumbs :items="breadcrumbs" />
		<div v-if="!readOnlyMode" class="flex items-center space-x-2">
			<router-link
				v-if="details.doc?.name"
				:to="{ name: 'WordHuntPage', params: { activityID: details.doc.name } }"
			>
				<Button>{{ __('Test Activity') }}</Button>
			</router-link>
			<router-link
				v-if="details.doc?.name"
				:to="{
					name: 'WordHuntSubmissionList',
					params: { activityID: details.doc.name },
				}"
			>
				<Button>{{ __('Check Submissions') }}</Button>
			</router-link>
			<Button variant="solid" @click="saveActivity()">{{ __('Save') }}</Button>
		</div>
	</header>
	<div v-if="details.doc" class="py-5">
		<div class="px-20 pb-5 space-y-5 border-b mb-5">
			<div class="text-lg text-ink-gray-9 font-semibold mb-4">
				{{ __('Details') }}
			</div>
			<div class="grid grid-cols-2 gap-5">
				<FormControl
					v-model="details.doc.title"
					:label="__('Title')"
					:required="true"
				/>
				<FormControl
					v-model="details.doc.total_marks"
					:label="__('Total Marks')"
					disabled
				/>
				<FormControl
					type="number"
					v-model="details.doc.max_attempts"
					:label="__('Maximum Attempts')"
				/>
				<FormControl
					type="number"
					v-model="details.doc.duration"
					:label="__('Duration (in minutes)')"
				/>
				<FormControl
					type="number"
					v-model="details.doc.passing_percentage"
					:label="__('Passing Percentage')"
					:required="true"
				/>
			</div>
		</div>

		<div class="px-20 pb-5 space-y-5 border-b mb-5">
			<div class="text-lg text-ink-gray-9 font-semibold mb-4">
				{{ __('Settings') }}
			</div>
			<div class="grid grid-cols-3 gap-5">
				<FormControl
					v-model="details.doc.show_answers"
					type="checkbox"
					:label="__('Show Answers')"
				/>
				<FormControl
					v-model="details.doc.show_submission_history"
					type="checkbox"
					:label="__('Show Submission History')"
				/>
				<FormControl
					v-model="details.doc.shuffle_answers"
					type="checkbox"
					:label="__('Shuffle Answers')"
				/>
			</div>
		</div>

		<div class="px-20 pb-5 space-y-5 border-b mb-5">
			<div class="text-lg text-ink-gray-9 font-semibold mb-4">
				{{ __('Passage') }}
			</div>
			<div
				class="rounded-lg border bg-surface-gray-1 p-4 text-sm text-ink-gray-7"
			>
				{{
					__(
						'Write the passage naturally and use underscores like _, __, or _______ wherever you want a blank.'
					)
				}}
			</div>
			<FormControl
				type="textarea"
				v-model="details.doc.passage"
				:label="__('Passage')"
				:required="true"
			/>
		</div>

		<div class="px-20 pb-5 space-y-5 mb-5">
			<div class="flex items-center justify-between mb-4">
				<div class="text-lg font-semibold text-ink-gray-9">
					{{ __('Blanks') }}
				</div>
				<Button v-if="!readOnlyMode" @click="addItem()">
					<template #prefix><Plus class="w-4 h-4" /></template>
					{{ __('New Row') }}
				</Button>
			</div>
			<div class="space-y-4">
				<div
					v-for="(item, idx) in details.doc.items"
					:key="item.name || idx"
					class="rounded-lg border p-4 space-y-4"
				>
					<div class="grid grid-cols-3 gap-4">
						<div
							class="rounded-lg border bg-surface-gray-1 px-3 py-2 text-sm text-ink-gray-7"
						>
							{{ __('Blank {0}').format(idx + 1) }}
						</div>
						<FormControl
							v-model="item.correct_answer"
							:label="__('Correct Answer')"
							:required="true"
						/>
						<FormControl
							type="number"
							v-model="item.marks"
							:label="__('Marks')"
							:required="true"
						/>
					</div>
					<Button v-if="!readOnlyMode" @click="removeItem(idx)">{{
						__('Remove')
					}}</Button>
				</div>
			</div>
		</div>
	</div>
</template>
<script setup>
import {
	Breadcrumbs,
	Button,
	createDocumentResource,
	FormControl,
	toast,
	usePageMeta,
} from 'frappe-ui'
import { computed, inject, onMounted, watch } from 'vue'
import { Plus } from 'lucide-vue-next'
import { sessionStore } from '@/stores/session'
import { useRouter } from 'vue-router'
import { escapeHTML } from '@/utils'

const { brand } = sessionStore()
const user = inject('$user')
const router = useRouter()
const readOnlyMode = window.read_only_mode

const props = defineProps({
	activityID: {
		type: String,
		required: true,
	},
})

onMounted(() => {
	if (!user.data?.is_moderator && !user.data?.is_instructor) {
		router.push({ name: 'Courses' })
	}
	details.reload()
})

const details = createDocumentResource({
	doctype: 'LMS Word Hunt Activity',
	name: props.activityID,
	auto: false,
})

watch(
	() => details.doc?.duration,
	(duration) => {
		if (
			details.doc &&
			(duration === undefined || duration === null || duration === '')
		) {
			details.doc.duration = 0
		}
	},
	{ immediate: true }
)

const addItem = () => {
	if (!details.doc.items) {
		details.doc.items = []
	}
	details.doc.items.push({
		doctype: 'LMS Word Hunt Item',
		correct_answer: '',
		marks: 1,
	})
}

const removeItem = (index) => {
	details.doc.items.splice(index, 1)
}

const calculateTotalMarks = () => {
	return (details.doc.items || []).reduce(
		(total, item) => total + (parseInt(item.marks) || 0),
		0
	)
}

const saveActivity = () => {
	details.doc.title = escapeHTML(details.doc.title.trim())
	details.doc.passage = (details.doc.passage || '').trim()
	details.doc.items = (details.doc.items || []).map((item) => ({
		...item,
		correct_answer: escapeHTML((item.correct_answer || '').trim()),
	}))

	details.setValue.submit(
		{
			...details.doc,
			total_marks: calculateTotalMarks(),
		},
		{
			onSuccess(data) {
				details.doc.total_marks = data.total_marks
				toast.success(__('Activity updated successfully'))
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
			},
		}
	)
}

const breadcrumbs = computed(() => [
	{ label: __('Word Hunt Activities'), route: { name: 'WordHuntActivities' } },
	{
		label: details.doc?.title,
		route: { name: 'WordHuntForm', params: { activityID: props.activityID } },
	},
])

usePageMeta(() => ({
	title: details.doc?.title,
	icon: brand.favicon,
}))
</script>
