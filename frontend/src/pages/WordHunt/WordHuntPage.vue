<template>
	<header
		v-if="!fromLesson"
		class="sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5"
	>
		<Breadcrumbs :items="breadcrumbs" />
	</header>
	<div
		class="md:w-7/12 md:mx-auto mx-4 py-10"
		:class="{ 'pt-4 md:w-full': fromLesson }"
	>
		<WordHunt :activityName="activityID" />
	</div>
</template>
<script setup>
import WordHunt from '@/components/WordHunt.vue'
import { Breadcrumbs, createResource, usePageMeta } from 'frappe-ui'
import { computed, inject, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { sessionStore } from '@/stores/session'

const { brand } = sessionStore()
const user = inject('$user')
const router = useRouter()
const fromLesson = ref(false)

const props = defineProps({
	activityID: {
		type: String,
		required: true,
	},
})

onMounted(() => {
	if (!user.data) {
		router.push({ name: 'Courses' })
	}
	if (new URLSearchParams(window.location.search).get('fromLesson')) {
		fromLesson.value = true
	}
})

const title = createResource({
	url: 'frappe.client.get_value',
	params: {
		doctype: 'LMS Word Hunt Activity',
		fieldname: 'title',
		filters: { name: props.activityID },
	},
	auto: true,
})

const breadcrumbs = computed(() => [
	{ label: __('Word Hunt') },
	{ label: title.data?.title },
])

usePageMeta(() => ({
	title: `${title.data?.title}`,
	icon: brand.favicon,
}))
</script>
