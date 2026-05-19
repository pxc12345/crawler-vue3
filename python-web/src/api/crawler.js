import api from './index'

export const crawlerAPI = {
  start(data) {
    return api.post('/crawler/start', data)
  },
  stop() {
    return api.post('/crawler/stop')
  },
  getStatus() {
    return api.get('/crawler/status')
  },
  getDataList(params) {
    return api.get('/crawler/data', { params })
  },
  clearData() {
    return api.delete('/crawler/data')
  },
  getExportUrl() {
    return api.defaults.baseURL + '/crawler/export'
  }
}