<script setup>
import { computed } from 'vue'

const props = defineProps({
  content: {
    type: String,
    default: '',
  },
  isStreaming: {
    type: Boolean,
    default: false,
  },
  placeholder: {
    type: String,
    default: '等待内容...',
  },
  format: {
    type: String,
    default: 'text', // 'text', 'list', 'checklist'
  },
})

const hasContent = computed(() => props.content && props.content.trim().length > 0)

// Parse content into list items
const listItems = computed(() => {
  if (!hasContent.value) return []

  // Split by numbered items (1. 2. 3.) or bullet points (- *)
  const lines = props.content.split('\n').filter(line => line.trim())
  return lines.map(line => {
    // Remove leading numbers, dots, dashes, asterisks
    return line.replace(/^[\d]+\.\s*/, '').replace(/^[-*]\s*/, '').trim()
  }).filter(item => item.length > 0)
})

// Parse content into checklist items
const checklistItems = computed(() => {
  if (!hasContent.value) return []

  const lines = props.content.split('\n').filter(line => line.trim())
  return lines.map(line => {
    // Check for markdown checkbox format
    const checked = line.includes('[x]') || line.includes('[X]')
    // Remove checkbox markers and leading dashes
    const text = line
      .replace(/^[-*]\s*\[[ xX]\]\s*/, '')
      .replace(/^[-*]\s*/, '')
      .trim()
    return { text, checked }
  }).filter(item => item.text.length > 0)
})
</script>

<template>
  <div class="text-gray-700 leading-relaxed">
    <!-- Placeholder when no content -->
    <div v-if="!hasContent && !isStreaming" class="text-gray-400 italic">
      {{ placeholder }}
    </div>

    <!-- Loading indicator when streaming but no content yet -->
    <div v-else-if="!hasContent && isStreaming" class="flex items-center gap-2 text-gray-500">
      <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
      </svg>
      <span>{{ placeholder }}</span>
    </div>

    <!-- Text format -->
    <div v-else-if="format === 'text'" class="whitespace-pre-wrap">
      {{ content }}
      <span v-if="isStreaming" class="inline-block w-2 h-5 bg-blue-500 animate-pulse ml-1 align-middle"></span>
    </div>

    <!-- List format -->
    <ul v-else-if="format === 'list'" class="list-disc list-inside space-y-2">
      <li v-for="(item, index) in listItems" :key="index" class="text-gray-700">
        {{ item }}
      </li>
      <li v-if="isStreaming" class="list-none">
        <span class="inline-block w-2 h-5 bg-blue-500 animate-pulse align-middle"></span>
      </li>
    </ul>

    <!-- Checklist format -->
    <div v-else-if="format === 'checklist'" class="space-y-3">
      <div
        v-for="(item, index) in checklistItems"
        :key="index"
        class="flex items-start gap-3 p-3 bg-gray-50 rounded-lg"
      >
        <input
          type="checkbox"
          :checked="item.checked"
          class="mt-1 h-4 w-4 rounded border-gray-300 text-blue-500 focus:ring-blue-500"
        />
        <span class="flex-1 text-gray-700">{{ item.text }}</span>
      </div>
      <div v-if="isStreaming" class="flex items-center gap-2 text-gray-500 pl-3">
        <span class="inline-block w-2 h-5 bg-blue-500 animate-pulse"></span>
      </div>
    </div>
  </div>
</template>
