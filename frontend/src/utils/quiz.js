import QuizBlock from '@/components/QuizBlock.vue'
import AssessmentPlugin from '@/components/AssessmentPlugin.vue'
import { createApp, h } from 'vue'
import { usersStore } from '../stores/user'
import translationPlugin from '../translation'
import { CircleHelp } from 'lucide-vue-next'
import { getLmsRoute } from '@/utils/basePath'
import { useRouter } from 'vue-router'

const router = useRouter()

export class Quiz {
	constructor({ data, api, readOnly }) {
		this.data = data
		this.readOnly = readOnly
	}

	static get toolbox() {
		const app = createApp({
			render: () => h(CircleHelp, { size: 5, strokeWidth: 1.5 }),
		})

		const div = document.createElement('div')
		app.mount(div)

		return {
			title: __('Quiz'),
			icon: div.innerHTML,
		}
	}

	static get isReadOnlySupported() {
		return true
	}

	render() {
		this.wrapper = document.createElement('div')
		if (Object.keys(this.data).length) {
			this.renderQuiz(this.data.quiz)
		} else {
			this.renderQuizModal()
		}
		return this.wrapper
	}

	renderQuiz(quiz) {
		if (this.readOnly) {
			const quizPath = getLmsRoute(`quiz/${quiz}?fromLesson=1`)

			const iframe = document.createElement('iframe')
			iframe.src = quizPath
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
					} catch (e) {
						// Ignore iframe access errors while embedded content is loading.
					}
				}, 300)
			}, 500)
			return
		}
		this.wrapper.innerHTML = `<div class='border rounded-md p-4 text-center bg-surface-menu-bar mb-4'>
        <span class="font-medium">
            Quiz: ${quiz}
        </span>
    </div>`
		return
	}

	renderQuizModal() {
		if (this.readOnly) {
			return
		}
		const app = createApp(AssessmentPlugin, {
			type: 'quiz',
			onAddition: (quiz) => {
				this.data.quiz = quiz
				this.renderQuiz(quiz)
			},
		})
		app.use(translationPlugin)
		app.mount(this.wrapper)
	}

	save() {
		if (Object.keys(this.data).length === 0) return {}
		return {
			quiz: this.data.quiz,
		}
	}
}
