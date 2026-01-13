/**
 * Meeting state management composable
 */

import { ref, computed, reactive } from 'vue'
import { startMeeting as apiStartMeeting, endMeeting as apiEndMeeting, getMeetingStreamURL } from '../api/meetings'
import { useSSE } from './useSSE'

export function useMeeting() {
  // Current meeting state
  const currentMeeting = ref(null)

  // Generated content
  const summary = ref('')
  const keyPoints = ref('')
  const actionItems = ref('')
  const transcripts = ref([])

  // Generation state
  const currentStage = ref('')
  const isStreaming = ref(false)
  const isGenerating = ref(false)
  const generationError = ref(null)

  // SSE connection
  const { connect, disconnect, isConnected } = useSSE()

  // Computed properties
  const meetingInProgress = computed(() =>
    currentMeeting.value?.status === 'in_progress'
  )

  const meetingCompleted = computed(() =>
    currentMeeting.value?.status === 'completed'
  )

  const hasMeeting = computed(() =>
    currentMeeting.value !== null
  )

  const duration = computed(() => {
    if (!currentMeeting.value) return '00:00'
    const seconds = currentMeeting.value.duration_seconds || 0
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
  })

  /**
   * Start a new meeting
   */
  async function start(macAddress, title = null) {
    try {
      // Reset state
      resetContent()
      generationError.value = null

      // Call API to start meeting
      const meeting = await apiStartMeeting(macAddress, title)
      currentMeeting.value = meeting

      return meeting
    } catch (error) {
      generationError.value = error.message
      throw error
    }
  }

  /**
   * End the current meeting and start generating minutes
   * @param {string|null} llmProvider - LLM provider to use
   * @param {string} language - Language for meeting minutes (zh, en)
   */
  async function end(llmProvider = null, language = 'en') {
    if (!currentMeeting.value) {
      throw new Error('No active meeting')
    }

    try {
      generationError.value = null
      isGenerating.value = true

      // Call API to end meeting
      const result = await apiEndMeeting(currentMeeting.value.meeting_id, llmProvider, language)

      // Update meeting with end time info
      currentMeeting.value = {
        ...currentMeeting.value,
        ...result,
      }

      // Start SSE stream for minutes generation
      const streamURL = getMeetingStreamURL(currentMeeting.value.meeting_id)
      await startStream(streamURL)

      return result
    } catch (error) {
      generationError.value = error.message
      isGenerating.value = false
      throw error
    }
  }

  /**
   * Start SSE stream to receive meeting minutes
   */
  function startStream(url) {
    isStreaming.value = true

    connect(url, {
      start: (data) => {
        currentStage.value = data.status || 'loading'
      },

      transcripts: (data) => {
        // Transcript count received
        console.log(`Received ${data.count} transcripts`)
      },

      stage_start: (data) => {
        currentStage.value = data.stage
      },

      content: (data) => {
        currentStage.value = data.stage

        // Append content to the appropriate field
        switch (data.stage) {
          case 'summary':
            summary.value += data.content
            break
          case 'key_points':
            keyPoints.value += data.content
            break
          case 'action_items':
            actionItems.value += data.content
            break
        }
      },

      stage_complete: (data) => {
        // Stage completed - content is already accumulated
        console.log(`Stage ${data.stage} complete`)
      },

      complete: (data) => {
        isStreaming.value = false
        isGenerating.value = false
        currentStage.value = ''

        if (currentMeeting.value) {
          currentMeeting.value.status = 'completed'
          currentMeeting.value.file_path = data.file_path
        }

        disconnect()
      },

      error: (data) => {
        isStreaming.value = false
        isGenerating.value = false
        generationError.value = data.error || 'Generation failed'
        disconnect()
      },
    })
  }

  /**
   * Reset all generated content
   */
  function resetContent() {
    summary.value = ''
    keyPoints.value = ''
    actionItems.value = ''
    transcripts.value = []
    currentStage.value = ''
  }

  /**
   * Reset entire meeting state
   */
  function reset() {
    currentMeeting.value = null
    resetContent()
    isStreaming.value = false
    isGenerating.value = false
    generationError.value = null
    disconnect()
  }

  return {
    // State
    currentMeeting,
    summary,
    keyPoints,
    actionItems,
    transcripts,
    currentStage,
    isStreaming,
    isGenerating,
    generationError,

    // Computed
    meetingInProgress,
    meetingCompleted,
    hasMeeting,
    duration,

    // Actions
    start,
    end,
    reset,
    resetContent,
  }
}
