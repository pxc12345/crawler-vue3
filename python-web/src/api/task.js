import api from './index'

export const taskAPI = {
  getTasks(params) {
    return api.get('/tasks', { params })
  },

  getTask(id) {
    return api.get(`/tasks/${id}`)
  },

  createTask(data) {
    return api.post('/tasks', data)
  },

  updateTask(id, data) {
    return api.put(`/tasks/${id}`, data)
  },

  deleteTask(id) {
    return api.delete(`/tasks/${id}`)
  },

  startTask(id) {
    return api.post(`/tasks/${id}/start`)
  },

  stopTask(id) {
    return api.post(`/tasks/${id}/stop`)
  },

  getTemplates(params) {
    return api.get('/tasks/templates', { params })
  },

  createTemplate(data) {
    return api.post('/tasks/templates', data)
  },

  updateTemplate(id, data) {
    return api.put(`/tasks/templates/${id}`, data)
  },

  deleteTemplate(id) {
    return api.delete(`/tasks/templates/${id}`)
  },

  getTemplateById(id) {
    return api.get(`/tasks/templates/${id}`)
  },

  useTemplate(id) {
    return api.post(`/tasks/templates/${id}/use`)
  },

  toggleTemplateFavorite(id) {
    return api.post(`/tasks/templates/${id}/favorite`)
  },

  getVersions(taskId) {
    return api.get(`/tasks/${taskId}/versions`)
  },

  getDataSummary(taskId) {
    return api.get(`/tasks/${taskId}/data-summary`)
  },

  rollbackVersion(taskId, versionId) {
    return api.post(`/tasks/${taskId}/versions/rollback`, { version_id: versionId })
  },

  getFavorites() {
    return api.get('/tasks/favorites')
  },

  addFavorite(taskId) {
    return api.post(`/tasks/${taskId}/favorite`)
  },

  removeFavorite(taskId) {
    return api.delete(`/tasks/${taskId}/favorite`)
  },

  restartFailedTasks() {
    return api.post('/tasks/restart-failed')
  }
}