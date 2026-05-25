import api from './index'

export const dataAPI = {
  getDataList(params) {
    return api.get('/data', { params })
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