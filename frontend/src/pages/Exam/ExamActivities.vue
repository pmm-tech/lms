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
	<div class="pt-5 mx-5">
		<div class="flex items-center justify-between mb-5">
			<div class="text-lg font-semibold text-ink-gray-9">
				{{ __('{0} Exams').format(exams.data?.length || 0) }}
			</div>
			<FormControl v-model="search" type="text" :placeholder="__('Search')">
				<template #prefix>
					<FeatherIcon name="search" class="size-4 text-ink-gray-5" />
				</template>
			</FormControl>
		</div>
		<ListView
			v-if="exams.data?.length"
			:columns="examColumns"
			:rows="exams.data"
			row-key="name"
			:options="{ showTooltip: false, selectable: false }"
			class="h-[79vh] border-b"
		>
			<ListHeader class="mb-2 grid items-center rounded bg-surface-white border-b rounded-none p-2">
				<ListHeaderItem :item="item" v-for="item in examColumns" :key="item.key" />
			</ListHeader>
			<ListRows>
				<router-link
					v-for="row in exams.data"
					:key="row.name"
					:to="{ name: 'ExamForm', params: { examID: row.name } }"
				>
					<ListRow :row="row" class="hover:bg-surface-gray-2" />
				</router-link>
			</ListRows>
		</ListView>
		<EmptyState v-else type="Exams" />
		<div class="flex items-center justify-end space-x-3 mt-3">
			<Button v-if="exams.hasNextPage" @click="exams.next()">{{ __('Load More') }}</Button>
			<div v-if="exams.hasNextPage" class="h-8 border-l"></div>
			<div class="text-ink-gray-5">{{ exams.data?.length || 0 }} {{ __('of') }} {{ totalExams.data || 0 }}</div>
		</div>
	</div>
	<Dialog
		v-model="showForm"
		:options="{
			title: __('Create an Exam'),
			size: 'sm',
			actions: [{ label: __('Save'), variant: 'solid', onClick({ close }) { insertExam(close) } }],
		}"
	>
		<template #body-content>
			<FormControl v-model="title" :label="__('Title')" type="text" autocomplete="off" />
			<FormControl
				class="mt-4"
				v-model="course"
				:label="__('Course')"
				type="select"
				:options="courseOptions"
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
	FeatherIcon,
	FormControl,
	ListHeader,
	ListHeaderItem,
	ListRow,
	ListRows,
	ListView,
	toast,
	usePageMeta,
} from 'frappe-ui'
import { computed, inject, onMounted, ref, watch } from 'vue'
import { Plus } from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'
import { sanitizeHTML } from '@/utils'
import { sessionStore } from '@/stores/session'
import EmptyState from '@/components/EmptyState.vue'

const { brand } = sessionStore()
const dayjs = inject('$dayjs')
const user = inject('$user')
const router = useRouter()
const route = useRoute()
const readOnlyMode = window.read_only_mode
const search = ref('')
const filters = ref({})
const showForm = ref(false)
const title = ref('')
const course = ref('')

onMounted(() => {
	if (!user.data?.is_moderator && !user.data?.is_instructor && !user.data?.is_evaluator) {
		router.push({ name: 'Courses' })
	}
	if (route.query.new === 'true') showForm.value = true
})

watch(search, () => {
	filters.value.title = ['like', `%${search.value}%`]
	exams.update({ filters: filters.value })
	exams.reload()
	totalExams.update({ filters: filters.value })
})

const exams = createListResource({
	doctype: 'LMS Exam',
	filters,
	fields: ['name', 'title', 'course', 'display_chapter', 'passing_percentage', 'max_attempts', 'modified'],
	auto: true,
	orderBy: 'modified desc',
	transform(data) {
		return data.map((exam) => ({ ...exam, modified: dayjs(exam.modified).fromNow(true) }))
	},
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

const totalExams = createResource({
	url: 'frappe.client.get_count',
	params: { doctype: 'LMS Exam', filters: filters.value },
	auto: true,
})

const validateTitle = () => {
	title.value = sanitizeHTML((title.value || '').trim())
}

const insertExam = (close) => {
	validateTitle()
	if (!course.value) {
		toast.error(__('Please select a course'))
		return
	}
	exams.insert.submit(
		{
			title: title.value,
			course: course.value,
			passing_percentage: 100,
			is_final_exam: 1,
		},
		{
			onSuccess(data) {
				close()
				title.value = ''
				course.value = ''
				router.push({ name: 'ExamForm', params: { examID: data.name } })
			},
			onError(error) {
				toast.error(error.messages?.[0] || error)
			},
		}
	)
}

const examColumns = computed(() => [
	{ label: __('Title'), key: 'title', width: 3 },
	{ label: __('Course'), key: 'course', width: 2 },
	{ label: __('Passing %'), key: 'passing_percentage', width: 1, align: 'center' },
	{ label: __('Modified'), key: 'modified', width: 1, align: 'right' },
])

const courseOptions = computed(() =>
	(courses.data || []).map((row) => ({ label: row.title, value: row.name }))
)

const breadcrumbs = computed(() => [{ label: __('Exams') }])

usePageMeta(() => ({ title: __('Exams'), icon: brand.favicon }))
</script>
