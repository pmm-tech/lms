<template>
	<div v-if="course?.data?.final_exam" class="mt-10">
		<div class="text-lg font-semibold text-ink-gray-9 mb-4">
			{{ __('Final Exam') }}
		</div>
		<div class="rounded-xl border border-outline-gray-2 bg-surface-white p-5">
			<div class="flex items-start justify-between gap-4">
				<div>
					<div class="text-base font-semibold text-ink-gray-9">
						{{ course.data.final_exam.title }}
					</div>
					<div class="mt-2 text-sm text-ink-gray-6">
						{{ __('Course-level final assessment') }}
					</div>
					<div
						v-if="course.data.final_exam.prerequisites?.length"
						class="mt-4 space-y-2"
					>
						<div class="text-sm font-medium text-ink-gray-8">
							{{ __('Prerequisites') }}
						</div>
						<div
							v-for="item in course.data.final_exam.prerequisites"
							:key="item.label"
							class="flex items-center justify-between gap-4 rounded-lg bg-surface-gray-2 px-3 py-2 text-sm"
						>
							<span>{{ item.label }}</span>
							<Badge
								:theme="item.satisfied ? 'green' : 'orange'"
								:label="item.satisfied ? __('Ready') : __('Pending')"
							/>
						</div>
					</div>
					<div
						v-if="course.data.final_exam.locked_reason"
						class="mt-4 rounded-lg bg-surface-orange-1 px-3 py-2 text-sm text-ink-orange-3"
					>
						{{ course.data.final_exam.locked_reason }}
					</div>
				</div>
				<router-link
					:to="{
						name: 'ExamPage',
						params: {
							examID: course.data.final_exam.name,
						},
					}"
				>
					<Button variant="solid">
						{{ course.data.final_exam.can_attempt ? __('Open Exam') : __('View Exam') }}
					</Button>
				</router-link>
			</div>
		</div>
	</div>
</template>

<script setup>
import { Badge, Button } from 'frappe-ui'

defineProps({
	course: {
		type: Object,
		required: true,
	},
})
</script>
