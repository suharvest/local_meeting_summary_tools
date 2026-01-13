<script setup>
import { ref, computed, onMounted, watch, provide } from 'vue'
import DeviceSelector from './components/DeviceSelector.vue'
import MeetingControl from './components/MeetingControl.vue'
import MeetingStatus from './components/MeetingStatus.vue'
import MeetingMinutes from './components/MeetingMinutes.vue'
import { useMeeting } from './composables/useMeeting'
import { useI18n } from './composables/useI18n'

// i18n
const { locale, availableLocales, setLocale, t, initLocale } = useI18n()

// Provide t function to child components
provide('t', t)
provide('locale', locale)

// Initialize locale on mount
onMounted(() => {
  initLocale()
})

// Device selection
const selectedDevice = ref('')

// Sync language with locale
watch(locale, (newLocale) => {
  // Locale changes affect both UI and output
}, { immediate: true })

// Handle language change
function handleLocaleChange(event) {
  setLocale(event.target.value)
}

// Meeting state management
const {
  currentMeeting,
  summary,
  keyPoints,
  actionItems,
  currentStage,
  isStreaming,
  isGenerating,
  generationError,
  meetingInProgress,
  meetingCompleted,
  hasMeeting,
  start,
  end,
  reset,
} = useMeeting()

// Show minutes section when generating or completed
const showMinutes = computed(() =>
  (hasMeeting.value && !meetingInProgress.value) ||
  isGenerating.value ||
  meetingCompleted.value
)

// Handle start meeting
async function handleStart() {
  if (!selectedDevice.value) return

  try {
    await start(selectedDevice.value)
  } catch (error) {
    console.error('Failed to start meeting:', error)
  }
}

// Handle end meeting
async function handleEnd() {
  try {
    await end(null, locale.value)
  } catch (error) {
    console.error('Failed to end meeting:', error)
  }
}

// Reset for new meeting
function handleNewMeeting() {
  reset()
  selectedDevice.value = ''
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-blue-50 to-white">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="max-w-4xl mx-auto px-4 py-6">
        <h1 class="text-3xl font-bold text-center text-gray-900">
          {{ t('appTitle') }}
        </h1>
        <p class="text-center text-gray-500 mt-2">
          {{ t('appSubtitle') }}
        </p>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-4xl mx-auto px-4 py-8">
      <!-- Control Panel -->
      <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
        <!-- Device & Language Selectors -->
        <div class="flex gap-4 flex-wrap">
          <!-- Device Selector -->
          <div class="flex-1 min-w-[200px]">
            <DeviceSelector
              v-model="selectedDevice"
              :disabled="meetingInProgress || isGenerating"
            />
          </div>

          <!-- Language Selector -->
          <div class="w-40">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              {{ t('outputLanguage') }}
            </label>
            <select
              :value="locale"
              @change="handleLocaleChange"
              :disabled="meetingInProgress || isGenerating"
              class="w-full px-4 py-3 rounded-lg border border-gray-300
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                     disabled:bg-gray-100 disabled:text-gray-500"
            >
              <option v-for="lang in availableLocales" :key="lang.code" :value="lang.code">
                {{ lang.name }}
              </option>
            </select>
          </div>
        </div>

        <!-- Meeting Control Button -->
        <MeetingControl
          :device="selectedDevice"
          :in-progress="meetingInProgress"
          :is-generating="isGenerating"
          @start="handleStart"
          @end="handleEnd"
        />

        <!-- Meeting Status (shown when in progress) -->
        <MeetingStatus
          v-if="meetingInProgress && currentMeeting"
          :meeting="currentMeeting"
        />
      </div>

      <!-- Meeting Minutes (shown after ending) -->
      <MeetingMinutes
        v-if="showMinutes && currentMeeting"
        :meeting="currentMeeting"
        :summary="summary"
        :key-points="keyPoints"
        :action-items="actionItems"
        :current-stage="currentStage"
        :is-streaming="isStreaming"
        :is-generating="isGenerating"
        :error="generationError"
      />

      <!-- New Meeting Button (shown when completed) -->
      <div v-if="meetingCompleted" class="mt-6 text-center">
        <button
          @click="handleNewMeeting"
          class="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg
                 hover:bg-gray-200 transition-colors font-medium"
        >
          {{ t('newMeeting') }}
        </button>
      </div>
    </main>

    <!-- Footer -->
    <footer class="text-center py-8 text-gray-400 text-sm">
      {{ t('version') }}
    </footer>
  </div>
</template>
