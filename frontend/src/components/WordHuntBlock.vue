<template>
	<WordHunt v-if="user.data" :activityName="activity" />
	<div v-else class="border rounded-md text-center py-20">
		<div>
			{{ __('Please login to access this activity.') }}
		</div>
		<Button @click="redirectToLogin()" class="mt-2">
			<span>
				{{ __('Login') }}
			</span>
		</Button>
	</div>
</template>
<script setup>
import { inject } from 'vue'
import { Button } from 'frappe-ui'
import WordHunt from '@/components/WordHunt.vue'

const user = inject('$user')

defineProps({
	activity: {
		type: String,
		required: true,
	},
})

const redirectToLogin = () => {
	window.location.href = `/login`
}
</script>
