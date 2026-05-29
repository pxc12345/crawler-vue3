import api from './index'

export const proxyAPI = {
  getProxies(params) {
    return api.get('/proxy/list', { params })
  },

  addProxy(data) {
    return api.post('/proxy/add', data)
  },

  deleteProxy(id) {
    return api.delete(`/proxy/${id}`)
  },

  refreshProxy(id) {
    return api.post(`/proxy/${id}/refresh`)
  },

  getProxyGroups() {
    return api.get('/proxy/groups')
  },

  createProxyGroup(data) {
    return api.post('/proxy/groups', data)
  },

  deleteProxyGroup(id) {
    return api.delete(`/proxy/groups/${id}`)
  },

  assignProxyToGroup(data) {
    return api.post('/proxy/groups/assign', data)
  },

  syncGroupProxies(groupId, proxyIds) {
    return api.post('/proxy/groups/sync', {
      group_id: groupId,
      proxy_ids: proxyIds
    })
  },

  getBlacklist() {
    return api.get('/proxy/blacklist')
  },

  addBlacklist(data) {
    return api.post('/proxy/blacklist', data)
  },

  removeBlacklist(id) {
    return api.delete(`/proxy/blacklist/${id}`)
  },

  getWhitelist() {
    return api.get('/proxy/whitelist')
  },

  addWhitelist(data) {
    return api.post('/proxy/whitelist', data)
  },

  removeWhitelist(id) {
    return api.delete(`/proxy/whitelist/${id}`)
  },

  getRateLimits() {
    return api.get('/proxy/rate-limits')
  },

  setRateLimit(data) {
    return api.post('/proxy/rate-limits', data)
  }
}