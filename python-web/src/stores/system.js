import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { alertAPI } from '../api/alert'
import { proxyAPI } from '../api/proxy'
import { systemAPI } from '../api/system'

export const useSystemStore = defineStore('system', () => {
  const alerts = ref([])
  const unreadCount = ref(0)
  const proxies = ref([])
  const blacklist = ref([])
  const whitelist = ref([])
  const rateLimits = ref([])
  const systemLogs = ref([])
  const resources = ref({})

  async function fetchAlerts(params) {
    const response = await alertAPI.getAlerts(params)
    alerts.value = response.data.data || response.data
    return response.data
  }

  async function markAlertRead(id) {
    const response = await alertAPI.markAsRead(id)
    if (response.data.success) {
      const index = alerts.value.findIndex(a => a.id === id)
      if (index !== -1) {
        alerts.value[index] = { ...alerts.value[index], read: true }
      }
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
    return response.data
  }

  async function fetchProxies(params) {
    const response = await proxyAPI.getProxies(params)
    proxies.value = response.data.data || response.data
    return response.data
  }

  async function addProxy(data) {
    const response = await proxyAPI.addProxy(data)
    if (response.data.success) {
      proxies.value.push(response.data.data)
    }
    return response.data
  }

  async function deleteProxy(id) {
    const response = await proxyAPI.deleteProxy(id)
    if (response.data.success) {
      proxies.value = proxies.value.filter(p => p.id !== id)
    }
    return response.data
  }

  async function refreshProxies() {
    const response = await proxyAPI.getProxies()
    proxies.value = response.data.data || response.data
    return response.data
  }

  async function fetchBlacklist() {
    const response = await proxyAPI.getBlacklist()
    blacklist.value = response.data.data || response.data
    return response.data
  }

  async function addBlacklist(data) {
    const response = await proxyAPI.addBlacklist(data)
    if (response.data.success) {
      blacklist.value.push(response.data.data)
    }
    return response.data
  }

  async function removeBlacklist(id) {
    const response = await proxyAPI.removeBlacklist(id)
    if (response.data.success) {
      blacklist.value = blacklist.value.filter(b => b.id !== id)
    }
    return response.data
  }

  async function fetchWhitelist() {
    const response = await proxyAPI.getWhitelist()
    whitelist.value = response.data.data || response.data
    return response.data
  }

  async function addWhitelist(data) {
    const response = await proxyAPI.addWhitelist(data)
    if (response.data.success) {
      whitelist.value.push(response.data.data)
    }
    return response.data
  }

  async function removeWhitelist(id) {
    const response = await proxyAPI.removeWhitelist(id)
    if (response.data.success) {
      whitelist.value = whitelist.value.filter(w => w.id !== id)
    }
    return response.data
  }

  async function fetchRateLimits() {
    const response = await proxyAPI.getRateLimits()
    rateLimits.value = response.data.data || response.data
    return response.data
  }

  async function setRateLimit(data) {
    const response = await proxyAPI.setRateLimit(data)
    if (response.data.success) {
      fetchRateLimits()
    }
    return response.data
  }

  async function fetchLogs(params) {
    const response = await systemAPI.getLogs(params)
    systemLogs.value = response.data.data || response.data
    return response.data
  }

  async function clearLogs(beforeDays) {
    const response = await systemAPI.clearLogs(beforeDays)
    if (response.data.success) {
      systemLogs.value = []
    }
    return response.data
  }

  async function fetchResources() {
    const response = await systemAPI.getResources()
    resources.value = response.data.data || response.data
    return response.data
  }

  return {
    alerts,
    unreadCount,
    proxies,
    blacklist,
    whitelist,
    rateLimits,
    systemLogs,
    resources,
    fetchAlerts,
    markAlertRead,
    fetchProxies,
    addProxy,
    deleteProxy,
    refreshProxies,
    fetchBlacklist,
    addBlacklist,
    removeBlacklist,
    fetchWhitelist,
    addWhitelist,
    removeWhitelist,
    fetchRateLimits,
    setRateLimit,
    fetchLogs,
    clearLogs,
    fetchResources
  }
})