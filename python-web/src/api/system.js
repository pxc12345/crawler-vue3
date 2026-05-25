import api from './index'

export const systemAPI = {
  getLogs(params) {
    return api.get('/system/logs', { params })
  },

  clearLogs(days) {
    return api.post('/system/logs/clear', { days: days })
  },

  getResources() {
    return api.get('/system/resources')
  },

  getDashboardStats() {
    return api.get('/system/dashboard-stats')
  },

  getSettings() {
    return api.get('/system/settings')
  },

  updateSetting(key, data) {
    return api.put(`/system/settings/${key}`, data)
  },

  getUserPreferences() {
    return api.get('/system/user/preferences')
  },

  saveUserPreferences(data) {
    return api.put('/system/user/preferences', data)
  },

  getSettingsBatch() {
    return api.get('/system/settings/batch')
  },

  saveSettingsBatch(data) {
    return api.put('/system/settings/batch', data)
  },

  getTheme() {
    return api.get('/user/theme')
  },

  saveTheme(theme) {
    return api.put('/user/theme', { theme })
  }
}