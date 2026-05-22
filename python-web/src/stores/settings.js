import { defineStore } from 'pinia'
import { ref } from 'vue'
import { systemAPI } from '../api/system'

export const useSettingsStore = defineStore('settings', () => {
  const theme = ref(localStorage.getItem('theme') || 'light')
  const preferences = ref({})
  const globalSettings = ref({})

  async function fetchSettings() {
    const response = await systemAPI.getSettings()
    if (response.data.success || response.data.data) {
      globalSettings.value = response.data.data || response.data
    }
    return response.data
  }

  async function updateSetting(key, data) {
    const response = await systemAPI.updateSetting(key, data)
    if (response.data.success) {
      globalSettings.value = { ...globalSettings.value, [key]: response.data.data }
    }
    return response.data
  }

  async function fetchPreferences() {
    const response = await systemAPI.getSettings()
    if (response.data.success || response.data.data) {
      preferences.value = (response.data.data || response.data).preferences || {}
    }
    return response.data
  }

  async function updatePreference(key, value) {
    const data = { [key]: value }
    const response = await systemAPI.updateSetting('preferences', data)
    if (response.data.success) {
      preferences.value = { ...preferences.value, [key]: value }
    }
    return response.data
  }

  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    localStorage.setItem('theme', theme.value)
    document.documentElement.setAttribute('data-theme', theme.value)
  }

  return {
    theme,
    preferences,
    globalSettings,
    fetchSettings,
    updateSetting,
    fetchPreferences,
    updatePreference,
    toggleTheme
  }
})