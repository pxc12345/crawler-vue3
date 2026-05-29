import { defineStore } from 'pinia'
import { ref } from 'vue'

const THEMES = {
  'pure-black': {
    name: '极简曜黑',
    label: '纯粹极致黑',
    colors: {
      '--bg-primary': '#050505',
      '--bg-card': 'rgba(20, 20, 20, 0.94)',
      '--border-color': 'rgba(255, 255, 255, 0.07)',
      '--text-primary': 'rgba(255, 255, 255, 0.92)',
      '--text-secondary': 'rgba(255, 255, 255, 0.55)',
      '--text-muted': 'rgba(255, 255, 255, 0.30)',
      '--accent-primary': '#9ca3af',
      '--accent-secondary': '#4b5563',
      '--accent-rgb': '156, 163, 175',
      '--gradient-primary': 'linear-gradient(135deg, #9ca3af, #4b5563)',
      '--btn-shadow': '0 2px 12px rgba(156, 163, 175, 0.15)',
      '--btn-hover-shadow': '0 5px 22px rgba(156, 163, 175, 0.25)',
      '--card-hover-bg': 'rgba(255, 255, 255, 0.04)',
      '--active-color': '#e5e7eb',
      '--active-bg': 'rgba(255, 255, 255, 0.08)',
      '--logo-gradient': 'linear-gradient(135deg, #9ca3af, #4b5563)',
      '--glow-color': 'rgba(255, 255, 255, 0.03)',
      '--glow-color-2': 'rgba(255, 255, 255, 0.015)',
      '--avatar-bg': 'linear-gradient(135deg, #9ca3af, #4b5563)',
      '--btn-text-color': '#ffffff',
    }
  },
  'space-gray': {
    name: '深空青灰',
    label: '冷调星空灰',
    colors: {
      '--bg-primary': '#0f172a',
      '--bg-card': 'rgba(17, 24, 39, 0.88)',
      '--border-color': 'rgba(148, 163, 184, 0.1)',
      '--text-primary': 'rgba(255, 255, 255, 0.9)',
      '--text-secondary': 'rgba(255, 255, 255, 0.55)',
      '--text-muted': 'rgba(255, 255, 255, 0.32)',
      '--accent-primary': '#94a3b8',
      '--accent-secondary': '#64748b',
      '--accent-rgb': '148, 163, 184',
      '--gradient-primary': 'linear-gradient(135deg, #94a3b8, #64748b)',
      '--btn-shadow': '0 2px 12px rgba(148, 163, 184, 0.2)',
      '--btn-hover-shadow': '0 4px 20px rgba(148, 163, 184, 0.35)',
      '--card-hover-bg': 'rgba(148, 163, 184, 0.06)',
      '--active-color': '#cbd5e1',
      '--active-bg': 'rgba(148, 163, 184, 0.1)',
      '--logo-gradient': 'linear-gradient(135deg, #94a3b8, #64748b)',
      '--glow-color': 'rgba(148, 163, 184, 0.05)',
      '--glow-color-2': 'rgba(100, 116, 139, 0.03)',
      '--avatar-bg': 'linear-gradient(135deg, #94a3b8, #64748b)',
      '--btn-text-color': '#ffffff',
    }
  },
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
      '--btn-shadow': '0 2px 12px rgba(76, 110, 245, 0.3)',
      '--btn-hover-shadow': '0 4px 20px rgba(76, 110, 245, 0.45)',
      '--card-hover-bg': 'rgba(76, 110, 245, 0.06)',
      '--active-color': '#a5b4fc',
      '--active-bg': 'rgba(76, 110, 245, 0.12)',
      '--logo-gradient': 'linear-gradient(135deg, #4c6ef5, #7c3aed)',
      '--glow-color': 'rgba(76, 110, 245, 0.06)',
      '--glow-color-2': 'rgba(124, 58, 237, 0.04)',
      '--avatar-bg': 'linear-gradient(135deg, #4c6ef5, #7c3aed)',
      '--btn-text-color': '#ffffff',
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
      '--btn-shadow': '0 2px 12px rgba(56, 189, 248, 0.3)',
      '--btn-hover-shadow': '0 4px 20px rgba(56, 189, 248, 0.4)',
      '--card-hover-bg': 'rgba(56, 189, 248, 0.06)',
      '--active-color': '#7dd3fc',
      '--active-bg': 'rgba(56, 189, 248, 0.12)',
      '--logo-gradient': 'linear-gradient(135deg, #38bdf8, #0ea5e9)',
      '--glow-color': 'rgba(56, 189, 248, 0.05)',
      '--glow-color-2': 'rgba(14, 165, 233, 0.03)',
      '--avatar-bg': 'linear-gradient(135deg, #38bdf8, #0ea5e9)',
      '--btn-text-color': '#ffffff',
    }
  },
  'night-green': {
    name: '暗夜玫瑰',
    label: '深邃玫瑰红',
    colors: {
      '--bg-primary': '#1c1412',
      '--bg-card': 'rgba(30, 22, 20, 0.88)',
      '--border-color': 'rgba(212, 135, 122, 0.1)',
      '--text-primary': 'rgba(255, 255, 255, 0.9)',
      '--text-secondary': 'rgba(255, 255, 255, 0.52)',
      '--text-muted': 'rgba(255, 255, 255, 0.30)',
      '--accent-primary': '#d4877a',
      '--accent-secondary': '#b06d61',
      '--accent-rgb': '212, 135, 122',
      '--gradient-primary': 'linear-gradient(135deg, #d4877a, #b06d61)',
      '--btn-shadow': '0 2px 12px rgba(212, 135, 122, 0.25)',
      '--btn-hover-shadow': '0 4px 20px rgba(212, 135, 122, 0.4)',
      '--card-hover-bg': 'rgba(212, 135, 122, 0.06)',
      '--active-color': '#ecc7bf',
      '--active-bg': 'rgba(212, 135, 122, 0.1)',
      '--logo-gradient': 'linear-gradient(135deg, #d4877a, #b06d61)',
      '--glow-color': 'rgba(212, 135, 122, 0.05)',
      '--glow-color-2': 'rgba(176, 109, 97, 0.03)',
      '--avatar-bg': 'linear-gradient(135deg, #d4877a, #b06d61)',
      '--btn-text-color': '#ffffff',
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
      '--btn-shadow': '0 2px 12px rgba(168, 85, 247, 0.3)',
      '--btn-hover-shadow': '0 4px 20px rgba(168, 85, 247, 0.45)',
      '--card-hover-bg': 'rgba(168, 85, 247, 0.06)',
      '--active-color': '#d8b4fe',
      '--active-bg': 'rgba(168, 85, 247, 0.12)',
      '--logo-gradient': 'linear-gradient(135deg, #a855f7, #f59e0b)',
      '--glow-color': 'rgba(168, 85, 247, 0.05)',
      '--glow-color-2': 'rgba(245, 158, 11, 0.03)',
      '--avatar-bg': 'linear-gradient(135deg, #a855f7, #f59e0b)',
      '--btn-text-color': '#ffffff',
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
      '--btn-shadow': '0 2px 12px rgba(6, 182, 212, 0.3)',
      '--btn-hover-shadow': '0 4px 20px rgba(6, 182, 212, 0.45)',
      '--card-hover-bg': 'rgba(6, 182, 212, 0.06)',
      '--active-color': '#67e8f9',
      '--active-bg': 'rgba(6, 182, 212, 0.12)',
      '--logo-gradient': 'linear-gradient(135deg, #06b6d4, #ec4899)',
      '--glow-color': 'rgba(6, 182, 212, 0.05)',
      '--glow-color-2': 'rgba(236, 72, 153, 0.03)',
      '--avatar-bg': 'linear-gradient(135deg, #06b6d4, #ec4899)',
      '--btn-text-color': '#ffffff',
    }
  },
  'elegant-white': {
    name: '雅致白',
    label: '纯净优雅白',
    colors: {
      '--bg-primary': '#ffffff',
      '--bg-card': 'rgba(255, 255, 255, 0.96)',
      '--border-color': 'rgba(0, 0, 0, 0.08)',
      '--text-primary': '#1a1a2e',
      '--text-secondary': '#4a5568',
      '--text-muted': '#6b7280',
      '--accent-primary': '#374151',
      '--accent-secondary': '#1f2937',
      '--accent-rgb': '55, 65, 81',
      '--gradient-primary': 'linear-gradient(135deg, #374151, #1f2937)',
      '--btn-shadow': '0 2px 12px rgba(55, 65, 81, 0.15)',
      '--btn-hover-shadow': '0 4px 20px rgba(55, 65, 81, 0.25)',
      '--card-hover-bg': 'rgba(55, 65, 81, 0.04)',
      '--active-color': '#1f2937',
      '--active-bg': 'rgba(55, 65, 81, 0.08)',
      '--logo-gradient': 'linear-gradient(135deg, #374151, #1f2937)',
      '--glow-color': 'rgba(55, 65, 81, 0.04)',
      '--glow-color-2': 'rgba(31, 41, 55, 0.03)',
      '--avatar-bg': 'linear-gradient(135deg, #374151, #1f2937)',
      '--btn-text-color': '#ffffff',
      '--link-color': '#374151',
      '--link-hover-color': '#1f2937',
      '--primary-600': '#374151',
      '--primary-700': '#1f2937',
      '--primary-800': '#111827',
    }
  }
}

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref(localStorage.getItem('app_theme') || 'pure-black')
  const themeList = ref(THEMES)

  function getThemeInfo(name) {
    return THEMES[name] || THEMES['pure-black']
  }

  function applyTheme(name) {
    currentTheme.value = name
    localStorage.setItem('app_theme', name)
    const theme = THEMES[name] || THEMES['pure-black']
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
