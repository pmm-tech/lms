<template>
	<header class="sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5">
		<Breadcrumbs :items="breadcrumbs" />
		<Button v-if="!readOnlyMode" variant="solid" @click="showForm = true">
			<template #prefix>
				<Plus class="w-4 h-4" />
			</template>
			{{ __('Create') }}
		</Button>
	</header>
	<div class="py-5 mx-5">
		<div class="flex items-center justify-between mb-4">
			<div class="text-lg font-semibold text-ink-gray-7">
				{{ totalActivities.data ? __('{0} Activities').format(totalActivities.data) : (totalActivities.loading ? __('Loading...') : __('No Activities')) }}
			</div>
			<FormControl v-model="search" type="text" :placeholder="__('Search')" />
		</div>
		<ListView
			v-if="activities.data?.length"
			:columns="columns"
			:rows="activities.data"
			row-key="name"
			:options="{ showTooltip: false, selectable: true }"
		>
			<ListHeader class="mb-2 grid items-center space-x-4 rounded bg-surface-gray-2 p-2">
				<ListHeaderItem :item="item" v-for="item in columns" />
			</ListHeader>
			<ListRows>
				<router-link
					v-for="row in activities.data"
					:to="{ name: 'DragDropForm', params: { activityID: row.name } }"
				>
					<ListRow :row="row" />
				</router-link>
			</ListRows>
		</ListView>
		<EmptyState v-else type="Drag & Drop Activities" />
		<div ref="loadMoreRef" class="h-2 w-full"></div>
		<div v-if="activities.loading" class="flex items-center justify-center py-5">
			<LoadingIndicator class="w-8 h-8 text-gray-400" />
		</div>
	</div>
	<Dialog
		v-model="showForm"
		:options="{
			title: __('Create a Drag & Drop Activity'),
			size: 'sm',
			actions: [{ label: __('Save'), variant: 'solid', onClick({ close }) { insertActivity(close) } }],
		}"
	>
		<template #body-content>
			<FormControl v-model="title" :label="__('Title')" type="text" @keydown.enter="insertActivity(() => (showForm = false))" />
		</template>
	</Dialog>
</template>
<script setup>
import {
	Breadcrumbs,
	Button,
	createListResource,
	createResource,
	Dialog,
	FormControl,
	ListHeader,
	ListHeaderItem,
	ListRow,
	ListRows,
	ListView,
	LoadingIndicator,
	toast,
	usePageMeta,
} from 'frappe-ui'
import { computed, inject, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { Plus } from 'lucide-vue-next'
import { sessionStore } from '@/stores/session'
import { useRouter, useRoute } from 'vue-router'
import { escapeHTML } from '@/utils'
import EmptyState from '@/components/EmptyState.vue'

const { brand } = sessionStore()
const user = inject('$user')
const dayjs = inject('$dayjs')
const router = useRouter()
const route = useRoute()
const search = ref('')
const title = ref('')
const showForm = ref(false)
const readOnlyMode = window.read_only_mode
const filters = ref({})
const loadMoreRef = ref(null)
let observer

onMounted(() => {
	if (!user.data?.is_moderator && !user.data?.is_instructor) {
		router.push({ name: 'Courses' })
	} else if (!user.data?.is_moderator) {
		filters.value.owner = user.data?.name
	}
	if (route.query.new === 'true') {
		showForm.value = true
	}

	observer = new IntersectionObserver(
		(entries) => {
			if (entries[0].isIntersecting && activities.hasNextPage && !activities.loading) {
				activities.next()
			}
		},
		{ threshold: 1.0 }
	)

	if (loadMoreRef.value) {
		observer.observe(loadMoreRef.value)
	}
})

onBeforeUnmount(() => {
	if (observer) {
		observer.disconnect()
	}
})

watch(search, () => {
	filters.value.title = ['like', `%${search.value}%`]
	activities.update({ filters: filters.value })
	activities.reload()
	totalActivities.reload()
})

const activities = createListResource({
	doctype: 'LMS Drag Drop Activity',
	fields: ['name', 'title', 'passing_percentage', 'total_marks', 'modified'],
	filters: filters,
	auto: true,
	cache: ['drag-drop-activities', user.data?.name],
	orderBy: 'modified desc',
	transform(data) {
		return data.map((row) => ({ ...row, modified: dayjs(row.modified).fromNow() }))
	},
})

const totalActivities = createResource({
	url: 'frappe.client.get_count',
	params: {
		doctype: 'LMS Drag Drop Activity',
		filters: filters.value,
	},
	auto: true,
	cache: ['drag-drop-activities-count', user.data?.name],
})

const insertActivity = (close) => {
	title.value = escapeHTML(title.value.trim())
	activities.insert.submit(
		{
			title: title.value,
			passing_percentage: 100,
		},
		{
			onSuccess(data) {
				toast.success(__('Activity created successfully'))
				close()
				title.value = ''
				router.push({ name: 'DragDropForm', params: { activityID: data.name } })
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
			},
		}
	)
}

const columns = computed(() => [
	{ label: __('Title'), key: 'title', width: '20rem' },
	{ label: __('Passing %'), key: 'passing_percentage', align: 'center', width: '8rem' },
	{ label: __('Total Marks'), key: 'total_marks', align: 'center', width: '8rem' },
	{ label: __('Modified'), key: 'modified', align: 'right', width: '8rem' },
])

const breadcrumbs = computed(() => [{ label: __('Drag & Drop Activities'), route: { name: 'DragDropActivities' } }])

usePageMeta(() => ({
	title: __('Drag & Drop Activities'),
	icon: brand.favicon,
}))
</script>
