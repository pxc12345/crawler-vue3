import api from './index'

export const dataAPI = {
  getDataList(params) {
    return api.get('/data', { params })
  },

  deleteData(id) {
    return api.delete(`/data/${id}`)
  },

  batchDeleteData(ids) {
    return api.post('/data/batch-delete', { ids })
  },

  cleanData(data) {
    return api.post('/data/clean', data)
  },

  exportData(params) {
    return api.get('/data/export', { params })
  },

  autoWriteConfig(data) {
    return api.post('/data/auto-write-config', data)
  },

  pushConfig(data) {
    return api.post('/data/push-config', data)
  }
}