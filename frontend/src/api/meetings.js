/**
 * Meeting API functions
 */

import { get, post, getStreamURL } from './index'

/**
 * Start a new meeting
 */
export async function startMeeting(macAddress, title = null) {
  const response = await post('/api/meetings/start', {
    mac_address: macAddress,
    title,
  })
  return response.data
}

/**
 * End a meeting
 * @param {string} meetingId - Meeting ID
 * @param {string|null} llmProvider - LLM provider to use
 * @param {string} language - Language for meeting minutes (zh, en)
 */
export async function endMeeting(meetingId, llmProvider = null, language = 'zh') {
  const response = await post('/api/meetings/end', {
    meeting_id: meetingId,
    llm_provider: llmProvider,
    language: language,
  })
  return response.data
}

/**
 * Get supported languages
 */
export async function getLanguages() {
  const response = await get('/api/meetings/config/languages')
  return response.data
}

/**
 * Get meeting details
 */
export async function getMeeting(meetingId) {
  const response = await get(`/api/meetings/${meetingId}`)
  return response.data
}

/**
 * Get list of active meetings
 */
export async function getMeetings() {
  const response = await get('/api/meetings')
  return response.data
}

/**
 * Get SSE stream URL for meeting minutes
 */
export function getMeetingStreamURL(meetingId) {
  return getStreamURL(`/api/meetings/${meetingId}/stream`)
}
