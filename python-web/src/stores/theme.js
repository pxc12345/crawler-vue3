import { defineStore } from 'pinia'
import { ref } from 'vue'

const THEMES = {
  default: {
    name: '默认蓝紫',
    label: '经典蓝紫渐变',
    colors: {
      '--bg-primary': '#0d1117',
      '--bg-card': 'rgba(22, 27, 34, 0.8)',
      '--border-color': 'rgba(255, 255, 255, 0.06)',
      '--text-primary': 'rgba(255, 255, 255, 0.9)',
      '--text-secondary': 'rgba(255, 255, 255, 0.55)',
      '--text-muted': 'rgba(255, 255, 255, 0.35)',
      '--accent-primary': '#4c6ef5',
      '--accent-secondary': '#7c3aed',
      '--accent-rgb': '76, 110, 245',
      '--gradient-primary': 'linear-gradient(135deg, #4c6ef5, #7c3aed)',
      '--btn-hover-shadow': '0 4px 20px rgba(76, 110, 245, 0.45)',
      '--card-hover-bg': 'rgba(76, 110, 245, 0.06)',
      '--active-color': '#7c8aff',
      '--active-bg': 'rgba(76, 110, 245, 0.12)',
      '--logo-gradient': 'linear-gradient(135deg, #4c6ef5, #7c3aed)',
      '--glow-color': 'rgba(76, 110, 245, 0.06)',
      '--glow-color-2': 'rgba(124, 58, 237, 0.04)',
      '--avatar-bg': 'linear-gradient(135deg, #4c6ef5, #7c3aed)',
    }
  },
  'space-gray': {
    name: '深空青灰',
    label: '沉稳太空灰',
    colors: {
      '--bg-primary': '#0d1117',
      '--bg-card': 'rgba(22, 27, 34, 0.85)',
      '--border-color': 'rgba(255, 255, 255, 0.05)',
      '--text-primary': 'rgba(255, 255, 255, 0.88)',
      '--text-secondary': 'rgba(255, 255, 255, 0.52)',
      '--text-muted': 'rgba(255, 255, 255, 0.32)',
      '--accent-primary': '#6b7280',
      '--accent-secondary': '#9ca3af',
      '--accent-rgb': '107, 114, 128',
      '--gradient-primary': 'linear-gradient(135deg, #6b7280, #9ca3af)',
      '--btn-hover-shadow': '0 4px 20px rgba(107, 114, 128, 0.4)',
      '--card-hover-bg': 'rgba(107, 114, 128, 0.06)',
      '--active-color': '#9ca3af',
      '--active-bg': 'rgba(107, 114, 128, 0.12)',
      '--logo-gradient': 'linear-gradient(135deg, #6b7280, #9ca3af)',
      '--glow-color': 'rgba(107, 114, 128, 0.05)',
      '--glow-color-2': 'rgba(156, 163, 175, 0.03)',
      '--avatar-bg': 'linear-gradient(135deg, #6b7280, #9ca3af)',
    }
  },
  'ice-blue': {
    name: '极地冰蓝',
    label: '清冷极地蓝',
    colors: {
      '--bg-primary': '#0c1119',
      '--bg-card': 'rgba(18, 28, 46, 0.85)',
      '--border-color': 'rgba(255, 255, 255, 0.05)',
      '--text-primary': 'rgba(255, 255, 255, 0.88)',
      '--text-secondary': 'rgba(255, 255, 255, 0.52)',
      '--text-muted': 'rgba(255, 255, 255, 0.32)',
      '--accent-primary': '#38bdf8',
      '--accent-secondary': '#0ea5e9',
      '--accent-rgb': '56, 189, 248',
      '--gradient-primary': 'linear-gradient(135deg, #38bdf8, #0ea5e9)',
      '--btn-hover-shadow': '0 4px 20px rgba(56, 189, 248, 0.4)',
      '--card-hover-bg': 'rgba(56, 189, 248, 0.06)',
      '--active-color': '#7dd3fc',
      '--active-bg': 'rgba(56, 189, 248, 0.12)',
      '--logo-gradient': 'linear-gradient(135deg, #38bdf8, #0ea5e9)',
      '--glow-color': 'rgba(56, 189, 248, 0.05)',
      '--glow-color-2': 'rgba(14, 165, 233, 0.03)',
      '--avatar-bg': 'linear-gradient(135deg, #38bdf8, #0ea5e9)',
    }
  },
  'night-green': {
    name: '暗夜青绿',
    label: '神秘暗夜绿',
    colors: {
      '--bg-primary': '#0d1210',
      '--bg-card': 'rgba(18, 28, 24, 0.85)',
      '--border-color': 'rgba(255, 255, 255, 0.05)',
      '--text-primary': 'rgba(255, 255, 255, 0.88)',
      '--text-secondary': 'rgba(255, 255, 255, 0.52)',
      '--text-muted': 'rgba(255, 255, 255, 0.32)',
      '--accent-primary': '#10b981',
      '--accent-secondary': '#059669',
      '--accent-rgb': '16, 185, 129',
      '--gradient-primary': 'linear-gradient(135deg, #10b981, #059669)',
      '--btn-hover-shadow': '0 4px 20px rgba(16, 185, 129, 0.4)',
      '--card-hover-bg': 'rgba(16, 185, 129, 0.06)',
      '--active-color': '#34d399',
      '--active-bg': 'rgba(16, 185, 129, 0.12)',
      '--logo-gradient': 'linear-gradient(135deg, #10b981, #059669)',
      '--glow-color': 'rgba(16, 185, 129, 0.05)',
      '--glow-color-2': 'rgba(5, 150, 105, 0.03)',
      '--avatar-bg': 'linear-gradient(135deg, #10b981, #059669)',
    }
  },
  'purple-gold': {
    name: '轻奢紫金',
    label: '奢华紫金调',
    colors: {
      '--bg-primary': '#0f0d14',
      '--bg-card': 'rgba(28, 24, 36, 0.85)',
      '--border-color': 'rgba(255, 255, 255, 0.05)',
      '--text-primary': 'rgba(255, 255, 255, 0.88)',
      '--text-secondary': 'rgba(255, 255, 255, 0.52)',
      '--text-muted': 'rgba(255, 255, 255, 0.32)',
      '--accent-primary': '#a855f7',
      '--accent-secondary': '#f59e0b',
      '--accent-rgb': '168, 85, 247',
      '--gradient-primary': 'linear-gradient(135deg, #a855f7, #f59e0b)',
      '--btn-hover-shadow': '0 4px 20px rgba(168, 85, 247, 0.4)',
      '--card-hover-bg': 'rgba(168, 85, 247, 0.06)',
      '--active-color': '#c084fc',
      '--active-bg': 'rgba(168, 85, 247, 0.12)',
      '--logo-gradient': 'linear-gradient(135deg, #a855f7, #f59e0b)',
      '--glow-color': 'rgba(168, 85, 247, 0.05)',
      '--glow-color-2': 'rgba(245, 158, 11, 0.03)',
      '--avatar-bg': 'linear-gradient(135deg, #a855f7, #f59e0b)',
    }
  },
  'cyber-aurora': {
    name: '赛博极光',
    label: '未来赛博风',
    colors: {
      '--bg-primary': '#0a0e17',
      '--bg-card': 'rgba(14, 20, 32, 0.85)',
      '--border-color': 'rgba(255, 255, 255, 0.05)',
      '--text-primary': 'rgba(255, 255, 255, 0.88)',
      '--text-secondary': 'rgba(255, 255, 255, 0.52)',
      '--text-muted': 'rgba(255, 255, 255, 0.32)',
      '--accent-primary': '#06b6d4',
      '--accent-secondary': '#ec4899',
      '--accent-rgb': '6, 182, 212',
      '--gradient-primary': 'linear-gradient(135deg, #06b6d4, #ec4899)',
      '--btn-hover-shadow': '0 4px 20px rgba(6, 182, 212, 0.4)',
      '--card-hover-bg': 'rgba(6, 182, 212, 0.06)',
      '--active-color': '#22d3ee',
      '--active-bg': 'rgba(6, 182, 212, 0.12)',
      '--logo-gradient': 'linear-gradient(135deg, #06b6d4, #ec4899)',
      '--glow-color': 'rgba(6, 182, 212, 0.05)',
      '--glow-color-2': 'rgba(236, 72, 153, 0.03)',
      '--avatar-bg': 'linear-gradient(135deg, #06b6d4, #ec4899)',
    }
  },
  'pure-black': {
    name: '极简曜黑',
    label: '纯粹极致黑',
    colors: {
      '--bg-primary': '#080808',
      '--bg-card': 'rgba(18, 18, 18, 0.9)',
      '--border-color': 'rgba(255, 255, 255, 0.04)',
      '--text-primary': 'rgba(255, 255, 255, 0.85)',
      '--text-secondary': 'rgba(255, 255, 255, 0.48)',
      '--text-muted': 'rgba(255, 255, 255, 0.28)',
      '--accent-primary': '#e5e7eb',
      '--accent-secondary': '#9ca3af',
      '--accent-rgb': '229, 231, 235',
      '--gradient-primary': 'linear-gradient(135deg, #e5e7eb, #9ca3af)',
      '--btn-hover-shadow': '0 4px 20px rgba(229, 231, 235, 0.3)',
      '--card-hover-bg': 'rgba(229, 231, 235, 0.04)',
      '--active-color': '#f3f4f6',
      '--active-bg': 'rgba(229, 231, 235, 0.1)',
      '--logo-gradient': 'linear-gradient(135deg, #e5e7eb, #9ca3af)',
      '--glow-color': 'rgba(229, 231, 235, 0.03)',
      '--glow-color-2': 'rgba(156, 163, 175, 0.02)',
      '--avatar-bg': 'linear-gradient(135deg, #e5e7eb, #9ca3af)',
    }
  }
}

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref(localStorage.getItem('app_theme') || 'default')
  const themeList = ref(THEMES)

  function getThemeInfo(name) {
    return THEMES[name] || THEMES['default']
  }

  function applyTheme(name) {
    currentTheme.value = name
    localStorage.setItem('app_theme', name)
    const theme = THEMES[name] || THEMES['default']
    const root = document.documentElement
    Object.entries(theme.colors).forEach(([key, val]) => {
      root.style.setProperty(key, val)
    })
  }

  function initTheme() {
    applyTheme(currentTheme.value)
  }

  async function switchTheme(name) {
    applyTheme(name)
    try {
      const { systemAPI } = await import('../api/system')
      await systemAPI.saveTheme(name)
    } catch {
      // 本地已生效，后端同步失败不影响
    }
  }

  async function syncFromServer() {
    try {
      const { systemAPI } = await import('../api/system')
      const res = await systemAPI.getTheme()
      if (res.data.success && res.data.data?.theme) {
        const serverTheme = res.data.data.theme
        if (THEMES[serverTheme]) {
          applyTheme(serverTheme)
        }
      }
    } catch {
      // 离线时使用本地缓存
    }
  }

  return {
    currentTheme,
    themeList,
    getThemeInfo,
    applyTheme,
    initTheme,
    switchTheme,
    syncFromServer
  }
})