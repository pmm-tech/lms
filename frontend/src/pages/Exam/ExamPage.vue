<template>
	<header class="sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5">
		<Breadcrumbs :items="breadcrumbs" />
	</header>
	<div class="md:w-7/12 md:mx-auto mx-2 sm:mx-4 py-4 sm:py-10">
		<Exam :examName="examID" />
	</div>
</template>

<script setup>
import { Breadcrumbs, createResource, usePageMeta } from 'frappe-ui'
import { computed, inject, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { sessionStore } from '@/stores/session'
import Exam from '@/components/Exam.vue'

const { brand } = sessionStore()
const user = inject('$user')
const router = useRouter()

const props = defineProps({
	examID: {
		type: String,
		required: true,
	},
})

const title = createResource({
	url: 'frappe.client.get_value',
	params: {
		doctype: 'LMS Exam',
		fieldname: 'title',
		filters: {
			name: props.examID,
		},
	},
	auto: true,
})

const breadcrumbs = computed(() => [{ label: __('Exam') }, { label: title.data?.title }])

onMounted(() => {
	if (!user.data) {
		router.push({ name: 'Courses' })
	}
})

usePageMeta(() => ({ title: title.data?.title, icon: brand.favicon }))
</script>
