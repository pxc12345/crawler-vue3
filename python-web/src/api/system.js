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

  getSettings() {
    return api.get('/system/settings')
  },

  updateSetting(key, data) {
    return api.put(`/system/settings/${key}`, data)
  }
}