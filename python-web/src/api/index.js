import axios from 'axios'
import { API_BASE_URL } from '../config/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry && originalRequest.url !== '/auth/refresh') {
      originalRequest._retry = true
      
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await api.post('/auth/refresh', { refresh_token: refreshToken })
          if (response.data.success) {
            localStorage.setItem('access_token', response.data.data.access_token)
            originalRequest.headers.Authorization = `Bearer ${response.data.data.access_token}`
            return api(originalRequest)
          } else {
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            localStorage.removeItem('user')
            window.location.href = '/login'
          }
        } catch (refreshError) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          window.location.href = '/login'
        }
      } else {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  register(data) {
    return api.post('/auth/register', data)
  },
  login(data) {
    return api.post('/auth/login', data)
  },
  refreshToken(refreshToken) {
    return api.post('/auth/refresh', { refresh_token: refreshToken })
  },
  logout(refreshToken) {
    return api.post('/auth/logout', { refresh_token: refreshToken })
  },
  sendForgotPasswordCode(target) {
    return api.post('/auth/forgot-password/send-code', { target })
  },
  verifyForgotPasswordCode(data) {
    return api.post('/auth/forgot-password/verify-code', data)
  },
  resetPassword(data) {
    return api.post('/auth/forgot-password/reset', data)
  },
  changePassword(data) {
    return api.post('/auth/change-password', data)
  }
}

export const userAPI = {
  getProfile() {
    return api.get('/user/profile')
  },

  updateProfile(data) {
    return api.put('/user/profile', data)
  }
}

export function downloadFile(url, filename, format = 'csv') {
  return api.get(url, {
    responseType: 'blob',
    params: { format }
  }).then(response => {
    const blob = response.data instanceof Blob ? response.data : new Blob([response.data])
    const downloadUrl = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = downloadUrl
    const contentDisposition = response.headers['content-disposition']
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?(.+)"?/)
      if (match) filename = match[1]
    }
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(downloadUrl)
    return true
  })
}

export default api
