import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE || 'https://crawler-vue3.onrender.com'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const msg = error.response?.data?.msg || '网络请求失败，请稍后重试'
    if (typeof window !== 'undefined' && (window as any).__showToast) {
      ;(window as any).__showToast(msg)
    }
    return Promise.reject(error)
  },
)

export function login(username: string) {
  return api.post('/api/login', { username })
}

export function getSettings() {
  return api.get('/api/settings/get')
}

export function updateSettings(data: {
  global_mode: string
  birthday_default_text: string
  festival_default_text: string
}) {
  return api.post('/api/settings/update', data)
}

export function refreshNearestFestival() {
  return api.get('/api/festival/nearest')
}

export function getUserList() {
  return api.get('/api/user/list')
}

export function saveUser(data: {
  id?: number
  username: string
  theme_id: number | null
  effect_profile_id: number | null
}) {
  return api.post('/api/user/save', data)
}

export function deleteUser(id: number) {
  return api.delete('/api/user/delete', { data: { id } })
}

export function getThemeList() {
  return api.get('/api/theme/list')
}

export function saveTheme(data: {
  id?: number
  name: string
  category: string
  background_color: string
  title_color: string
  body_color: string
  button_color: string
  card_color: string
  sort?: number
}) {
  return api.post('/api/theme/save', data)
}

export function deleteTheme(id: number) {
  return api.delete('/api/theme/delete', { data: { id } })
}

export function getEffectProfiles() {
  return api.get('/api/effect/list')
}

export function saveEffectProfile(data: {
  id?: number
  name: string
  welcome_effects: string[]
  intro_effects: string[]
  main_effects: string[]
  closing_effects: string[]
  particle_density: number
  motion_level: number
  glow_intensity: number
  sort?: number
}) {
  return api.post('/api/effect/save', data)
}

export function deleteEffectProfile(id: number) {
  return api.delete('/api/effect/delete', { data: { id } })
}

export function getContentConfig(mode?: string) {
  return api.get('/api/content/get', { params: mode ? { mode } : {} })
}

export function saveContentConfig(data: {
  mode: string
  steps: Array<{
    step_key: string
    step_order: number
    title: string
    body: string
  }>
}) {
  return api.post('/api/content/save', data)
}

export default api
