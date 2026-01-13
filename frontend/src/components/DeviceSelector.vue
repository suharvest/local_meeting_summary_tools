<script setup>
import { ref, onMounted, inject } from 'vue'
import { getDevices } from '../api/devices'

const t = inject('t')

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])

const devices = ref([])
const loading = ref(false)
const error = ref(null)

async function loadDevices() {
  loading.value = true
  error.value = null

  try {
    devices.value = await getDevices()
  } catch (e) {
    error.value = e.message
    console.error('Failed to load devices:', e)
  } finally {
    loading.value = false
  }
}

function handleChange(event) {
  emit('update:modelValue', event.target.value)
}

onMounted(() => {
  loadDevices()
})
</script>

<template>
  <div class="mb-6">
    <label class="block text-sm font-medium text-gray-700 mb-2">
      {{ t('selectDevice') }}
    </label>

    <div v-if="loading" class="text-gray-500 text-sm">
      {{ t('loadingDevices') }}
    </div>

    <div v-else-if="error" class="text-red-500 text-sm">
      {{ error }}
      <button @click="loadDevices" class="ml-2 text-blue-500 underline">
        Retry
      </button>
    </div>

    <select
      v-else
      :value="modelValue"
      @change="handleChange"
      :disabled="disabled"
      class="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm
             focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
             disabled:bg-gray-100 disabled:cursor-not-allowed
             text-gray-900 bg-white"
    >
      <option value="">{{ t('selectDevicePlaceholder') }}</option>
      <option
        v-for="device in devices"
        :key="device.mac_address"
        :value="device.mac_address"
      >
        {{ device.display_name }}
        <span v-if="device.recording_count">
          ({{ t('recordingCount', { count: device.recording_count.toLocaleString() }) }})
        </span>
      </option>
    </select>
  </div>
</template>
