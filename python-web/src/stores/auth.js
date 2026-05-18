import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI, userAPI } from '../api'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)

  function setAuth(data) {
    accessToken.value = data.access_token
    refreshToken.value = data.refresh_token
    user.value = data.user
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    localStorage.setItem('user', JSON.stringify(data.user))
  }

  function clearAuth() {
    accessToken.value = ''
    refreshToken.value = ''
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  async function login(identifier, password) {
    const response = await authAPI.login({ identifier, password })
    if (response.data.success) {
      setAuth(response.data.data)
    }
    return response.data
  }

  async function register(username, password, email, phone) {
    const response = await authAPI.register({ username, password, email, phone })
    return response.data
  }

  async function logout() {
    try {
      if (refreshToken.value) {
        await authAPI.logout(refreshToken.value)
      }
    } finally {
      clearAuth()
    }
  }

  async function fetchProfile() {
    const response = await userAPI.getProfile()
    if (response.data.success) {
      user.value = response.data.data
      localStorage.setItem('user', JSON.stringify(response.data.data))
    }
    return response.data
  }

  return {
    accessToken,
    refreshToken,
    user,
    isAuthenticated,
    login,
    register,
    logout,
    fetchProfile,
    clearAuth
  }
})
