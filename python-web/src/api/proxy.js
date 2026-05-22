import api from './index'

export const proxyAPI = {
  getProxies(params) {
    return api.get('/proxies', { params })
  },

  addProxy(data) {
    return api.post('/proxies', data)
  },

  deleteProxy(id) {
    return api.delete(`/proxies/${id}`)
  },

  refreshProxy(id) {
    return api.post(`/proxies/${id}/refresh`)
  },

  getProxyGroups() {
    return api.get('/proxies/groups')
  },

  createProxyGroup(data) {
    return api.post('/proxies/groups', data)
  },

  assignProxyToGroup(data) {
    return api.post('/proxies/assign', data)
  },

  getBlacklist() {
    return api.get('/proxies/blacklist')
  },

  addBlacklist(data) {
    return api.post('/proxies/blacklist', data)
  },

  removeBlacklist(id) {
    return api.delete(`/proxies/blacklist/${id}`)
  },

  getWhitelist() {
    return api.get('/proxies/whitelist')
  },

  addWhitelist(data) {
    return api.post('/proxies/whitelist', data)
  },

  removeWhitelist(id) {
    return api.delete(`/proxies/whitelist/${id}`)
  },

  getRateLimits() {
    return api.get('/proxies/rate-limits')
  },

  setRateLimit(data) {
    return api.post('/proxies/rate-limits', data)
  }
}