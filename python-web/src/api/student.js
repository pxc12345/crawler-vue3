const API_BASE_URL = 'http://127.0.0.1:5000'

async function request(url, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    })
    const data = await response.json()
    if (data.code !== 200 && data.code !== 201) {
      throw new Error(data.message || '请求失败')
    }
    return data
  } catch (error) {
    throw new Error(error.message || '网络错误')
  }
}

export const studentApi = {
  getAll() {
    return request('/students')
  },

  getById(id) {
    return request(`/students/${id}`)
  },

  search(name) {
    return request(`/students/search?name=${encodeURIComponent(name)}`)
  },

  create(student) {
    return request('/students', {
      method: 'POST',
      body: JSON.stringify(student)
    })
  },

  update(id, student) {
    return request(`/students/${id}`, {
      method: 'PUT',
      body: JSON.stringify(student)
    })
  },

  delete(id) {
    return request(`/students/${id}`, {
      method: 'DELETE'
    })
  },

  batchDelete(ids) {
    return request('/students/batch', {
      method: 'DELETE',
      body: JSON.stringify({ ids })
    })
  },

  getStatistics() {
    return request('/students/statistics')
  },

  healthCheck() {
    return request('/health')
  }
}
