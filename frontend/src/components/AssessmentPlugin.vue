<template>
	<Dialog
		v-model="show"
		:options="{
			title: dialogTitle,
			size: 'xl',
			actions: [
				{
					label: __('Save'),
					variant: 'solid',
					onClick: () => {
						addAssessment()
					},
				},
			],
		}"
	>
		<template #body-content>
			<div class="">
				<div>
					<Link
						v-if="type == 'quiz'"
						v-model="quiz"
						doctype="LMS Quiz"
						:label="__('Select a quiz')"
						placeholder=" "
						:onCreate="(value, close) => redirectToForm()"
					/>
					<Link
						v-else-if="type == 'dragDrop'"
						v-model="dragDrop"
						doctype="LMS Drag Drop Activity"
						:label="__('Select an Activity')"
						placeholder=" "
						:onCreate="(value, close) => redirectToForm()"
					/>
					<Link
						v-else-if="type == 'wordHunt'"
						v-model="wordHunt"
						doctype="LMS Word Hunt Activity"
						:label="__('Select an Activity')"
						placeholder=" "
						:onCreate="(value, close) => redirectToForm()"
					/>
					<div v-else class="space-y-4">
						<Link
							v-if="filterAssignmentsByCourse"
							v-model="assignment"
							doctype="LMS Assignment"
							:filters="{
								course: route.params.courseName,
							}"
							placeholder=" "
							:label="__('Select an Assignment')"
							:onCreate="(value, close) => redirectToForm()"
						/>
						<Link
							v-else
							v-model="assignment"
							doctype="LMS Assignment"
							placeholder=" "
							:label="__('Select an Assignment')"
							:onCreate="(value, close) => redirectToForm()"
						/>
						<Switch
							size="sm"
							:description="__('Only show assignments from the current course')"
							:label="__('Filter assignments by course')"
							v-model="filterAssignmentsByCourse"
						/>
					</div>
				</div>
			</div>
		</template>
	</Dialog>
</template>
<script setup>
import { Dialog, Switch } from 'frappe-ui'
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getLmsRoute } from '@/utils/basePath'
import Link from '@/components/Controls/Link.vue'

const show = ref(false)
const quiz = ref(null)
const dragDrop = ref(null)
const wordHunt = ref(null)
const assignment = ref(null)
const filterAssignmentsByCourse = ref(false)
const route = useRoute()

const props = defineProps({
	type: {
		type: String,
		required: true,
	},
	onAddition: {
		type: Function,
		required: true,
	},
})

onMounted(async () => {
	await nextTick()
	show.value = true
})

const dialogTitle = computed(() => {
	if (props.type == 'quiz') {
		return __('Add a quiz to your lesson')
	}
	if (props.type == 'dragDrop') {
		return __('Add a drag and drop activity to your lesson')
	}
	if (props.type == 'wordHunt') {
		return __('Add a word hunt activity to your lesson')
	}
	return __('Add an assignment to your lesson')
})

const addAssessment = () => {
	props.onAddition(
		props.type == 'quiz'
			? quiz.value
			: props.type == 'dragDrop'
				? dragDrop.value
				: props.type == 'wordHunt'
					? wordHunt.value
				: assignment.value
	)
	show.value = false
}

const redirectToForm = () => {
	if (props.type == 'quiz') {
		window.open(getLmsRoute('quizzes?new=true'), '_blank')
	} else if (props.type == 'dragDrop') {
		window.open(getLmsRoute('drag-drop-activities?new=true'), '_blank')
	} else if (props.type == 'wordHunt') {
		window.open(getLmsRoute('word-hunt-activities?new=true'), '_blank')
	} else {
		window.open(getLmsRoute('assignments?new=true'), '_blank')
	}
}
</script>
