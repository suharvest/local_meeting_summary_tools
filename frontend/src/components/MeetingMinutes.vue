<script setup>
import { computed, inject } from 'vue'
import StreamingContent from './StreamingContent.vue'

const t = inject('t')
const locale = inject('locale')

const props = defineProps({
  meeting: {
    type: Object,
    required: true,
  },
  summary: {
    type: String,
    default: '',
  },
  keyPoints: {
    type: String,
    default: '',
  },
  actionItems: {
    type: String,
    default: '',
  },
  currentStage: {
    type: String,
    default: '',
  },
  isStreaming: {
    type: Boolean,
    default: false,
  },
  isGenerating: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: null,
  },
})

const title = computed(() => props.meeting?.title || t('meetingMinutes'))

const startTimeFormatted = computed(() => {
  if (!props.meeting?.start_time) return ''
  const localeStr = locale.value === 'zh' ? 'zh-CN' : 'en-US'
  return new Date(props.meeting.start_time).toLocaleString(localeStr, {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
})

const duration = computed(() => {
  const seconds = props.meeting?.duration_seconds || 0
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
})

const isCompleted = computed(() => props.meeting?.status === 'completed')
</script>

<template>
  <div class="bg-white rounded-lg shadow-lg overflow-hidden">
    <!-- Header -->
    <div class="bg-gradient-to-r from-green-500 to-green-600 px-6 py-4 text-white">
      <div class="flex items-center gap-2 mb-2">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h2 class="text-xl font-semibold">
          {{ isCompleted ? t('meetingMinutes') : t('generatingMinutes') }}
        </h2>
      </div>
    </div>

    <!-- Meeting Info -->
    <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
      <div class="grid grid-cols-3 gap-4 text-sm">
        <div>
          <div class="text-gray-500">{{ t('meetingMinutes') }}</div>
          <div class="font-medium text-gray-900">{{ title }}</div>
        </div>
        <div>
          <div class="text-gray-500">{{ t('duration') }}</div>
          <div class="font-medium text-gray-900">{{ startTimeFormatted }}</div>
        </div>
        <div>
          <div class="text-gray-500">{{ t('duration') }}</div>
          <div class="font-medium text-gray-900">{{ duration }}</div>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="px-6 py-4 bg-red-50 border-b border-red-200">
      <div class="flex items-center gap-2 text-red-700">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ t('generationFailed') }}: {{ error }}</span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isGenerating && !summary && !error" class="px-6 py-8 text-center">
      <div class="inline-flex items-center gap-3 text-gray-600">
        <svg class="animate-spin h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span>{{ t('generatingMinutes') }}</span>
      </div>
    </div>

    <!-- Content Sections -->
    <div v-else class="divide-y divide-gray-200">
      <!-- Summary Section -->
      <div class="px-6 py-5">
        <h3 class="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-3">
          <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          {{ t('summary') }}
        </h3>
        <StreamingContent
          :content="summary"
          :isStreaming="isStreaming && currentStage === 'summary'"
          :placeholder="t('generating')"
        />
      </div>

      <!-- Key Points Section -->
      <div class="px-6 py-5">
        <h3 class="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-3">
          <svg class="w-5 h-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          {{ t('keyPoints') }}
        </h3>
        <StreamingContent
          :content="keyPoints"
          :isStreaming="isStreaming && currentStage === 'key_points'"
          :placeholder="t('generating')"
          format="list"
        />
      </div>

      <!-- Action Items Section -->
      <div class="px-6 py-5">
        <h3 class="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-3">
          <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          {{ t('actionItems') }}
        </h3>
        <StreamingContent
          :content="actionItems"
          :isStreaming="isStreaming && currentStage === 'action_items'"
          :placeholder="t('generating')"
          format="checklist"
        />
      </div>
    </div>

    <!-- Footer -->
    <div v-if="isCompleted && meeting?.file_path" class="px-6 py-4 bg-gray-50 border-t border-gray-200">
      <div class="flex items-center gap-2 text-sm text-gray-600">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
        </svg>
        <span>{{ t('savedTo') }}: {{ meeting.file_path }}</span>
      </div>
    </div>
  </div>
</template>
