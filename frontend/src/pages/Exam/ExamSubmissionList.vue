<template>
	<header class="sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5">
		<Breadcrumbs :items="breadcrumbs" />
	</header>
	<div v-if="submissions.data?.length" class="md:w-3/4 md:mx-auto py-5 mx-5">
		<div class="text-xl font-semibold mb-5 text-ink-gray-9">{{ submissions.data[0].exam_title }}</div>
		<ListView :columns="examColumns" :rows="submissions.data" row-key="name" :options="{ showTooltip: false, selectable: false }">
			<ListHeader class="mb-2 grid items-center space-x-4 rounded bg-surface-gray-2 p-2">
				<ListHeaderItem :item="item" v-for="item in examColumns" :key="item.key" />
			</ListHeader>
			<ListRows>
				<router-link v-for="row in submissions.data" :key="row.name" :to="{ name: 'ExamSubmission', params: { submission: row.name } }">
					<ListRow :row="row" />
				</router-link>
			</ListRows>
		</ListView>
	</div>
	<EmptyState v-else type="Exam Submissions" />
</template>

<script setup>
import { Breadcrumbs, createListResource, ListHeader, ListHeaderItem, ListRow, ListRows, ListView, usePageMeta } from 'frappe-ui'
import { computed, inject, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { sessionStore } from '@/stores/session'
import EmptyState from '@/components/EmptyState.vue'

const { brand } = sessionStore()
const router = useRouter()
const user = inject('$user')

onMounted(() => {
	if (!user.data?.is_instructor && !user.data?.is_moderator) router.push({ name: 'Courses' })
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
	fields: ['name', 'member_name', 'score', 'percentage', 'exam_title', 'attempt_number'],
	orderBy: 'creation desc',
	auto: true,
})

const examColumns = computed(() => [
	{ label: __('Member'), key: 'member_name', width: 1 },
	{ label: __('Attempt'), key: 'attempt_number', width: 1, align: 'center' },
	{ label: __('Score'), key: 'score', width: 1, align: 'center' },
	{ label: __('Percentage'), key: 'percentage', width: 1, align: 'center' },
])

const breadcrumbs = computed(() => [{ label: __('Exam Submissions') }])

usePageMeta(() => ({ title: __('Exam Submissions'), icon: brand.favicon }))
</script>
