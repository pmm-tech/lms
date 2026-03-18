import AssessmentPlugin from '@/components/AssessmentPlugin.vue'
import { createApp, h } from 'vue'
import translationPlugin from '../translation'
import { Grip } from 'lucide-vue-next'
import { getLmsRoute } from '@/utils/basePath'

export class DragDrop {
	constructor({ data, readOnly }) {
		this.data = data
		this.readOnly = readOnly
	}

	static get toolbox() {
		const app = createApp({
			render: () => h(Grip, { size: 18, strokeWidth: 1.5 }),
		})

		const div = document.createElement('div')
		app.mount(div)

		return {
			title: __('Drag & Drop'),
			icon: div.innerHTML,
		}
	}

	static get isReadOnlySupported() {
		return true
	}

	render() {
		this.wrapper = document.createElement('div')
		if (Object.keys(this.data).length) {
			this.renderActivity(this.data.activity)
		} else {
			this.renderActivityModal()
		}
		return this.wrapper
	}

	renderActivity(activity) {
		if (this.readOnly) {
			const activityPath = getLmsRoute(`drag-drop/${activity}?fromLesson=1`)
			this.wrapper.innerHTML = `<iframe src="${activityPath}" class="w-full h-[560px]"></iframe>`
			return
		}

		this.wrapper.innerHTML = `<div class='border rounded-md p-4 text-center bg-surface-menu-bar mb-4'>
			<span class="font-medium">
				Drag & Drop Activity: ${activity}
			</span>
		</div>`
	}

	renderActivityModal() {
		if (this.readOnly) return

		const app = createApp(AssessmentPlugin, {
			type: 'dragDrop',
			onAddition: (activity) => {
				this.data.activity = activity
				this.renderActivity(activity)
			},
		})
		app.use(translationPlugin)
		app.mount(this.wrapper)
	}

	save() {
		if (Object.keys(this.data).length === 0) return {}
		return {
			activity: this.data.activity,
		}
	}
}
