import api from './index'

export const alertAPI = {
  getAlertRules() {
    return api.get('/alerts/rules')
  },

  createAlertRule(data) {
    return api.post('/alerts/rules', data)
  },

  updateAlertRule(id, data) {
    return api.put(`/alerts/rules/${id}`, data)
  },

  deleteAlertRule(id) {
    return api.delete(`/alerts/rules/${id}`)
  },

  getAlerts(params) {
    return api.get('/alerts', { params })
  },

  markAsRead(id) {
    return api.put(`/alerts/${id}/read`)
  },

  markAllAsRead() {
    return api.put('/alerts/read-all')
  },

  getUnreadCount() {
    return api.get('/alerts/unread-count')
  }
}