import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useBlessingStore = defineStore('blessing', () => {
  const defaultTheme = {
    id: null as number | null,
    name: '默认晨雾',
    category: '高级粉色系',
    background_color: '#f8efe9',
    title_color: '#7b2f36',
    body_color: '#3d312e',
    button_color: '#cf6f5d',
    card_color: '#fffaf6',
  }

  const defaultEffectProfile = {
    id: null as number | null,
    name: '默认高级流光',
    welcome_effects: ['mist-glow', 'light-particles'],
    intro_effects: ['star-twinkle', 'glass-bubble'],
    main_effects: ['radiance-burst', 'halo-ring'],
    closing_effects: ['signature-draw', 'seal-fade'],
    particle_density: 0.65,
    motion_level: 0.55,
    glow_intensity: 0.72,
  }

  const username = ref('')
  const role = ref('')
  const bgColor = ref(defaultTheme.background_color)
  const textColor = ref(defaultTheme.body_color)
  const theme = ref({ ...defaultTheme })
  const effectProfile = ref({ ...defaultEffectProfile })

  const globalMode = ref('birthday')
  const currentFestival = ref('')
  const birthdayText = ref('')
  const festivalText = ref('')
  const contentSteps = ref<any[]>([])
  const updateTime = ref('')

  function setUser(user: string, userRole: string, bg: string, text: string, themeData?: any, effectData?: any) {
    username.value = user
    role.value = userRole
    bgColor.value = bg
    textColor.value = text
    theme.value = {
      ...defaultTheme,
      ...(themeData || {}),
      background_color: bg || themeData?.background_color || defaultTheme.background_color,
      body_color: text || themeData?.body_color || defaultTheme.body_color,
    }
    effectProfile.value = {
      ...defaultEffectProfile,
      ...(effectData || {}),
      welcome_effects: effectData?.welcome_effects || defaultEffectProfile.welcome_effects,
      intro_effects: effectData?.intro_effects || defaultEffectProfile.intro_effects,
      main_effects: effectData?.main_effects || defaultEffectProfile.main_effects,
      closing_effects: effectData?.closing_effects || defaultEffectProfile.closing_effects,
    }
    sessionStorage.setItem('blessing_username', user)
    sessionStorage.setItem('blessing_role', userRole)
    sessionStorage.setItem('blessing_bg', bg)
    sessionStorage.setItem('blessing_text', text)
    sessionStorage.setItem('blessing_theme', JSON.stringify(theme.value))
    sessionStorage.setItem('blessing_effect_profile', JSON.stringify(effectProfile.value))
  }

  function restoreUser() {
    username.value = sessionStorage.getItem('blessing_username') || ''
    role.value = sessionStorage.getItem('blessing_role') || ''
    bgColor.value = sessionStorage.getItem('blessing_bg') || defaultTheme.background_color
    textColor.value = sessionStorage.getItem('blessing_text') || defaultTheme.body_color
    try {
      theme.value = { ...defaultTheme, ...JSON.parse(sessionStorage.getItem('blessing_theme') || '{}') }
    } catch {
      theme.value = { ...defaultTheme }
    }
    try {
      effectProfile.value = { ...defaultEffectProfile, ...JSON.parse(sessionStorage.getItem('blessing_effect_profile') || '{}') }
    } catch {
      effectProfile.value = { ...defaultEffectProfile }
    }
  }

  function clearUser() {
    username.value = ''
    role.value = ''
    bgColor.value = defaultTheme.background_color
    textColor.value = defaultTheme.body_color
    theme.value = { ...defaultTheme }
    effectProfile.value = { ...defaultEffectProfile }
    sessionStorage.clear()
  }

  function setSettings(mode: string, festival: string, bText: string, fText: string, time: string, steps: any[] = []) {
    globalMode.value = mode
    currentFestival.value = festival
    birthdayText.value = bText
    festivalText.value = fText
    contentSteps.value = steps
    updateTime.value = time
  }

  return {
    username,
    role,
    bgColor,
    textColor,
    theme,
    effectProfile,
    globalMode,
    currentFestival,
    birthdayText,
    festivalText,
    contentSteps,
    updateTime,
    setUser,
    restoreUser,
    clearUser,
    setSettings,
  }
})
