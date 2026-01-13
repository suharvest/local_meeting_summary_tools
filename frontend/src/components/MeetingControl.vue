<script setup>
import { computed, inject } from 'vue'

const t = inject('t')

const props = defineProps({
  device: {
    type: String,
    default: '',
  },
  inProgress: {
    type: Boolean,
    default: false,
  },
  isGenerating: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['start', 'end'])

const canStart = computed(() => props.device && !props.inProgress && !props.isGenerating)
const canEnd = computed(() => props.inProgress && !props.isGenerating)
</script>

<template>
  <div class="flex justify-center">
    <!-- Start Meeting Button -->
    <button
      v-if="!inProgress"
      @click="emit('start')"
      :disabled="!canStart"
      class="flex items-center gap-2 px-8 py-4 bg-blue-500 text-white text-lg font-medium
             rounded-full shadow-lg hover:bg-blue-600
             disabled:bg-gray-300 disabled:cursor-not-allowed
             transition-all duration-200 transform hover:scale-105
             disabled:transform-none"
    >
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
      </svg>
      {{ t('startMeeting') }}
    </button>

    <!-- End Meeting Button -->
    <button
      v-else
      @click="emit('end')"
      :disabled="!canEnd"
      class="flex items-center gap-2 px-8 py-4 bg-red-500 text-white text-lg font-medium
             rounded-full shadow-lg hover:bg-red-600
             disabled:bg-gray-300 disabled:cursor-not-allowed
             transition-all duration-200 transform hover:scale-105
             disabled:transform-none animate-pulse"
    >
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
      </svg>
      {{ t('endMeeting') }}
    </button>
  </div>
</template>
