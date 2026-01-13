/**
 * Device API functions
 */

import { get } from './index'

/**
 * Get list of all devices
 */
export async function getDevices() {
  const response = await get('/api/devices')
  return response.data
}

/**
 * Get device details by MAC address
 */
export async function getDevice(macAddress) {
  const response = await get(`/api/devices/${macAddress}`)
  return response.data
}

/**
 * Get recent recordings from a device
 */
export async function getRecentRecordings(macAddress, limit = 20) {
  const response = await get(`/api/devices/${macAddress}/recent?limit=${limit}`)
  return response.data
}
