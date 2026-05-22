import api from './index'

export const systemAPI = {
  getLogs(params) {
    return api.get('/system/logs', { params })
  },

  clearLogs(beforeDays) {
    return api.delete('/system/logs', { data: { before_days: beforeDays } })
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
  }
}