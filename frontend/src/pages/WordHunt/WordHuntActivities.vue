<template>
	<header
		class="sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5"
	>
		<Breadcrumbs :items="breadcrumbs" />
		<Button v-if="!readOnlyMode" variant="solid" @click="showForm = true">
			<template #prefix>
				<Plus class="w-4 h-4" />
			</template>
			{{ __('Create') }}
		</Button>
	</header>
	<div class="py-5 mx-5">
		<div class="flex items-center justify-between gap-4 mb-4">
			<div class="text-lg font-semibold text-ink-gray-7">
				{{
					totalActivities.loading
						? __('Loading...')
						: totalActivities.data
						? __('{0} Activities').format(totalActivities.data)
						: __('No Activities')
				}}
			</div>
			<FormControl
				v-model="search"
				type="text"
				:placeholder="__('Search by title')"
			/>
		</div>
		<div
			v-if="isInitialLoading"
			class="flex items-center justify-center rounded border bg-surface-white py-16"
		>
			<LoadingIndicator class="w-8 h-8 text-gray-400" />
		</div>
		<ListView
			v-else-if="activities.data?.length"
			:columns="columns"
			:rows="activities.data"
			row-key="name"
			:options="{
				showTooltip: false,
				selectable: false,
				onRowClick: (row) => openActivity(row.name),
			}"
		>
			<ListHeader
				class="mb-2 grid items-center space-x-4 rounded bg-surface-gray-2 p-2"
			>
				<ListHeaderItem :item="item" v-for="item in columns" />
			</ListHeader>
			<ListRows>
				<ListRow
					v-for="row in activities.data"
					:row="row"
					class="hover:bg-surface-gray-1"
				>
					<template #default="{ column }">
						<ListRowItem :item="row[column.key]" :align="column.align">
							<div
								v-if="column.key === 'modified'"
								class="text-sm text-ink-gray-5"
							>
								{{ row[column.key] }}
							</div>
							<div
								v-else-if="column.key === 'actions'"
								class="flex items-center justify-end gap-2"
							>
								<Button
									v-if="!readOnlyMode"
									size="sm"
									variant="ghost"
									@click.stop="openActivity(row.name)"
								>
									{{ __('Edit') }}
								</Button>
								<Button
									size="sm"
									variant="ghost"
									@click.stop="openSubmissions(row.name)"
								>
									{{ __('Submissions') }}
								</Button>
							</div>
							<div v-else>
								{{ row[column.key] }}
							</div>
						</ListRowItem>
					</template>
				</ListRow>
			</ListRows>
		</ListView>
		<div
			v-else-if="hasActiveSearch"
			class="rounded border bg-surface-white px-6 py-12 text-center"
		>
			<div class="text-lg font-semibold text-ink-gray-9">
				{{ __('No matching activities') }}
			</div>
			<div class="mt-2 text-ink-gray-7">
				{{ __('Try a different title or clear the current search.') }}
			</div>
		</div>
		<EmptyState v-else type="Word Hunt Activities" />
		<div
			v-if="activities.loading && !isInitialLoading"
			class="flex items-center justify-center py-5"
		>
			<LoadingIndicator class="w-8 h-8 text-gray-400" />
		</div>
		<div
			v-if="activities.data?.length"
			class="mt-4 flex items-center justify-between gap-3"
		>
			<div class="text-sm text-ink-gray-5">
				{{ pageRangeLabel }}
			</div>
			<div class="flex items-center gap-2">
				<Button
					variant="ghost"
					:disabled="currentPage === 1 || activities.loading"
					@click="goToPreviousPage"
				>
					{{ __('Previous') }}
				</Button>
				<div class="text-sm text-ink-gray-7">
					{{ __('Page {0} of {1}').format(currentPage, totalPages) }}
				</div>
				<Button
					variant="ghost"
					:disabled="!activities.hasNextPage || activities.loading"
					@click="goToNextPage"
				>
					{{ __('Next') }}
				</Button>
			</div>
		</div>
	</div>
	<Dialog
		v-model="showForm"
		:options="{
			title: __('Create a Word Hunt Activity'),
			size: 'sm',
			actions: [
				{
					label: __('Save'),
					variant: 'solid',
					onClick({ close }) {
						insertActivity(close)
					},
				},
			],
		}"
	>
		<template #body-content>
			<FormControl
				v-model="title"
				:label="__('Title')"
				type="text"
				@keydown.enter="insertActivity(() => (showForm = false))"
			/>
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
	ListRowItem,
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
const pageLength = 20
const start = ref(0)
let searchDebounce

onMounted(() => {
	if (!user.data?.is_moderator && !user.data?.is_instructor) {
		router.push({ name: 'Courses' })
	} else if (!user.data?.is_moderator) {
		filters.value.owner = user.data?.name
	}
	if (route.query.new === 'true') {
		showForm.value = true
	}

	reloadActivities({ resetPage: true })
})

onBeforeUnmount(() => {
	if (searchDebounce) {
		clearTimeout(searchDebounce)
	}
})

watch(search, () => {
	if (searchDebounce) {
		clearTimeout(searchDebounce)
	}
	searchDebounce = setTimeout(() => {
		updateSearchFilter()
		reloadActivities({ resetPage: true })
	}, 300)
})

const activities = createListResource({
	doctype: 'LMS Word Hunt Activity',
	fields: ['name', 'title', 'passing_percentage', 'total_marks', 'modified'],
	filters: filters,
	auto: true,
	cache: ['word-hunt-activities', user.data?.name],
	orderBy: 'modified desc',
	pageLength,
	start: start.value,
	transform(data) {
		return data.map((row) => ({
			...row,
			modified: dayjs(row.modified).fromNow(),
		}))
	},
})

const totalActivities = createResource({
	url: 'frappe.client.get_count',
	params: {
		doctype: 'LMS Word Hunt Activity',
		filters: filters.value,
	},
	auto: true,
	cache: ['word-hunt-activities-count', user.data?.name],
})

const isInitialLoading = computed(() => activities.loading && !activities.data)
const hasActiveSearch = computed(() => Boolean(search.value.trim()))
const currentPage = computed(() => Math.floor(start.value / pageLength) + 1)
const totalPages = computed(() => {
	const total = totalActivities.data || 0
	return Math.max(1, Math.ceil(total / pageLength))
})
const pageRangeLabel = computed(() => {
	const total = totalActivities.data || 0
	if (!total) {
		return __('0 of 0')
	}

	const from = start.value + 1
	const to = Math.min(start.value + (activities.data?.length || 0), total)
	return __('{0}-{1} of {2}').format(from, to, total)
})

const updateSearchFilter = () => {
	const trimmedSearch = search.value.trim()
	if (trimmedSearch) {
		filters.value.title = ['like', `%${trimmedSearch}%`]
	} else {
		delete filters.value.title
	}
}

const reloadActivities = ({ resetPage = false } = {}) => {
	if (resetPage) {
		start.value = 0
	}

	activities.update({
		filters: filters.value,
		start: start.value,
		pageLength,
	})
	activities.reload()

	totalActivities.update({
		filters: filters.value,
	})
	totalActivities.reload()
}

const goToPreviousPage = () => {
	if (currentPage.value === 1) return
	start.value = Math.max(0, start.value - pageLength)
	reloadActivities()
}

const goToNextPage = () => {
	if (!activities.hasNextPage) return
	start.value += pageLength
	reloadActivities()
}

const openActivity = (activityID) => {
	if (readOnlyMode) return
	router.push({ name: 'WordHuntForm', params: { activityID } })
}

const openSubmissions = (activityID) => {
	router.push({ name: 'WordHuntSubmissionList', params: { activityID } })
}

const insertActivity = (close) => {
	title.value = escapeHTML(title.value.trim())
	if (!title.value) {
		toast.error(__('Title is required'))
		return
	}

	activities.insert.submit(
		{
			title: title.value,
			passage: 'Complete the sentence with _______.',
			passing_percentage: 100,
			items: [
				{
					doctype: 'LMS Word Hunt Item',
					correct_answer: 'example',
					marks: 1,
				},
			],
		},
		{
			onSuccess(data) {
				toast.success(__('Activity created successfully'))
				close()
				title.value = ''
				reloadActivities({ resetPage: true })
				router.push({ name: 'WordHuntForm', params: { activityID: data.name } })
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
			},
		}
	)
}

const columns = computed(() => [
	{ label: __('Title'), key: 'title', width: '20rem' },
	{
		label: __('Passing %'),
		key: 'passing_percentage',
		align: 'center',
		width: '8rem',
	},
	{
		label: __('Total Marks'),
		key: 'total_marks',
		align: 'center',
		width: '8rem',
	},
	{ label: __('Modified'), key: 'modified', align: 'right', width: '8rem' },
	{ label: __('Actions'), key: 'actions', align: 'right', width: '12rem' },
])

const breadcrumbs = computed(() => [
	{ label: __('Word Hunt Activities'), route: { name: 'WordHuntActivities' } },
])

usePageMeta(() => ({
	title: __('Word Hunt Activities'),
	icon: brand.favicon,
}))
</script>
