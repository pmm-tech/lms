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

			const iframe = document.createElement('iframe')
			iframe.src = activityPath
			iframe.className = 'w-full'
			iframe.style.border = 'none'
			iframe.style.height = '200px'

			iframe.addEventListener('load', () => {
				let lastHeight = 0
				let attempts = 0
				const poll = setInterval(() => {
					try {
						const height =
							iframe.contentWindow.document.body.scrollHeight
						if (height === lastHeight || attempts > 20) {
							clearInterval(poll)
							if (height > 0) iframe.style.height = height + 'px'
						}
						lastHeight = height
						attempts++
					} catch (e) {
						clearInterval(poll)
					}
				}, 100)
			})

			this.wrapper.appendChild(iframe)

			setTimeout(() => {
				iframe.style.height =
					iframe.contentWindow.document.body.scrollHeight + 'px'

				let lastHeight = 0
				setInterval(() => {
					try {
						const height =
							iframe.contentWindow.document.body.scrollHeight
						if (height !== lastHeight) {
							iframe.style.height = height + 'px'
							lastHeight = height
						}
					} catch (e) {}
				}, 300)
			}, 1500)
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
