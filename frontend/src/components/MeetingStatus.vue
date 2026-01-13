<script setup>
import { ref, computed, onMounted, onUnmounted, inject } from 'vue'

const t = inject('t')
const locale = inject('locale')

const props = defineProps({
  meeting: {
    type: Object,
    required: true,
  },
})

const elapsedSeconds = ref(0)
let timer = null

const formattedTime = computed(() => {
  const mins = Math.floor(elapsedSeconds.value / 60)
  const secs = elapsedSeconds.value % 60
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
})

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

function updateElapsed() {
  if (props.meeting?.start_time) {
    const start = props.meeting.start_time
    const now = Date.now()
    elapsedSeconds.value = Math.floor((now - start) / 1000)
  }
}

onMounted(() => {
  updateElapsed()
  timer = setInterval(updateElapsed, 1000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<template>
  <div class="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <!-- Recording indicator -->
        <div class="flex items-center gap-2">
          <span class="relative flex h-3 w-3">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
          </span>
          <span class="text-red-600 font-medium">{{ t('meetingInProgress') }}</span>
        </div>
      </div>

      <!-- Timer -->
      <div class="text-2xl font-mono font-bold text-gray-800">
        {{ formattedTime }}
      </div>
    </div>

    <!-- Meeting info -->
    <div class="mt-3 text-sm text-gray-600">
      <div class="flex items-center gap-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ startTimeFormatted }}</span>
      </div>
      <div v-if="meeting?.device_name" class="flex items-center gap-2 mt-1">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
        <span>{{ t('device') }}: {{ meeting.device_name }}</span>
      </div>
    </div>
  </div>
</template>
