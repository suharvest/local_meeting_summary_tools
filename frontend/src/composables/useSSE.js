/**
 * SSE (Server-Sent Events) connection management composable
 */

import { ref, onUnmounted } from 'vue'

export function useSSE() {
  const eventSource = ref(null)
  const isConnected = ref(false)
  const error = ref(null)

  /**
   * Connect to an SSE endpoint
   * @param {string} url - SSE endpoint URL
   * @param {Object} handlers - Event handlers object { eventName: handlerFunction }
   */
  function connect(url, handlers = {}) {
    // Close existing connection if any
    if (eventSource.value) {
      eventSource.value.close()
    }

    error.value = null

    try {
      eventSource.value = new EventSource(url)

      eventSource.value.onopen = () => {
        isConnected.value = true
        error.value = null
        if (handlers.open) {
          handlers.open()
        }
      }

      eventSource.value.onerror = (e) => {
        error.value = e
        isConnected.value = false
        if (handlers.error) {
          handlers.error(e)
        }
      }

      // Register custom event handlers
      Object.entries(handlers).forEach(([event, handler]) => {
        if (event !== 'open' && event !== 'error') {
          eventSource.value.addEventListener(event, (e) => {
            try {
              const data = JSON.parse(e.data)
              handler(data)
            } catch (parseError) {
              console.error('Failed to parse SSE data:', parseError)
            }
          })
        }
      })
    } catch (e) {
      error.value = e
      isConnected.value = false
    }
  }

  /**
   * Disconnect from the SSE endpoint
   */
  function disconnect() {
    if (eventSource.value) {
      eventSource.value.close()
      eventSource.value = null
      isConnected.value = false
    }
  }

  // Clean up on component unmount
  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    error,
    connect,
    disconnect,
  }
}
