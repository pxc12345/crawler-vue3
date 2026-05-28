const API_BASE_URL = 'https://crawler-vue3.onrender.com'

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

  getStatistics() {
    return request('/students/statistics')
  },

  uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)
    return fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData
    }).then(res => res.json())
  },

  async exportStudents() {
    try {
      const response = await fetch(`${API_BASE_URL}/students/export`)
      if (!response.ok) {
        throw new Error('导出失败')
      }
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      const contentDisposition = response.headers.get('Content-Disposition')
      let filename = 'students_export.csv'
      if (contentDisposition) {
        const match = contentDisposition.match(/filename=["']?(.+)["']?/)
        if (match) filename = match[1]
      }
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      throw new Error(error.message || '导出失败')
    }
  },

  importStudents(file) {
    const formData = new FormData()
    formData.append('file', file)
    return fetch(`${API_BASE_URL}/students/import`, {
      method: 'POST',
      body: formData
    }).then(res => res.json())
  }
}