<template>
	<header class="sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5">
		<Breadcrumbs v-if="details.doc" :items="breadcrumbs" />
		<div class="space-x-2">
			<Button variant="solid" @click="saveSubmission()">{{ __('Save') }}</Button>
		</div>
	</header>
	<div v-if="details.doc" class="w-2/3 border-x mx-auto py-5">
		<div class="text-xl px-10 font-semibold text-ink-gray-9 mb-5">{{ details.doc.member_name }}</div>
		<div class="space-y-4 border-b pb-5 px-10">
			<div class="grid grid-cols-2 gap-5">
				<FormControl v-model="details.doc.activity_title" :label="__('Activity')" :disabled="true" />
				<FormControl v-model="details.doc.member_name" :label="__('Member')" :disabled="true" />
			</div>
			<div class="grid grid-cols-2 gap-5">
				<FormControl v-model="details.doc.score" :label="__('Score')" :disabled="true" />
				<FormControl v-model="details.doc.percentage" :label="__('Percentage')" :disabled="true" />
			</div>
		</div>
		<div class="divide-y">
			<div v-for="row in details.doc.result" class="py-5 px-10 space-y-4">
				<div class="text-ink-gray-9">
					<span class="font-semibold">{{ __('Prompt') }}: </span>
					<span>{{ row.prompt_before }} ____ {{ row.prompt_after }}</span>
				</div>
				<div class="grid grid-cols-2 gap-5">
					<FormControl v-model="row.submitted_answer" :label="__('Submitted Answer')" :disabled="true" />
					<FormControl v-model="row.correct_answer" :label="__('Correct Answer')" :disabled="true" />
				</div>
				<div class="grid grid-cols-2 gap-5">
					<FormControl v-model="row.marks" :label="__('Marks')" />
					<FormControl v-model="row.marks_out_of" :label="__('Marks out of')" :disabled="true" />
				</div>
			</div>
		</div>
	</div>
</template>
<script setup>
import { Breadcrumbs, Button, createDocumentResource, FormControl, toast, usePageMeta } from 'frappe-ui'
import { computed, inject, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { sessionStore } from '@/stores/session'

const { brand } = sessionStore()
const router = useRouter()
const user = inject('$user')

const props = defineProps({
	submission: {
		type: String,
		required: true,
	},
})

onMounted(() => {
	if (!user.data?.is_instructor && !user.data?.is_moderator) {
		router.push({ name: 'Courses' })
	}
})

const details = createDocumentResource({
	doctype: 'LMS Drag Drop Submission',
	name: props.submission,
	auto: true,
})

const saveSubmission = () => {
	details.save.submit(
		{},
		{
			onError(err) {
				toast.error(err.messages?.[0] || err)
			},
		}
	)
}

const breadcrumbs = computed(() => [
	{
		label: __('Drag & Drop Submissions'),
		route: { name: 'DragDropSubmissionList', params: { activityID: details.doc.activity } },
	},
	{ label: details.doc.activity_title },
])

usePageMeta(() => ({
	title: `${details.doc?.activity_title}`,
	icon: brand.favicon,
}))
</script>
