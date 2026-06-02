<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import html2canvas from 'html2canvas'

import { getSettings } from '@/utils/api'
import { useBlessingStore } from '@/stores/blessing'

type StepItem = {
  step_key: string
  step_name?: string
  step_order: number
  title: string
  body: string
}

const router = useRouter()
const store = useBlessingStore()

const loading = ref(true)
const currentStep = ref(0)
const stepVisible = ref(false)
const steps = ref<StepItem[]>([])

const theme = computed(() => store.theme)
const effectProfile = computed(() => store.effectProfile)
const activeStep = computed(() => steps.value[currentStep.value] || steps.value[0])
const isLastStep = computed(() => currentStep.value === steps.value.length - 1)

const activeEffects = computed(() => {
  const key = activeStep.value?.step_key
  if (key === 'welcome') return effectProfile.value.welcome_effects || []
  if (key === 'intro') return effectProfile.value.intro_effects || []
  if (key === 'main') return effectProfile.value.main_effects || []
  return effectProfile.value.closing_effects || []
})

const particleCount = computed(() => Math.max(8, Math.round((effectProfile.value.particle_density || 0.65) * 18)))
const effectVars = computed(() => ({
  '--theme-bg': theme.value.background_color,
  '--theme-card': theme.value.card_color,
  '--theme-title': theme.value.title_color,
  '--theme-body': theme.value.body_color,
  '--theme-button': theme.value.button_color,
  '--particle-density': String(effectProfile.value.particle_density || 0.65),
  '--motion-level': String(effectProfile.value.motion_level || 0.55),
  '--glow-intensity': String(effectProfile.value.glow_intensity || 0.72),
}) as Record<string, string>)

const fallbackBirthdaySteps: StepItem[] = [
  { step_key: 'welcome', step_name: '开场欢迎页', step_order: 1, title: '今夜为你亮灯', body: '把日历翻到今天，连风都像替你轻声报喜。愿你推开这一页时，先被温柔接住，再被喜悦慢慢包围。' },
  { step_key: 'intro', step_name: '导语页', step_order: 2, title: '把好时光留给你', body: '愿你走过的每一步都算数，认真喜欢过的事情都能开花，努力熬过的夜晚都能在未来变成星光。' },
  { step_key: 'main', step_name: '主祝福页', step_order: 3, title: '愿望开始靠近', body: '愿你新一岁的生活有热烈也有安稳，有奔赴远方的勇气，也有回到日常的松弛。愿欢喜有回应，期待有着落，生日快乐。' },
  { step_key: 'closing', step_name: '收尾落款页', step_order: 4, title: '把祝福珍藏', body: '把这一份偏爱好好收下吧。愿它陪你度过明亮的时刻，也陪你穿过普通的日子，提醒你一直值得被认真祝福。' },
]

const fallbackFestivalSteps: StepItem[] = [
  { step_key: 'welcome', step_name: '开场欢迎页', step_order: 1, title: '节日已至', body: '节日像一封刚拆开的信，先把热闹送到门前，再把惦念慢慢放进心里。今天这一份祝福，也专门为你而来。' },
  { step_key: 'intro', step_name: '导语页', step_order: 2, title: '愿此刻被照亮', body: '愿你无论身在何处，都能在这个节点里感受到陪伴、松弛和被惦记的安心，让生活暂时停下来，对你多一点温柔。' },
  { step_key: 'main', step_name: '主祝福页', step_order: 3, title: '平安喜乐常在', body: '愿这个节日替你带来轻松和好消息，愿平安常在，喜乐常在，心之所向都有回音。' },
  { step_key: 'closing', step_name: '收尾落款页', step_order: 4, title: '心意缓缓落下', body: '把这份节日心意留在今天，也带进之后的日子里。愿你接下来遇见的人和事，都能继续把温暖递给你。' },
]

onMounted(async () => {
  store.restoreUser()
  if (!store.username) {
    router.push('/login')
    return
  }

  try {
    const res: any = await getSettings()
    if (res.code === 200) {
      const data = res.data
      store.setSettings(data.global_mode, data.current_nearest_festival, data.birthday_default_text, data.festival_default_text, data.update_time, data.content_steps || [])
      steps.value = (data.content_steps?.length ? data.content_steps : fallbackSteps()).map((item: any) => ({ ...item }))
    }
  } catch {
    steps.value = fallbackSteps()
  }

  if (!steps.value.length) steps.value = fallbackSteps()

  loading.value = false
  setTimeout(() => {
    stepVisible.value = true
  }, 100)
})

function fallbackSteps() {
  return (store.globalMode === 'festival' ? fallbackFestivalSteps : fallbackBirthdaySteps).map((item) => ({ ...item }))
}

function hasEffect(effectName: string) {
  return activeEffects.value.includes(effectName)
}

function switchStep(nextIndex: number) {
  stepVisible.value = false
  setTimeout(() => {
    currentStep.value = nextIndex
    stepVisible.value = true
  }, 180)
}

function nextStep() {
  if (currentStep.value < steps.value.length - 1) switchStep(currentStep.value + 1)
}

function prevStep() {
  if (currentStep.value > 0) switchStep(currentStep.value - 1)
}

async function saveImage() {
  const target = document.getElementById('blessing-card')
  if (!target) return
  try {
    const canvas = await html2canvas(target, {
      backgroundColor: theme.value.background_color,
      scale: 2,
      useCORS: true,
    })
    const link = document.createElement('a')
    link.download = `${store.username}-blessing.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  } catch {
    showToast('保存失败，请重试')
  }
}

function shareBlessing() {
  if (navigator.share) {
    navigator.share({
      title: activeStep.value?.title || '专属祝福',
      text: activeStep.value?.body || '',
      url: window.location.href,
    }).catch(() => {})
    return
  }

  navigator.clipboard.writeText(window.location.href).then(() => {
    showToast('链接已复制，可以直接分享')
  }).catch(() => {
    showToast('分享失败，请手动复制链接')
  })
}

function goBack() {
  store.clearUser()
  router.push('/login')
}

function showToast(msg: string) {
  const el = document.createElement('div')
  el.className = 'toast'
  el.textContent = msg
  document.body.appendChild(el)
  setTimeout(() => el.remove(), 2200)
}
</script>

<template>
  <div class="show-page" :style="effectVars">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>正在铺开祝福页面...</p>
    </div>

    <template v-else>
      <div class="ambient-field">
        <div v-if="hasEffect('mist-glow')" class="mist-layer">
          <span class="mist mist-a"></span>
          <span class="mist mist-b"></span>
          <span class="mist mist-c"></span>
        </div>

        <div v-if="hasEffect('light-particles') || hasEffect('stardust') || hasEffect('festival-bokeh')" class="particle-layer">
          <span
            v-for="index in particleCount"
            :key="index"
            class="particle"
            :class="{
              star: hasEffect('stardust'),
              bokeh: hasEffect('festival-bokeh'),
              pearl: hasEffect('light-particles') && !hasEffect('stardust') && !hasEffect('festival-bokeh'),
            }"
            :style="{
              left: `${(index * 100) / particleCount}%`,
              animationDelay: `${index * 0.22}s`,
              animationDuration: `${5.8 - (effectProfile.motion_level || 0.55) * 2 + (index % 4) * 0.35}s`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('silk-flow')" class="silk-layer">
          <span class="silk silk-one"></span>
          <span class="silk silk-two"></span>
          <span class="silk silk-three"></span>
        </div>

        <div v-if="hasEffect('letter-unfold')" class="letter-stage">
          <div class="letter-back"></div>
          <div class="letter-front"></div>
          <div class="letter-page"></div>
        </div>

        <div v-if="hasEffect('confetti-burst')" class="confetti-layer">
          <span v-for="i in 30" :key="i" class="confetti-piece" 
            :style="{
              left: `${Math.random() * 100}%`,
              background: ['#ff6b6b','#ffd93d','#6bcb77','#4d96ff','#ff6bd6','#f9c74f'][i % 6],
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${3 + Math.random() * 2}s`,
              width: `${8 + Math.random() * 8}px`,
              height: `${8 + Math.random() * 8}px`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('floating-hearts')" class="hearts-layer">
          <span v-for="i in 20" :key="i" class="heart-float"
            :style="{
              left: `${5 + (i * 4.5) % 90}%`,
              animationDelay: `${i * 0.3}s`,
              animationDuration: `${4 + Math.random() * 3}s`,
              fontSize: `${12 + Math.random() * 16}px`,
              opacity: 0.4 + Math.random() * 0.5,
            }"
          >&#10084;</span>
        </div>

        <div v-if="hasEffect('firework-flash')" class="firework-layer">
          <div v-for="i in 8" :key="i" class="firework-burst"
            :style="{
              left: `${10 + (i * 12) % 80}%`,
              top: `${5 + (i * 7) % 50}%`,
              animationDelay: `${i * 0.4}s`,
            }"
          ></div>
        </div>

        <div v-if="hasEffect('aurora-wave')" class="aurora-layer">
          <span class="aurora aurora-1"></span>
          <span class="aurora aurora-2"></span>
          <span class="aurora aurora-3"></span>
        </div>

        <div v-if="hasEffect('sparkle-trail')" class="sparkle-layer">
          <span v-for="i in 25" :key="i" class="sparkle-dot"
            :style="{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 4}s`,
              animationDuration: `${2 + Math.random() * 2}s`,
              width: `${4 + Math.random() * 6}px`,
              height: `${4 + Math.random() * 6}px`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('lantern-rise')" class="lantern-layer">
          <span v-for="i in 12" :key="i" class="lantern-float"
            :style="{
              left: `${8 + (i * 7) % 84}%`,
              animationDelay: `${i * 0.5}s`,
              animationDuration: `${6 + Math.random() * 4}s`,
            }"
          >
            <span class="lantern-body"></span>
            <span class="lantern-string"></span>
          </span>
        </div>

        <div v-if="hasEffect('snowflake-drift')" class="snow-layer">
          <span v-for="i in 40" :key="i" class="snowflake"
            :style="{
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${5 + Math.random() * 5}s`,
              fontSize: `${6 + Math.random() * 10}px`,
              opacity: 0.5 + Math.random() * 0.5,
            }"
          >&#10052;</span>
        </div>

        <div v-if="hasEffect('petal-fall')" class="petal-layer">
          <span v-for="i in 30" :key="i" class="petal-float"
            :style="{
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 4}s`,
              animationDuration: `${5 + Math.random() * 4}s`,
              width: `${10 + Math.random() * 12}px`,
              height: `${10 + Math.random() * 12}px`,
              background: `rgba(255, ${180 + Math.floor(Math.random() * 40)}, ${200 + Math.floor(Math.random() * 55)}, 0.7)`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('bubble-rise')" class="bubble-layer">
          <span v-for="i in 25" :key="i" class="bubble-float"
            :style="{
              left: `${5 + (i * 4) % 90}%`,
              animationDelay: `${i * 0.25}s`,
              animationDuration: `${4 + Math.random() * 4}s`,
              width: `${8 + Math.random() * 16}px`,
              height: `${8 + Math.random() * 16}px`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('golden-shimmer')" class="golden-layer">
          <span class="golden-shine"></span>
          <span class="golden-shine golden-shine-2"></span>
          <span class="golden-shine golden-shine-3"></span>
        </div>

        <div v-if="hasEffect('star-twinkle')" class="star-twinkle-layer">
          <span v-for="i in 30" :key="`stw-${i}`" class="star-twinkle-dot"
            :style="{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              width: `${6 + Math.random() * 8}px`,
              height: `${6 + Math.random() * 8}px`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('glass-bubble')" class="glass-bubble-layer">
          <span v-for="i in 20" :key="`gb-${i}`" class="glass-bubble-float"
            :style="{
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 4}s`,
              width: `${15 + Math.random() * 20}px`,
              height: `${15 + Math.random() * 20}px`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('butterfly-fly')" class="butterfly-layer">
          <span v-for="i in 6" :key="`bf-${i}`" class="butterfly"
            :style="{
              left: `${10 + i * 15}%`,
              animationDelay: `${i * 0.8}s`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('firefly-glow')" class="firefly-layer">
          <span v-for="i in 25" :key="`ff-${i}`" class="firefly-dot"
            :style="{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('light-beam')" class="light-beam-layer">
          <span class="beam beam-1"></span>
          <span class="beam beam-2"></span>
          <span class="beam beam-3"></span>
        </div>

        <div v-if="hasEffect('rainbow-bridge')" class="rainbow-layer">
          <span class="rainbow-arc"></span>
        </div>

        <div v-if="hasEffect('heart-smoke')" class="heart-smoke-layer">
          <span v-for="i in 15" :key="`hs-${i}`" class="heart-smoke-float"
            :style="{
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 4}s`,
              fontSize: `${20 + Math.random() * 20}px`,
            }"
          >&#10084;</span>
        </div>

        <div v-if="hasEffect('gem-rain')" class="gem-rain-layer">
          <span v-for="i in 30" :key="`gr-${i}`" class="gem-drop"
            :style="{
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              background: ['#ff6b6b','#4d96ff','#6bcb77','#ffd93d','#ff6bd6','#fff'][i % 6],
              width: `${6 + Math.random() * 6}px`,
              height: `${10 + Math.random() * 10}px`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('feather-fall')" class="feather-layer">
          <span v-for="i in 25" :key="`ft-${i}`" class="feather-float"
            :style="{
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${6 + Math.random() * 4}s`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('water-ripple')" class="water-ripple-layer">
          <span class="ripple ripple-1"></span>
          <span class="ripple ripple-2"></span>
          <span class="ripple ripple-3"></span>
        </div>

        <div v-if="hasEffect('shooting-star')" class="shooting-star-layer">
          <span v-for="i in 8" :key="`ss-${i}`" class="shooting-star"
            :style="{
              left: `${Math.random() * 60}%`,
              top: `${Math.random() * 40}%`,
              animationDelay: `${i * 1.5}s`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('pearl-string')" class="pearl-layer">
          <span v-for="i in 20" :key="`ps-${i}`" class="pearl-dot"
            :style="{
              left: `${5 + i * 4.5}%`,
              top: `${30 + Math.random() * 40}%`,
              animationDelay: `${i * 0.2}s`,
              width: `${8 + Math.random() * 6}px`,
              height: `${8 + Math.random() * 6}px`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('gold-leaf')" class="gold-leaf-layer">
          <span v-for="i in 25" :key="`gl-${i}`" class="gold-leaf-float"
            :style="{
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${5 + Math.random() * 4}s`,
              transform: `rotate(${Math.random() * 360}deg)`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('dream-violet')" class="dream-violet-layer">
          <span class="violet-wisp violet-1"></span>
          <span class="violet-wisp violet-2"></span>
          <span class="violet-wisp violet-3"></span>
        </div>

        <div v-if="hasEffect('radiance-burst')" class="radiance-layer">
          <span class="radiance-ray"></span>
          <span class="radiance-ray radiance-ray-2"></span>
          <span class="radiance-ray radiance-ray-3"></span>
        </div>

        <div v-if="hasEffect('halo-ring')" class="halo-layer">
          <span class="halo-ring"></span>
          <span class="halo-ring halo-ring-2"></span>
        </div>

        <div v-if="hasEffect('light-jump')" class="light-jump-layer">
          <span v-for="i in 20" :key="`lj-${i}`" class="light-jump-dot"
            :style="{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 2}s`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('ribbon-fly')" class="ribbon-layer">
          <span v-for="i in 12" :key="`rf-${i}`" class="ribbon-strip"
            :style="{
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              background: ['#ff6b6b','#ffd93d','#6bcb77','#4d96ff','#ff6bd6'][i % 5],
              height: `${100 + Math.random() * 200}px`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('lantern-float')" class="lantern-float-layer">
          <span v-for="i in 10" :key="`lf-${i}`" class="lantern-sway"
            :style="{
              left: `${10 + i * 9}%`,
              animationDelay: `${i * 0.5}s`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('halo-spin')" class="halo-spin-layer">
          <span class="halo-spin-ring"></span>
        </div>

        <div v-if="hasEffect('light-flow')" class="light-flow-layer">
          <span class="flow-line flow-line-1"></span>
          <span class="flow-line flow-line-2"></span>
          <span class="flow-line flow-line-3"></span>
        </div>

        <div v-if="hasEffect('star-blink')" class="star-blink-layer">
          <span v-for="i in 25" :key="`sb-${i}`" class="star-blink-dot"
            :style="{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 4}s`,
              fontSize: `${8 + Math.random() * 12}px`,
            }"
          >&#9733;</span>
        </div>

        <div v-if="hasEffect('halo-pulse')" class="halo-pulse-layer">
          <span class="halo-pulse-ring"></span>
          <span class="halo-pulse-ring halo-pulse-ring-2"></span>
          <span class="halo-pulse-ring halo-pulse-ring-3"></span>
        </div>

        <div v-if="hasEffect('confetti-celebrate')" class="confetti-celebrate-layer">
          <span v-for="i in 40" :key="`cc-${i}`" class="confetti-pop"
            :style="{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              background: ['#ff6b6b','#ffd93d','#6bcb77','#4d96ff','#ff6bd6','#f9c74f'][i % 6],
              width: `${8 + Math.random() * 8}px`,
              height: `${8 + Math.random() * 8}px`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('gem-flash')" class="gem-flash-layer">
          <span v-for="i in 20" :key="`gf-${i}`" class="gem-flash-dot"
            :style="{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 2}s`,
              background: ['#ffd700','#ff6b6b','#4d96ff','#ff6bd6','#6bcb77'][i % 5],
              width: `${6 + Math.random() * 10}px`,
              height: `${6 + Math.random() * 10}px`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('phoenix-spread')" class="phoenix-layer">
          <span class="phoenix-wing phoenix-wing-1"></span>
          <span class="phoenix-wing phoenix-wing-2"></span>
        </div>

        <div v-if="hasEffect('flame-text')" class="flame-text-layer">
          <span class="flame-warp"></span>
        </div>

        <div v-if="hasEffect('golden-glow')" class="golden-glow-layer">
          <span class="golden-glow-shine"></span>
          <span class="golden-glow-shine golden-glow-shine-2"></span>
          <span class="golden-glow-shine golden-glow-shine-3"></span>
        </div>

        <div v-if="hasEffect('ink-spread')" class="ink-spread-layer">
          <span class="ink-spot ink-spot-1"></span>
          <span class="ink-spot ink-spot-2"></span>
          <span class="ink-spot ink-spot-3"></span>
        </div>

        <div v-if="hasEffect('cloud-float')" class="cloud-float-layer">
          <span class="cloud cloud-1"></span>
          <span class="cloud cloud-2"></span>
          <span class="cloud cloud-3"></span>
        </div>

        <div v-if="hasEffect('candle-flicker')" class="candle-layer">
          <span class="candle-flame"></span>
          <span class="candle-flame candle-flame-2"></span>
        </div>

        <div v-if="hasEffect('moon-glow')" class="moon-glow-layer">
          <span class="moon-sphere"></span>
          <span class="moon-rays"></span>
        </div>

        <div v-if="hasEffect('silk-drift')" class="silk-drift-layer">
          <span class="silk-drift silk-drift-1"></span>
          <span class="silk-drift silk-drift-2"></span>
        </div>

        <div v-if="hasEffect('paper-crane')" class="paper-crane-layer">
          <span v-for="i in 5" :key="i" class="paper-crane-fly"
            :style="{
              left: `${15 + i * 15}%`,
              animationDelay: `${i * 1.2}s`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('ribbon-knot')" class="ribbon-knot-layer">
          <span class="ribbon-circle"></span>
          <span class="ribbon-ends"></span>
        </div>

        <div v-if="hasEffect('lotus-bloom')" class="lotus-layer">
          <span class="lotus-flower lotus-flower-1"></span>
          <span class="lotus-flower lotus-flower-2"></span>
        </div>

        <div v-if="hasEffect('cloud-mist')" class="cloud-mist-layer">
          <span class="mist-wisp mist-wisp-1"></span>
          <span class="mist-wisp mist-wisp-2"></span>
          <span class="mist-wisp mist-wisp-3"></span>
        </div>

        <div v-if="hasEffect('star-wish')" class="star-wish-layer">
          <span v-for="i in 6" :key="i" class="wish-star"
            :style="{
              left: `${Math.random() * 80}%`,
              top: `${Math.random() * 60}%`,
              animationDelay: `${i * 2}s`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('stardust')" class="stardust-layer">
          <span v-for="i in 30" :key="i" class="dust-particle"
            :style="{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
            }"
          ></span>
        </div>

        <div v-if="hasEffect('afterglow')" class="afterglow-layer">
          <span class="glow-warm"></span>
          <span class="glow-warm glow-warm-2"></span>
        </div>
      </div>

      <section class="progress-shell">
        <div class="progress-copy">
          <p class="progress-kicker">Blessing Story</p>
          <h1>{{ store.globalMode === 'festival' ? (store.currentFestival || '节日祝福') : '生日祝福' }}</h1>
        </div>
        <div class="progress-track">
          <span v-for="(_, index) in steps" :key="index" :class="{ active: index <= currentStep }"></span>
        </div>
      </section>

      <transition name="step-fade" mode="out-in">
        <section
          :key="currentStep"
          id="blessing-card"
          class="blessing-card"
          :class="{
            visible: stepVisible,
            highlight: hasEffect('card-highlight'),
            'step-welcome': currentStep === 0,
            'step-intro': currentStep === 1,
            'step-main': currentStep === 2,
            'step-closing': currentStep === 3,
          }"
        >
          <div class="card-hero-effects">
            <div v-if="hasEffect('mist-glow')" class="card-mist-layer">
              <span class="card-mist card-mist-a"></span>
              <span class="card-mist card-mist-b"></span>
            </div>

            <div v-if="hasEffect('light-particles') || hasEffect('stardust') || hasEffect('festival-bokeh')" class="card-particle-layer">
              <span
                v-for="index in Math.max(6, Math.round(particleCount * 0.55))"
                :key="`card-${index}`"
                class="card-particle"
                :class="{
                  star: hasEffect('stardust'),
                  bokeh: hasEffect('festival-bokeh'),
                  pearl: hasEffect('light-particles') && !hasEffect('stardust') && !hasEffect('festival-bokeh'),
                }"
                :style="{
                  left: `${8 + (index * 82) / Math.max(6, Math.round(particleCount * 0.55))}%`,
                  top: `${8 + (index % 4) * 10}%`,
                  animationDelay: `${index * 0.18}s`,
                  animationDuration: `${3.4 - (effectProfile.motion_level || 0.55) * 0.9 + (index % 3) * 0.18}s`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('silk-flow')" class="card-silk-layer">
              <span class="card-silk card-silk-one"></span>
              <span class="card-silk card-silk-two"></span>
            </div>

            <div v-if="hasEffect('letter-unfold')" class="card-letter-stage">
              <div class="card-letter-back"></div>
              <div class="card-letter-front"></div>
              <div class="card-letter-page"></div>
            </div>

            <div v-if="hasEffect('festival-bokeh')" class="hero-bokeh-cluster">
              <span></span>
              <span></span>
              <span></span>
            </div>

            <div v-if="hasEffect('stardust')" class="hero-star-cluster">
              <span></span>
              <span></span>
              <span></span>
            </div>

            <div v-if="hasEffect('confetti-burst')" class="card-confetti-layer">
              <span v-for="i in 20" :key="`cc-${i}`" class="card-confetti"
                :style="{
                  left: `${Math.random() * 100}%`,
                  background: ['#ff6b6b','#ffd93d','#6bcb77','#4d96ff','#ff6bd6','#f9c74f'][i % 6],
                  animationDelay: `${Math.random() * 2}s`,
                  width: `${6 + Math.random() * 6}px`,
                  height: `${6 + Math.random() * 6}px`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('floating-hearts')" class="card-hearts-layer">
              <span v-for="i in 12" :key="`ch-${i}`" class="card-heart"
                :style="{
                  left: `${10 + (i * 8) % 80}%`,
                  animationDelay: `${i * 0.3}s`,
                  fontSize: `${10 + Math.random() * 12}px`,
                }"
              >&#10084;</span>
            </div>

            <div v-if="hasEffect('firework-flash')" class="card-firework-layer">
              <span v-for="i in 5" :key="`cf-${i}`" class="card-firework"
                :style="{
                  left: `${15 + (i * 18) % 70}%`,
                  top: `${10 + (i * 12) % 40}%`,
                  animationDelay: `${i * 0.5}s`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('aurora-wave')" class="card-aurora-layer">
              <span class="card-aurora card-aurora-1"></span>
              <span class="card-aurora card-aurora-2"></span>
            </div>

            <div v-if="hasEffect('sparkle-trail')" class="card-sparkle-layer">
              <span v-for="i in 15" :key="`cs-${i}`" class="card-sparkle"
                :style="{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 3}s`,
                  width: `${3 + Math.random() * 5}px`,
                  height: `${3 + Math.random() * 5}px`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('lantern-rise')" class="card-lantern-layer">
              <span v-for="i in 6" :key="`cl-${i}`" class="card-lantern"
                :style="{
                  left: `${15 + (i * 14) % 70}%`,
                  animationDelay: `${i * 0.6}s`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('snowflake-drift')" class="card-snow-layer">
              <span v-for="i in 20" :key="`csn-${i}`" class="card-snowflake"
                :style="{
                  left: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 3}s`,
                  fontSize: `${5 + Math.random() * 8}px`,
                }"
              >&#10052;</span>
            </div>

            <div v-if="hasEffect('petal-fall')" class="card-petal-layer">
              <span v-for="i in 18" :key="`cp-${i}`" class="card-petal"
                :style="{
                  left: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 3}s`,
                  width: `${8 + Math.random() * 10}px`,
                  height: `${8 + Math.random() * 10}px`,
                  background: `rgba(255, ${180 + Math.floor(Math.random() * 40)}, ${200 + Math.floor(Math.random() * 55)}, 0.7)`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('bubble-rise')" class="card-bubble-layer">
              <span v-for="i in 15" :key="`cb-${i}`" class="card-bubble"
                :style="{
                  left: `${8 + (i * 6) % 84}%`,
                  animationDelay: `${i * 0.3}s`,
                  width: `${6 + Math.random() * 12}px`,
                  height: `${6 + Math.random() * 12}px`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('golden-shimmer')" class="card-golden-layer">
              <span class="card-golden-shine"></span>
              <span class="card-golden-shine card-golden-shine-2"></span>
            </div>

            <div v-if="hasEffect('star-twinkle')" class="card-star-twinkle-layer">
              <span v-for="i in 15" :key="`cstw-${i}`" class="card-star-twinkle"
                :style="{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 3}s`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('glass-bubble')" class="card-glass-bubble-layer">
              <span v-for="i in 12" :key="`cgb-${i}`" class="card-glass-bubble"
                :style="{
                  left: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 3}s`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('butterfly-fly')" class="card-butterfly-layer">
              <span v-for="i in 4" :key="`cbf-${i}`" class="card-butterfly"
                :style="{
                  left: `${15 + i * 20}%`,
                  animationDelay: `${i * 0.8}s`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('firefly-glow')" class="card-firefly-layer">
              <span v-for="i in 15" :key="`cff-${i}`" class="card-firefly-dot"
                :style="{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 4}s`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('light-beam')" class="card-light-beam-layer">
              <span class="card-beam card-beam-1"></span>
              <span class="card-beam card-beam-2"></span>
            </div>

            <div v-if="hasEffect('rainbow-bridge')" class="card-rainbow-layer">
              <span class="card-rainbow-arc"></span>
            </div>

            <div v-if="hasEffect('heart-smoke')" class="card-heart-smoke-layer">
              <span v-for="i in 8" :key="`chsm-${i}`" class="card-heart-smoke"
                :style="{
                  left: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 3}s`,
                }"
              >&#10084;</span>
            </div>

            <div v-if="hasEffect('gem-rain')" class="card-gem-rain-layer">
              <span v-for="i in 15" :key="`cgr-${i}`" class="card-gem-drop"
                :style="{
                  left: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 2}s`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('feather-fall')" class="card-feather-layer">
              <span v-for="i in 12" :key="`cft-${i}`" class="card-feather"
                :style="{
                  left: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 4}s`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('water-ripple')" class="card-water-ripple-layer">
              <span class="card-ripple card-ripple-1"></span>
              <span class="card-ripple card-ripple-2"></span>
            </div>

            <div v-if="hasEffect('shooting-star')" class="card-shooting-star-layer">
              <span v-for="i in 5" :key="`css-${i}`" class="card-shooting-star"
                :style="{
                  left: `${Math.random() * 60}%`,
                  top: `${Math.random() * 40}%`,
                  animationDelay: `${i * 1.5}s`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('pearl-string')" class="card-pearl-layer">
              <span v-for="i in 12" :key="`cps-${i}`" class="card-pearl-dot"
                :style="{
                  left: `${5 + i * 8}%`,
                  animationDelay: `${i * 0.3}s`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('gold-leaf')" class="card-gold-leaf-layer">
              <span v-for="i in 12" :key="`cgl-${i}`" class="card-gold-leaf"
                :style="{
                  left: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 4}s`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('dream-violet')" class="card-dream-violet-layer">
              <span class="card-violet card-violet-1"></span>
              <span class="card-violet card-violet-2"></span>
            </div>

            <div v-if="hasEffect('radiance-burst')" class="card-radiance-layer">
              <span class="card-radiance-ray"></span>
              <span class="card-radiance-ray card-radiance-ray-2"></span>
            </div>

            <div v-if="hasEffect('halo-ring')" class="card-halo-layer">
              <span class="card-halo-ring"></span>
            </div>

            <div v-if="hasEffect('light-jump')" class="card-light-jump-layer">
              <span v-for="i in 12" :key="`clj-${i}`" class="card-light-jump"
                :style="{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 2}s`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('ribbon-fly')" class="card-ribbon-layer">
              <span v-for="i in 8" :key="`crf-${i}`" class="card-ribbon"
                :style="{
                  left: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 2}s`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('lantern-float')" class="card-lantern-float-layer">
              <span v-for="i in 5" :key="`clf-${i}`" class="card-lantern-sway"
                :style="{
                  left: `${15 + i * 18}%`,
                  animationDelay: `${i * 0.6}s`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('halo-spin')" class="card-halo-spin-layer">
              <span class="card-halo-spin-ring"></span>
            </div>

            <div v-if="hasEffect('light-flow')" class="card-light-flow-layer">
              <span class="card-flow-line card-flow-line-1"></span>
              <span class="card-flow-line card-flow-line-2"></span>
            </div>

            <div v-if="hasEffect('star-blink')" class="card-star-blink-layer">
              <span v-for="i in 15" :key="`csb-${i}`" class="card-star-blink"
                :style="{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 3}s`,
                }"
              >&#9733;</span>
            </div>

            <div v-if="hasEffect('halo-pulse')" class="card-halo-pulse-layer">
              <span class="card-halo-pulse-ring"></span>
              <span class="card-halo-pulse-ring card-halo-pulse-ring-2"></span>
            </div>

            <div v-if="hasEffect('confetti-celebrate')" class="card-confetti-celebrate-layer">
              <span v-for="i in 20" :key="`ccc-${i}`" class="card-confetti-pop"
                :style="{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 2}s`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('gem-flash')" class="card-gem-flash-layer">
              <span v-for="i in 12" :key="`cgf-${i}`" class="card-gem-flash"
                :style="{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 1.5}s`,
                }"
              ></span>
            </div>

            <div v-if="hasEffect('phoenix-spread')" class="card-phoenix-layer">
              <span class="card-phoenix-wing card-phoenix-wing-1"></span>
              <span class="card-phoenix-wing card-phoenix-wing-2"></span>
            </div>

            <div v-if="hasEffect('flame-text')" class="card-flame-text-layer">
              <span class="card-flame-warp"></span>
            </div>

            <div v-if="hasEffect('golden-glow')" class="card-golden-glow-layer">
              <span class="card-golden-glow-shine"></span>
              <span class="card-golden-glow-shine card-golden-glow-shine-2"></span>
            </div>
          </div>

          <div class="card-motion" v-if="hasEffect('card-highlight')"></div>
          <div class="card-glow" v-if="hasEffect('afterglow')"></div>

          <div class="card-topline">
            <p class="step-label">{{ activeStep.step_name || '祝福页面' }}</p>
            <p class="step-index">0{{ currentStep + 1 }}</p>
          </div>

          <div class="ornament-line"></div>

          <div class="title-shell">
            <h2 class="blessing-title">{{ activeStep.title }}</h2>
          </div>
          <p class="blessing-content">{{ activeStep.body }}</p>

          <div v-if="hasEffect('festival-bokeh')" class="bokeh-ring"></div>
          <div v-if="hasEffect('stardust')" class="star-flare"></div>

          <div class="signature" v-if="isLastStep">
            <span class="signature-line"></span>
            <p :class="{ handwriting: hasEffect('signature-draw') }">{{ store.username }}</p>
          </div>

          <div v-if="hasEffect('seal-fade')" class="seal-mark">祝福</div>
        </section>
      </transition>

      <div class="step-actions">
        <button class="ghost-btn" :disabled="currentStep === 0" @click="prevStep">上一步</button>
        <button v-if="!isLastStep" class="primary-btn" @click="nextStep">下一步</button>
      </div>

      <div v-if="isLastStep" class="action-bar">
        <button class="action-btn" @click="saveImage">保存图片</button>
        <button class="action-btn" @click="shareBlessing">分享链接</button>
        <button class="action-btn" @click="goBack">返回登录</button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.show-page {
  min-height: 100vh;
  padding: 22px 18px 30px;
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at 18% 12%, color-mix(in srgb, var(--theme-button) 18%, transparent), transparent 22%),
    radial-gradient(circle at 82% 10%, color-mix(in srgb, var(--theme-title) 16%, transparent), transparent 24%),
    linear-gradient(180deg, color-mix(in srgb, var(--theme-bg) 78%, white) 0%, var(--theme-bg) 100%);
  color: var(--theme-body);
}

.loading-state {
  min-height: calc(100vh - 44px);
  display: grid;
  place-items: center;
  gap: 14px;
  text-align: center;
}

.spinner {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 3px solid rgba(0, 0, 0, 0.08);
  border-top-color: var(--theme-button);
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.ambient-field {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.mist-layer,
.particle-layer,
.silk-layer,
.letter-stage,
.confetti-layer,
.hearts-layer,
.firework-layer,
.aurora-layer,
.sparkle-layer,
.lantern-layer,
.snow-layer,
.petal-layer,
.bubble-layer,
.golden-layer {
  position: absolute;
  inset: 0;
}

.mist {
  position: absolute;
  border-radius: 50%;
  filter: blur(14px);
  animation: mistDrift calc(7s - var(--motion-level) * 2.4s) ease-in-out infinite;
}

.mist-a {
  width: 200px;
  height: 200px;
  left: -20px;
  top: 120px;
  background: color-mix(in srgb, var(--theme-title) 22%, white);
  opacity: calc(0.26 + var(--glow-intensity) * 0.12);
}

.mist-b {
  width: 240px;
  height: 240px;
  right: -30px;
  top: 250px;
  background: color-mix(in srgb, var(--theme-button) 26%, white);
  opacity: calc(0.22 + var(--glow-intensity) * 0.1);
  animation-delay: 1.2s;
}

.mist-c {
  width: 160px;
  height: 160px;
  left: 34%;
  top: 56%;
  background: rgba(255, 255, 255, 0.28);
  opacity: 0.24;
  animation-delay: 0.7s;
}

.particle {
  position: absolute;
  bottom: -32px;
  animation: particleRise linear infinite;
}

.particle.pearl {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 0 18px rgba(255, 255, 255, 0.42);
}

.particle.star {
  width: 12px;
  height: 12px;
  background: radial-gradient(circle, rgba(255,255,255,1) 0%, rgba(255,230,170,0.75) 45%, transparent 72%);
}

.particle.bokeh {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: radial-gradient(circle, color-mix(in srgb, var(--theme-button) 42%, white) 0%, transparent 72%);
}

.silk {
  position: absolute;
  left: -15%;
  width: 130%;
  border-radius: 999px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.56), transparent);
  filter: blur(2px);
  animation: silkFlow calc(7s - var(--motion-level) * 2s) ease-in-out infinite;
}

.silk-one {
  top: 18%;
  height: 88px;
  transform: rotate(-10deg);
}

.silk-two {
  top: 42%;
  height: 110px;
  transform: rotate(6deg);
  animation-delay: 1s;
}

.silk-three {
  top: 66%;
  height: 92px;
  transform: rotate(-4deg);
  animation-delay: 2s;
}

.letter-stage {
  top: 18%;
  left: 50%;
  width: 230px;
  height: 170px;
  transform: translateX(-50%);
}

.letter-back,
.letter-front,
.letter-page {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  border-radius: 16px;
}

.letter-back {
  bottom: 0;
  width: 220px;
  height: 130px;
  background: rgba(255, 255, 255, 0.34);
  box-shadow: 0 12px 24px rgba(72, 52, 37, 0.08);
}

.letter-page {
  bottom: 24px;
  width: 180px;
  height: 110px;
  background: rgba(255, 255, 255, 0.62);
  animation: pageLift calc(4.4s - var(--motion-level) * 1.4s) ease-in-out infinite;
}

.letter-front {
  bottom: 0;
  width: 220px;
  height: 130px;
  background: linear-gradient(180deg, rgba(255,255,255,0.1), rgba(255,255,255,0.34));
  clip-path: polygon(0 0, 100% 0, 50% 58%);
  animation: flapOpen calc(4.4s - var(--motion-level) * 1.4s) ease-in-out infinite;
}

.progress-shell,
.blessing-card {
  position: relative;
  z-index: 2;
}

.progress-shell {
  margin-bottom: 18px;
}

.progress-kicker,
.step-label,
.step-index {
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.progress-kicker,
.step-index {
  color: color-mix(in srgb, var(--theme-body) 54%, white);
}

.progress-copy h1 {
  color: var(--theme-title);
  font-size: 1.15rem;
  font-weight: 900;
  margin-top: 4px;
}

.progress-track {
  margin-top: 14px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.progress-track span {
  height: 5px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.42);
}

.progress-track span.active {
  background: var(--theme-title);
}

.blessing-card {
  min-height: 500px;
  border-radius: 28px;
  background: linear-gradient(180deg, color-mix(in srgb, var(--theme-card) 90%, white) 0%, var(--theme-card) 100%);
  box-shadow: 0 24px 60px rgba(60, 46, 34, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.46);
  padding: 28px 24px;
  opacity: 0;
  transform: translateY(18px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;
}

.blessing-card.step-welcome.visible {
  animation: cardWelcomeBreath 4s ease-in-out 0.3s infinite;
}

.blessing-card.step-intro.visible {
  animation: cardIntroGlow 3s ease-in-out 0.3s infinite;
}

.blessing-card.step-main.visible {
  animation: cardMainPulse 2s ease-in-out 0.3s infinite;
}

.blessing-card.step-closing.visible {
  animation: cardClosingFade 5s ease-in-out 0.3s infinite;
}

@keyframes cardWelcomeBreath {
  0% {
    transform: scale(1);
    box-shadow: 0 24px 60px rgba(60, 46, 34, 0.14);
  }
  50% {
    transform: scale(1.02);
    box-shadow: 0 28px 70px rgba(60, 46, 34, 0.2);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 24px 60px rgba(60, 46, 34, 0.14);
  }
}

@keyframes cardIntroGlow {
  0% {
    box-shadow: 0 24px 60px rgba(60, 46, 34, 0.14), 0 0 0 rgba(255, 182, 193, 0);
  }
  50% {
    box-shadow: 0 24px 60px rgba(60, 46, 34, 0.14), 0 0 30px rgba(255, 182, 193, 0.3);
  }
  100% {
    box-shadow: 0 24px 60px rgba(60, 46, 34, 0.14), 0 0 0 rgba(255, 182, 193, 0);
  }
}

@keyframes cardMainPulse {
  0% {
    transform: scale(1);
    box-shadow: 0 24px 60px rgba(60, 46, 34, 0.14);
  }
  25% {
    transform: scale(1.01);
    box-shadow: 0 26px 65px rgba(60, 46, 34, 0.16);
  }
  50% {
    transform: scale(1.03);
    box-shadow: 0 28px 70px rgba(60, 46, 34, 0.18);
  }
  75% {
    transform: scale(1.01);
    box-shadow: 0 26px 65px rgba(60, 46, 34, 0.16);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 24px 60px rgba(60, 46, 34, 0.14);
  }
}

@keyframes cardClosingFade {
  0% {
    opacity: 1;
    box-shadow: 0 24px 60px rgba(60, 46, 34, 0.14);
  }
  50% {
    opacity: 0.9;
    box-shadow: 0 20px 50px rgba(60, 46, 34, 0.1);
  }
  100% {
    opacity: 1;
    box-shadow: 0 24px 60px rgba(60, 46, 34, 0.14);
  }
}

.card-hero-effects {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 2000000;
}

.card-mist-layer,
.card-particle-layer,
.card-silk-layer,
.card-letter-stage,
.hero-bokeh-cluster,
.hero-star-cluster {
  position: absolute;
  inset: 0;
}

.card-mist {
  position: absolute;
  border-radius: 50%;
  filter: blur(12px);
  animation: mistDrift calc(5.2s - var(--motion-level) * 1.5s) ease-in-out infinite;
}

.card-mist-a {
  width: 140px;
  height: 140px;
  left: 8%;
  top: 8%;
  background: color-mix(in srgb, var(--theme-title) 24%, white);
  opacity: 0.34;
}

.card-mist-b {
  width: 160px;
  height: 160px;
  right: 8%;
  top: 2%;
  background: color-mix(in srgb, var(--theme-button) 26%, white);
  opacity: 0.3;
  animation-delay: 1s;
}

.card-particle {
  position: absolute;
  animation: heroFloat linear infinite;
}

.card-particle.pearl {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 0 22px rgba(255, 255, 255, 0.55);
}

.card-particle.star {
  width: 14px;
  height: 14px;
  background: radial-gradient(circle, rgba(255,255,255,1) 0%, rgba(255,227,173,0.85) 44%, transparent 72%);
}

.card-particle.bokeh {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: radial-gradient(circle, color-mix(in srgb, var(--theme-button) 56%, white) 0%, transparent 74%);
}

.card-silk {
  position: absolute;
  left: -8%;
  width: 116%;
  border-radius: 999px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.76), transparent);
  filter: blur(1px);
  animation: silkFlow calc(4.8s - var(--motion-level) * 1.2s) ease-in-out infinite;
}

.card-silk-one {
  top: 18%;
  height: 60px;
  transform: rotate(-8deg);
}

.card-silk-two {
  top: 34%;
  height: 76px;
  transform: rotate(6deg);
  animation-delay: 0.8s;
}

.card-letter-stage {
  left: 50%;
  top: 6%;
  width: 170px;
  height: 120px;
  transform: translateX(-50%);
}

.card-letter-back,
.card-letter-front,
.card-letter-page {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  border-radius: 14px;
}

.card-letter-back {
  bottom: 0;
  width: 164px;
  height: 92px;
  background: rgba(255, 255, 255, 0.44);
}

.card-letter-page {
  bottom: 16px;
  width: 126px;
  height: 84px;
  background: rgba(255, 255, 255, 0.78);
  animation: pageLift calc(3.6s - var(--motion-level) * 1s) ease-in-out infinite;
}

.card-letter-front {
  bottom: 0;
  width: 164px;
  height: 92px;
  background: linear-gradient(180deg, rgba(255,255,255,0.14), rgba(255,255,255,0.48));
  clip-path: polygon(0 0, 100% 0, 50% 60%);
  animation: flapOpen calc(3.6s - var(--motion-level) * 1s) ease-in-out infinite;
}

.hero-bokeh-cluster span,
.hero-star-cluster span {
  position: absolute;
  border-radius: 50%;
}

.hero-bokeh-cluster span:nth-child(1) {
  width: 56px;
  height: 56px;
  right: 14%;
  top: 10%;
  background: radial-gradient(circle, color-mix(in srgb, var(--theme-button) 52%, white) 0%, transparent 72%);
  animation: clusterPulse 2.8s ease-in-out infinite;
}

.hero-bokeh-cluster span:nth-child(2) {
  width: 30px;
  height: 30px;
  right: 28%;
  top: 18%;
  background: radial-gradient(circle, rgba(255,255,255,0.95) 0%, transparent 72%);
  animation: clusterPulse 2.4s ease-in-out infinite 0.4s;
}

.hero-bokeh-cluster span:nth-child(3) {
  width: 18px;
  height: 18px;
  right: 10%;
  top: 26%;
  background: radial-gradient(circle, rgba(255,255,255,0.88) 0%, transparent 72%);
  animation: clusterPulse 2.2s ease-in-out infinite 0.7s;
}

.hero-star-cluster span:nth-child(1) {
  width: 34px;
  height: 34px;
  left: 10%;
  top: 14%;
  background: radial-gradient(circle, rgba(255,255,255,1) 0%, rgba(255,231,183,0.84) 46%, transparent 72%);
  animation: flareTwinkle 2.4s ease-in-out infinite;
}

.hero-star-cluster span:nth-child(2) {
  width: 18px;
  height: 18px;
  left: 20%;
  top: 7%;
  background: radial-gradient(circle, rgba(255,255,255,0.96) 0%, rgba(255,231,183,0.72) 46%, transparent 72%);
  animation: flareTwinkle 2.1s ease-in-out infinite 0.4s;
}

.hero-star-cluster span:nth-child(3) {
  width: 12px;
  height: 12px;
  left: 28%;
  top: 20%;
  background: radial-gradient(circle, rgba(255,255,255,0.92) 0%, rgba(255,231,183,0.66) 46%, transparent 72%);
  animation: flareTwinkle 2.8s ease-in-out infinite 0.7s;
}

.blessing-card.visible {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 0.42s ease, transform 0.42s ease;
}

.card-motion,
.card-glow,
.bokeh-ring,
.star-flare {
  position: absolute;
  pointer-events: none;
}

.card-motion {
  inset: -35%;
  background: linear-gradient(120deg, transparent 30%, rgba(255,255,255,calc(0.16 + var(--glow-intensity) * 0.2)) 48%, transparent 64%);
  transform: rotate(10deg);
  animation: cardSweep calc(4.6s - var(--motion-level) * 1.6s) linear infinite;
}

.card-glow {
  inset: auto 12% 14% 12%;
  height: 88px;
  border-radius: 50%;
  background: radial-gradient(circle, color-mix(in srgb, var(--theme-button) 26%, white) 0%, transparent 70%);
  filter: blur(14px);
  animation: cardPulse calc(3.8s - var(--motion-level) * 1.2s) ease-in-out infinite;
}

.card-topline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
  position: relative;
  z-index: 2;
}

.step-label {
  color: color-mix(in srgb, var(--theme-body) 60%, white);
}

.ornament-line {
  width: 84px;
  height: 4px;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--theme-title), var(--theme-button));
  margin-bottom: 22px;
  position: relative;
  z-index: 2;
}

.title-shell {
  overflow: hidden;
  position: relative;
  z-index: 2;
}

.blessing-title {
  color: var(--theme-title);
  font-size: clamp(2rem, 8vw, 2.65rem);
  line-height: 1.18;
  font-weight: 900;
  margin-bottom: 18px;
  animation: titleLift 0.55s ease-out;
}

.blessing-content {
  color: var(--theme-body);
  font-size: clamp(1rem, 4.1vw, 1.18rem);
  line-height: 2;
  white-space: pre-wrap;
  word-break: break-word;
  position: relative;
  z-index: 2;
  animation: contentFade 0.8s ease-out;
}

.bokeh-ring {
  right: -24px;
  top: 22%;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  border: 20px solid rgba(255, 255, 255, 0.14);
  animation: ringFloat calc(6s - var(--motion-level) * 1.8s) ease-in-out infinite;
}

.star-flare {
  left: 18px;
  top: 16px;
  width: 72px;
  height: 72px;
  background: radial-gradient(circle, rgba(255,255,255,0.96) 0%, rgba(255,229,170,0.74) 42%, transparent 72%);
  filter: blur(1px);
  animation: flareTwinkle calc(2.8s - var(--motion-level) * 0.8s) ease-in-out infinite;
}

.signature {
  margin-top: 34px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
  position: relative;
  z-index: 2;
}

.signature-line {
  width: 100px;
  height: 1px;
  background: color-mix(in srgb, var(--theme-title) 50%, transparent);
}

.signature p {
  color: var(--theme-title);
  font-size: 1rem;
  font-weight: 800;
}

.signature p.handwriting {
  font-family: "Segoe Script", "KaiTi", cursive;
  overflow: hidden;
  white-space: nowrap;
  border-right: 2px solid color-mix(in srgb, var(--theme-title) 70%, transparent);
  animation: writeName 2.2s steps(24, end) forwards;
  max-width: 0;
}

.seal-mark {
  position: absolute;
  right: 22px;
  bottom: 22px;
  width: 82px;
  height: 82px;
  border-radius: 50%;
  border: 2px solid rgba(180, 44, 44, 0.42);
  color: rgba(180, 44, 44, 0.58);
  display: grid;
  place-items: center;
  font-weight: 900;
  transform: rotate(-12deg);
  animation: stampDrop 3.2s ease-in-out infinite;
}

.step-fade-enter-active,
.step-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.step-fade-enter-from,
.step-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

.step-actions,
.action-bar {
  position: relative;
  z-index: 2;
  display: grid;
  gap: 10px;
  margin-top: 18px;
}

.step-actions {
  grid-template-columns: 1fr 1fr;
}

.ghost-btn,
.primary-btn,
.action-btn {
  min-height: 48px;
  border-radius: 16px;
  font-weight: 800;
}

.ghost-btn {
  border: 1px solid color-mix(in srgb, var(--theme-body) 26%, transparent);
  background: rgba(255, 255, 255, 0.5);
  color: var(--theme-body);
}

.ghost-btn:disabled {
  opacity: 0.35;
}

.primary-btn {
  border: 0;
  background: linear-gradient(135deg, var(--theme-button), color-mix(in srgb, var(--theme-button) 65%, white));
  color: #fff;
  box-shadow: 0 16px 28px color-mix(in srgb, var(--theme-button) 28%, transparent);
}

.action-bar {
  grid-template-columns: repeat(3, 1fr);
}

.action-btn {
  border: 1px solid color-mix(in srgb, var(--theme-body) 16%, transparent);
  background: rgba(255, 255, 255, 0.62);
  color: var(--theme-body);
  font-size: 0.82rem;
}

@keyframes mistDrift {
  0%, 100% { transform: translate3d(0, 0, 0) scale(1); }
  50% { transform: translate3d(24px, -20px, 0) scale(1.12); }
}

@keyframes particleRise {
  0% { transform: translateY(0) scale(0.8); opacity: 0; }
  15% { opacity: calc(0.35 + var(--particle-density) * 0.5); }
  100% { transform: translateY(-115vh) scale(1.22); opacity: 0; }
}

@keyframes heroFloat {
  0% { transform: translateY(0) scale(0.88); opacity: 0; }
  16% { opacity: 1; }
  50% { transform: translateY(-16px) scale(1.04); opacity: 0.96; }
  100% { transform: translateY(-34px) scale(0.9); opacity: 0; }
}

@keyframes silkFlow {
  0%, 100% { transform: translateX(0) rotate(-10deg); opacity: 0.3; }
  50% { transform: translateX(6%) rotate(2deg); opacity: 0.6; }
}

@keyframes pageLift {
  0%, 100% { transform: translateX(-50%) translateY(12px); opacity: 0.45; }
  50% { transform: translateX(-50%) translateY(-6px); opacity: 0.9; }
}

@keyframes flapOpen {
  0%, 100% { transform: translateX(-50%) rotateX(0deg); opacity: 0.42; }
  50% { transform: translateX(-50%) rotateX(18deg); opacity: 0.78; }
}

@keyframes cardSweep {
  0% { transform: translateX(-46%) rotate(10deg); }
  100% { transform: translateX(46%) rotate(10deg); }
}

@keyframes cardPulse {
  0%, 100% { opacity: 0.24; transform: scaleX(0.96); }
  50% { opacity: 0.62; transform: scaleX(1.04); }
}

@keyframes titleLift {
  from { opacity: 0; transform: translateY(18px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes contentFade {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes ringFloat {
  0%, 100% { transform: translateY(0) scale(0.98); opacity: 0.24; }
  50% { transform: translateY(-12px) scale(1.04); opacity: 0.46; }
}

@keyframes flareTwinkle {
  0%, 100% { transform: scale(0.92); opacity: 0.58; }
  50% { transform: scale(1.12); opacity: 1; }
}

@keyframes clusterPulse {
  0%, 100% { transform: scale(0.92); opacity: 0.52; }
  50% { transform: scale(1.08); opacity: 0.96; }
}

@keyframes stampDrop {
  0%, 100% { transform: translateY(0) rotate(-12deg); opacity: 0.46; }
  28% { transform: translateY(8px) rotate(-9deg); opacity: 0.86; }
  55% { transform: translateY(0) rotate(-12deg); opacity: 0.58; }
}

@keyframes writeName {
  from { max-width: 0; }
  to { max-width: 180px; }
}

.confetti-piece {
  position: absolute;
  top: -20px;
  border-radius: 2px;
  animation: confettiFall linear infinite;
  transform: rotate(45deg);
}

@keyframes confettiFall {
  0% { transform: translateY(-20px) rotate(0deg); opacity: 1; }
  100% { transform: translateY(110vh) rotate(720deg); opacity: 0.3; }
}

.heart-float {
  position: absolute;
  color: rgba(255, 100, 130, 0.8);
  animation: heartFloat linear infinite;
}

@keyframes heartFloat {
  0% { transform: translateY(100vh) scale(0.8); opacity: 0; }
  10% { opacity: 0.8; }
  90% { opacity: 0.8; }
  100% { transform: translateY(-20px) scale(1.2); opacity: 0; }
}

.firework-burst {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: radial-gradient(circle, #fff 0%, #ffd700 30%, #ff6b6b 60%, transparent 80%);
  animation: fireworkExplode 1.5s ease-out infinite;
}

@keyframes fireworkExplode {
  0% { transform: scale(0); opacity: 1; box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.8); }
  50% { transform: scale(1.5); opacity: 1; box-shadow: 0 0 20px 10px rgba(255, 107, 107, 0.5); }
  100% { transform: scale(2); opacity: 0; box-shadow: 0 0 40px 20px transparent; }
}

.aurora {
  position: absolute;
  border-radius: 50%;
  filter: blur(30px);
  animation: auroraWave ease-in-out infinite;
}

.aurora-1 {
  width: 80%;
  height: 200px;
  left: 10%;
  top: 10%;
  background: linear-gradient(180deg, rgba(72, 219, 251, 0.4), rgba(180, 100, 255, 0.3), transparent);
  animation-duration: 6s;
}

.aurora-2 {
  width: 60%;
  height: 150px;
  left: 20%;
  top: 20%;
  background: linear-gradient(180deg, rgba(100, 255, 180, 0.35), rgba(72, 180, 251, 0.25), transparent);
  animation-duration: 8s;
  animation-delay: 2s;
}

.aurora-3 {
  width: 50%;
  height: 120px;
  left: 25%;
  top: 5%;
  background: linear-gradient(180deg, rgba(255, 180, 219, 0.3), rgba(255, 219, 150, 0.25), transparent);
  animation-duration: 7s;
  animation-delay: 4s;
}

@keyframes auroraWave {
  0%, 100% { transform: translateX(-10%) scaleY(1); opacity: 0.5; }
  50% { transform: translateX(10%) scaleY(1.3); opacity: 0.8; }
}

.sparkle-dot {
  position: absolute;
  background: radial-gradient(circle, #fff 0%, #ffd700 50%, transparent 70%);
  border-radius: 50%;
  animation: sparkleFlash ease-in-out infinite;
}

@keyframes sparkleFlash {
  0%, 100% { transform: scale(0.5); opacity: 0.2; }
  50% { transform: scale(1.5); opacity: 1; }
}

.lantern-float {
  position: absolute;
  bottom: -60px;
  animation: lanternRise linear infinite;
}

.lantern-body {
  display: block;
  width: 24px;
  height: 32px;
  background: radial-gradient(ellipse, #ff6b6b 0%, #c0392b 100%);
  border-radius: 50%;
  box-shadow: 0 0 15px rgba(255, 100, 100, 0.6);
}

.lantern-string {
  display: block;
  width: 1px;
  height: 12px;
  background: rgba(139, 69, 19, 0.6);
  margin: 0 auto;
}

@keyframes lanternRise {
  0% { transform: translateY(0) rotate(-5deg); opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { transform: translateY(-110vh) rotate(5deg); opacity: 0; }
}

.snowflake {
  position: absolute;
  top: -20px;
  color: rgba(255, 255, 255, 0.9);
  animation: snowFall linear infinite;
  text-shadow: 0 0 5px rgba(200, 220, 255, 0.8);
}

@keyframes snowFall {
  0% { transform: translateY(-20px) rotate(0deg); opacity: 1; }
  100% { transform: translateY(100vh) rotate(360deg); opacity: 0.3; }
}

.petal-float {
  position: absolute;
  top: -30px;
  border-radius: 50% 10px 50% 10px;
  animation: petalFall linear infinite;
}

@keyframes petalFall {
  0% { transform: translateY(-30px) rotate(0deg); opacity: 0.9; }
  100% { transform: translateY(110vh) rotate(540deg); opacity: 0.2; }
}

.bubble-float {
  position: absolute;
  bottom: -30px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.9), rgba(200, 230, 255, 0.4));
  border: 1px solid rgba(255, 255, 255, 0.6);
  animation: bubbleRise linear infinite;
}

@keyframes bubbleRise {
  0% { transform: translateY(0) translateX(0); opacity: 0; }
  10% { opacity: 0.8; }
  50% { transform: translateY(-50vh) translateX(20px); }
  90% { opacity: 0.8; }
  100% { transform: translateY(-110vh) translateX(-10px); opacity: 0; }
}

.golden-layer {
  overflow: hidden;
}

.golden-shine {
  position: absolute;
  width: 200%;
  height: 60px;
  top: 20%;
  left: -50%;
  background: linear-gradient(90deg, transparent, rgba(255, 215, 0, 0.3), rgba(255, 255, 255, 0.5), rgba(255, 215, 0, 0.3), transparent);
  animation: goldenSweep 4s ease-in-out infinite;
}

.golden-shine-2 {
  top: 45%;
  animation-delay: 1.5s;
  width: 150%;
}

.golden-shine-3 {
  top: 70%;
  animation-delay: 3s;
  width: 180%;
}

@keyframes goldenSweep {
  0% { transform: translateX(-50%) rotate(-15deg); }
  100% { transform: translateX(50%) rotate(-15deg); }
}

.card-confetti-layer,
.card-hearts-layer,
.card-firework-layer,
.card-aurora-layer,
.card-sparkle-layer,
.card-lantern-layer,
.card-snow-layer,
.card-petal-layer,
.card-bubble-layer,
.card-golden-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 210000;
  overflow: hidden;
}

.card-confetti {
  position: absolute;
  top: -20px;
  border-radius: 2px;
  animation: cardConfettiFall linear infinite;
  opacity: 0.85;
  box-shadow: 0 0 4px rgba(0,0,0,0.2);
}

@keyframes cardConfettiFall {
  0% { transform: translateY(-20px) rotate(0deg); opacity: 0.85; }
  100% { transform: translateY(50vh) rotate(540deg); opacity: 0.6; }
}

.card-heart {
  position: absolute;
  color: #ff4477;
  animation: cardHeartFloat ease-in-out infinite;
  bottom: -20px;
  text-shadow: 0 0 8px rgba(255, 68, 119, 0.6);
  filter: drop-shadow(0 0 3px rgba(255, 68, 119, 0.5));
}

@keyframes cardHeartFloat {
  0%, 100% { transform: translateY(0) scale(1); opacity: 0.9; }
  50% { transform: translateY(-30px) scale(1.15); opacity: 1; }
}

.card-firework {
  position: absolute;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: radial-gradient(circle, #fff 0%, #ffd700 30%, #ff4444 60%, transparent 80%);
  animation: cardFireworkFlash ease-out infinite;
  box-shadow: 0 0 12px rgba(255, 200, 0, 0.8), 0 0 24px rgba(255, 100, 100, 0.5);
}

@keyframes cardFireworkFlash {
  0%, 70%, 100% { transform: scale(0.3); opacity: 0.2; }
  80% { transform: scale(1.8); opacity: 1; }
}

.card-aurora {
  position: absolute;
  border-radius: 50%;
  filter: blur(20px);
  animation: cardAuroraPulse ease-in-out infinite;
}

.card-aurora-1 {
  width: 120%;
  height: 100px;
  left: -10%;
  top: 5%;
  background: linear-gradient(90deg, rgba(100, 200, 255, 0.5), rgba(180, 100, 255, 0.45), rgba(255, 100, 200, 0.4), transparent);
  animation-duration: 4s;
}

.card-aurora-2 {
  width: 100%;
  height: 80px;
  left: 0%;
  top: 15%;
  background: linear-gradient(90deg, transparent, rgba(255, 200, 100, 0.4), rgba(255, 150, 180, 0.35), transparent);
  animation-duration: 5s;
  animation-delay: 2s;
}

@keyframes cardAuroraPulse {
  0%, 100% { opacity: 0.6; transform: scaleX(0.95) translateX(-2%); }
  50% { opacity: 0.9; transform: scaleX(1.05) translateX(2%); }
}

.card-sparkle {
  position: absolute;
  background: radial-gradient(circle, #ffffff 0%, #ffd700 50%, rgba(255, 180, 100, 0.5) 70%, transparent 100%);
  border-radius: 50%;
  animation: cardSparkleFlash ease-in-out infinite;
  box-shadow: 0 0 6px rgba(255, 215, 0, 0.8);
}

@keyframes cardSparkleFlash {
  0%, 100% { transform: scale(0.4); opacity: 0.3; }
  50% { transform: scale(1.4); opacity: 1; }
}

.card-lantern {
  position: absolute;
  bottom: -30px;
  width: 20px;
  height: 28px;
  background: radial-gradient(ellipse, #ff6b6b 0%, #dc143c 100%);
  border-radius: 50%;
  box-shadow: 0 0 15px rgba(255, 100, 100, 0.7), 0 0 30px rgba(255, 50, 50, 0.4);
  animation: cardLanternFloat ease-in-out infinite;
}

@keyframes cardLanternFloat {
  0%, 100% { transform: translateY(0) rotate(-4deg); opacity: 0.9; }
  50% { transform: translateY(-30px) rotate(4deg); opacity: 1; }
}

.card-snowflake {
  position: absolute;
  top: -20px;
  color: #e8f4ff;
  animation: cardSnowFall linear infinite;
  text-shadow: 0 0 8px rgba(180, 220, 255, 1), 0 0 16px rgba(200, 230, 255, 0.8);
  filter: drop-shadow(0 0 2px rgba(255,255,255,0.8));
}

@keyframes cardSnowFall {
  0% { transform: translateY(-20px) rotate(0deg); opacity: 1; }
  100% { transform: translateY(50vh) rotate(360deg); opacity: 0.5; }
}

.card-petal {
  position: absolute;
  top: -20px;
  border-radius: 50% 10px 50% 10px;
  animation: cardPetalFall linear infinite;
  box-shadow: 0 0 4px rgba(255, 180, 200, 0.5);
}

@keyframes cardPetalFall {
  0% { transform: translateY(-20px) rotate(0deg); opacity: 0.9; }
  100% { transform: translateY(50vh) rotate(400deg); opacity: 0.4; }
}

.card-bubble {
  position: absolute;
  bottom: -20px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.95), rgba(180, 220, 255, 0.5), rgba(100, 180, 255, 0.3));
  border: 1px solid rgba(255, 255, 255, 0.8);
  animation: cardBubbleRise linear infinite;
  box-shadow: inset 0 0 8px rgba(255,255,255,0.5), 0 0 6px rgba(200, 230, 255, 0.4);
}

@keyframes cardBubbleRise {
  0% { transform: translateY(0); opacity: 0; }
  10% { opacity: 0.9; }
  90% { opacity: 0.9; }
  100% { transform: translateY(-50vh); opacity: 0; }
}

.card-golden-layer {
  overflow: hidden;
}

.card-golden-shine {
  position: absolute;
  width: 200%;
  height: 50px;
  left: -50%;
  top: 10%;
  background: linear-gradient(90deg, transparent, rgba(255, 215, 0, 0.4), rgba(255, 255, 255, 0.7), rgba(255, 215, 0, 0.4), transparent);
  animation: cardGoldenSweep 3s ease-in-out infinite;
  box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
}

.card-golden-shine-2 {
  top: 50%;
  animation-delay: 1.5s;
}

@keyframes cardGoldenSweep {
  0% { transform: translateX(-40%) rotate(-10deg); }
  100% { transform: translateX(40%) rotate(-10deg); }
}

.star-twinkle-layer,
.glass-bubble-layer,
.butterfly-layer,
.firefly-layer,
.light-beam-layer,
.rainbow-layer,
.heart-smoke-layer,
.gem-rain-layer,
.feather-layer,
.water-ripple-layer,
.shooting-star-layer,
.pearl-layer,
.gold-leaf-layer,
.dream-violet-layer,
.radiance-layer,
.halo-layer,
.light-jump-layer,
.ribbon-layer,
.lantern-float-layer,
.halo-spin-layer,
.light-flow-layer,
.star-blink-layer,
.halo-pulse-layer,
.confetti-celebrate-layer,
.gem-flash-layer,
.phoenix-layer,
.flame-text-layer,
.golden-glow-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.star-twinkle-dot {
  position: absolute;
  background: radial-gradient(circle, #fff 0%, #ffd700 40%, transparent 70%);
  border-radius: 50%;
  animation: starTwinkle 2s ease-in-out infinite;
}

@keyframes starTwinkle {
  0%, 100% { transform: scale(0.5); opacity: 0.3; }
  50% { transform: scale(1.5); opacity: 1; }
}

.glass-bubble-float {
  position: absolute;
  bottom: -40px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.9), rgba(200, 230, 255, 0.4), rgba(150, 200, 255, 0.2));
  border: 1px solid rgba(255, 255, 255, 0.8);
  animation: glassBubbleRise linear infinite;
  box-shadow: inset 0 0 15px rgba(255, 255, 255, 0.6), 0 0 10px rgba(200, 220, 255, 0.3);
}

@keyframes glassBubbleRise {
  0% { transform: translateY(0) scale(0.8); opacity: 0; }
  10% { opacity: 0.9; }
  90% { opacity: 0.9; }
  100% { transform: translateY(-110vh) scale(1.1); opacity: 0; }
}

.butterfly {
  position: absolute;
  bottom: -30px;
  width: 20px;
  height: 16px;
  background: linear-gradient(135deg, #ff6bd6 0%, #ffd93d 50%, #ff6bd6 100%);
  border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
  animation: butterflyFly 6s ease-in-out infinite;
  box-shadow: 0 0 10px rgba(255, 107, 214, 0.5);
}

@keyframes butterflyFly {
  0% { transform: translateY(0) translateX(0) rotate(-5deg); }
  25% { transform: translateY(-30vh) translateX(20px) rotate(5deg); }
  50% { transform: translateY(-50vh) translateX(-10px) rotate(-3deg); }
  75% { transform: translateY(-70vh) translateX(15px) rotate(4deg); }
  100% { transform: translateY(-100vh) translateX(0) rotate(0deg); opacity: 0; }
}

.firefly-dot {
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ffd700;
  box-shadow: 0 0 10px #ffd700, 0 0 20px rgba(255, 215, 0, 0.5);
  animation: fireflyGlow 4s ease-in-out infinite;
}

@keyframes fireflyGlow {
  0%, 100% { opacity: 0.2; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.2); }
}

.beam {
  position: absolute;
  width: 4px;
  height: 120%;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.8), rgba(255, 215, 0, 0.4), transparent);
  animation: beamSweep 5s ease-in-out infinite;
  filter: blur(2px);
}

.beam-1 { left: 20%; transform: rotate(15deg); }
.beam-2 { left: 50%; transform: rotate(0deg); animation-delay: 1.5s; }
.beam-3 { left: 80%; transform: rotate(-15deg); animation-delay: 3s; }

@keyframes beamSweep {
  0%, 100% { opacity: 0.3; height: 80%; }
  50% { opacity: 0.8; height: 120%; }
}

.rainbow-arc {
  position: absolute;
  width: 300px;
  height: 150px;
  left: 50%;
  top: 50%;
  transform: translateX(-50%);
  border-radius: 300px 300px 0 0;
  background: linear-gradient(180deg, 
    rgba(255, 0, 0, 0.4) 0%, 
    rgba(255, 165, 0, 0.4) 16%, 
    rgba(255, 255, 0, 0.4) 33%, 
    rgba(0, 128, 0, 0.4) 50%, 
    rgba(0, 0, 255, 0.4) 66%, 
    rgba(128, 0, 128, 0.4) 83%, 
    transparent 100%);
  animation: rainbowPulse 4s ease-in-out infinite;
}

@keyframes rainbowPulse {
  0%, 100% { opacity: 0.5; transform: translateX(-50%) scale(0.9); }
  50% { opacity: 0.8; transform: translateX(-50%) scale(1.1); }
}

.heart-smoke-float {
  position: absolute;
  bottom: -30px;
  color: rgba(255, 100, 150, 0.6);
  animation: heartSmokeRise 5s ease-out infinite;
  filter: blur(3px);
}

@keyframes heartSmokeRise {
  0% { transform: translateY(0) scale(0.5); opacity: 0; }
  20% { opacity: 0.6; }
  100% { transform: translateY(-100vh) scale(1.5); opacity: 0; }
}

.gem-drop {
  position: absolute;
  top: -30px;
  border-radius: 50% 10% 50% 10%;
  animation: gemFall 3s ease-in infinite;
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
}

@keyframes gemFall {
  0% { transform: translateY(-30px) rotate(0deg); opacity: 1; }
  100% { transform: translateY(100vh) rotate(360deg); opacity: 0.3; }
}

.feather-float {
  position: absolute;
  top: -20px;
  width: 12px;
  height: 20px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(200, 220, 255, 0.6));
  border-radius: 50% 50% 50% 50% / 80% 80% 20% 20%;
  animation: featherFall 7s linear infinite;
}

@keyframes featherFall {
  0% { transform: translateY(-20px) translateX(0) rotate(0deg); opacity: 0.9; }
  100% { transform: translateY(100vh) translateX(50px) rotate(360deg); opacity: 0.2; }
}

.ripple {
  position: absolute;
  border: 2px solid rgba(100, 200, 255, 0.4);
  border-radius: 50%;
  animation: waterRipple 4s ease-out infinite;
}

.ripple-1 { width: 50px; height: 50px; left: 20%; top: 30%; }
.ripple-2 { width: 80px; height: 80px; left: 50%; top: 50%; animation-delay: 1.3s; }
.ripple-3 { width: 110px; height: 110px; left: 70%; top: 60%; animation-delay: 2.6s; }

@keyframes waterRipple {
  0% { transform: scale(0); opacity: 1; }
  100% { transform: scale(3); opacity: 0; }
}

.shooting-star {
  position: absolute;
  width: 80px;
  height: 2px;
  background: linear-gradient(90deg, #fff, #ffd700, transparent);
  animation: shootingStarMove 2s linear infinite;
  border-radius: 50%;
}

@keyframes shootingStarMove {
  0% { transform: translateX(0) translateY(0); opacity: 1; }
  100% { transform: translateX(200px) translateY(150px); opacity: 0; }
}

.pearl-dot {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #fff, #e8e8e8, #d0d0d0);
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.8);
  animation: pearlShine 3s ease-in-out infinite;
}

@keyframes pearlShine {
  0%, 100% { opacity: 0.5; transform: scale(0.9); }
  50% { opacity: 1; transform: scale(1.1); }
}

.gold-leaf-float {
  position: absolute;
  top: -30px;
  width: 15px;
  height: 20px;
  background: linear-gradient(135deg, #ffd700, #ffec8b, #daa520);
  border-radius: 50% 0 50% 0;
  animation: goldLeafFall 6s linear infinite;
  box-shadow: 0 0 8px rgba(255, 215, 0, 0.4);
}

@keyframes goldLeafFall {
  0% { transform: translateY(-30px) rotate(0deg); opacity: 0.9; }
  100% { transform: translateY(100vh) rotate(720deg); opacity: 0.2; }
}

.violet-wisp {
  position: absolute;
  width: 60%;
  height: 100px;
  left: 20%;
  border-radius: 50%;
  filter: blur(30px);
  animation: violetWave 8s ease-in-out infinite;
}

.violet-1 { top: 10%; background: linear-gradient(90deg, transparent, rgba(138, 43, 226, 0.4), transparent); }
.violet-2 { top: 30%; background: linear-gradient(90deg, transparent, rgba(186, 85, 211, 0.35), transparent); animation-delay: 2s; }
.violet-3 { top: 50%; background: linear-gradient(90deg, transparent, rgba(221, 160, 221, 0.3), transparent); animation-delay: 4s; }

@keyframes violetWave {
  0%, 100% { transform: translateX(-10%) scaleY(1); opacity: 0.5; }
  50% { transform: translateX(10%) scaleY(1.3); opacity: 0.8; }
}

.radiance-ray {
  position: absolute;
  width: 4px;
  height: 150%;
  left: 30%;
  top: -25%;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(255, 215, 0, 0.5), transparent);
  animation: radianceBurst 3s ease-out infinite;
  transform-origin: center top;
}

.radiance-ray-2 { left: 50%; animation-delay: 1s; }
.radiance-ray-3 { left: 70%; animation-delay: 2s; }

@keyframes radianceBurst {
  0% { transform: scaleY(0.5) rotate(-10deg); opacity: 0.3; }
  50% { transform: scaleY(1.2) rotate(0deg); opacity: 1; }
  100% { transform: scaleY(0.5) rotate(10deg); opacity: 0.3; }
}

.halo-ring {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  border: 3px solid rgba(255, 215, 0, 0.5);
  border-radius: 50%;
  animation: haloExpand 4s ease-in-out infinite;
}

.halo-ring { width: 100px; height: 100px; }
.halo-ring-2 { width: 160px; height: 160px; animation-delay: 1.5s; border-color: rgba(255, 182, 193, 0.4); }

@keyframes haloExpand {
  0%, 100% { transform: translate(-50%, -50%) scale(0.9); opacity: 0.4; }
  50% { transform: translate(-50%, -50%) scale(1.1); opacity: 0.8; }
}

.light-jump-dot {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: radial-gradient(circle, #fff, #ffd700);
  box-shadow: 0 0 10px rgba(255, 215, 0, 0.8);
  animation: lightJump 2s ease-in-out infinite;
}

@keyframes lightJump {
  0%, 100% { transform: translateY(0) scale(0.8); opacity: 0.3; }
  50% { transform: translateY(-20px) scale(1.2); opacity: 1; }
}

.ribbon-strip {
  position: absolute;
  top: -100%;
  width: 8px;
  border-radius: 4px;
  animation: ribbonFly 5s linear infinite;
  opacity: 0.7;
}

@keyframes ribbonFly {
  0% { transform: translateY(0) rotate(0deg); }
  100% { transform: translateY(200vh) rotate(360deg); }
}

.lantern-sway {
  position: absolute;
  bottom: -40px;
  width: 20px;
  height: 28px;
  background: radial-gradient(ellipse, #ff6b6b, #dc143c);
  border-radius: 50%;
  box-shadow: 0 0 15px rgba(255, 100, 100, 0.6);
  animation: lanternSway 5s ease-in-out infinite;
}

@keyframes lanternSway {
  0%, 100% { transform: translateY(0) rotate(-8deg); }
  50% { transform: translateY(-30px) rotate(8deg); }
}

.halo-spin-ring {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 150px;
  height: 150px;
  transform: translate(-50%, -50%);
  border: 4px solid transparent;
  border-top-color: rgba(255, 215, 0, 0.7);
  border-bottom-color: rgba(255, 182, 193, 0.5);
  border-radius: 50%;
  animation: haloSpin 3s linear infinite;
}

@keyframes haloSpin {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

.flow-line {
  position: absolute;
  width: 3px;
  height: 200%;
  left: 30%;
  top: -50%;
  background: linear-gradient(180deg, transparent, rgba(255, 255, 255, 0.6), rgba(255, 215, 0, 0.4), transparent);
  animation: lightFlow 4s ease-in-out infinite;
}

.flow-line-2 { left: 50%; animation-delay: 1.3s; }
.flow-line-3 { left: 70%; animation-delay: 2.6s; }

@keyframes lightFlow {
  0% { transform: translateY(0); opacity: 0; }
  20% { opacity: 1; }
  80% { opacity: 1; }
  100% { transform: translateY(50vh); opacity: 0; }
}

.star-blink-dot {
  position: absolute;
  color: #ffd700;
  text-shadow: 0 0 10px rgba(255, 215, 0, 0.8);
  animation: starBlink 3s ease-in-out infinite;
}

@keyframes starBlink {
  0%, 100% { opacity: 0.2; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.3); }
}

.halo-pulse-ring {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  border: 2px solid rgba(255, 215, 0, 0.5);
  animation: haloPulse 3s ease-out infinite;
}

.halo-pulse-ring { width: 80px; height: 80px; }
.halo-pulse-ring-2 { width: 140px; height: 140px; animation-delay: 1s; border-color: rgba(255, 182, 193, 0.4); }
.halo-pulse-ring-3 { width: 200px; height: 200px; animation-delay: 2s; border-color: rgba(255, 255, 255, 0.3); }

@keyframes haloPulse {
  0% { transform: translate(-50%, -50%) scale(0.5); opacity: 1; }
  100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
}

.confetti-pop {
  position: absolute;
  border-radius: 3px;
  animation: confettiPop 4s ease-out infinite;
  transform: rotate(45deg);
}

@keyframes confettiPop {
  0% { transform: scale(0) rotate(0deg); opacity: 1; }
  50% { transform: scale(1.2) rotate(180deg); opacity: 0.8; }
  100% { transform: scale(0) rotate(360deg); opacity: 0; }
}

.gem-flash-dot {
  position: absolute;
  border-radius: 2px;
  animation: gemFlash 2s ease-in-out infinite;
  box-shadow: 0 0 8px rgba(255, 215, 0, 0.6);
}

@keyframes gemFlash {
  0%, 100% { transform: scale(0.5); opacity: 0.2; }
  50% { transform: scale(1.5); opacity: 1; }
}

.phoenix-wing {
  position: absolute;
  width: 200px;
  height: 300px;
  top: 20%;
  border-radius: 50%;
  animation: phoenixSpread 5s ease-in-out infinite;
}

.phoenix-wing-1 {
  left: -50px;
  background: linear-gradient(135deg, rgba(255, 100, 50, 0.4), rgba(255, 200, 0, 0.3), transparent);
  transform-origin: right center;
}

.phoenix-wing-2 {
  right: -50px;
  background: linear-gradient(225deg, rgba(255, 100, 50, 0.4), rgba(255, 200, 0, 0.3), transparent);
  transform-origin: left center;
}

@keyframes phoenixSpread {
  0%, 100% { transform: scaleX(0.8) rotate(0deg); opacity: 0.6; }
  50% { transform: scaleX(1.2) rotate(5deg); opacity: 1; }
}

.flame-warp {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at center, rgba(255, 100, 50, 0.3), rgba(255, 200, 0, 0.2), transparent 70%);
  animation: flameWarp 3s ease-in-out infinite;
}

@keyframes flameWarp {
  0%, 100% { transform: scale(1) rotate(0deg); opacity: 0.6; }
  50% { transform: scale(1.1) rotate(2deg); opacity: 1; }
}

.golden-glow-shine {
  position: absolute;
  width: 200%;
  height: 80px;
  left: -50%;
  top: 15%;
  background: linear-gradient(90deg, transparent, rgba(255, 215, 0, 0.4), rgba(255, 255, 255, 0.8), rgba(255, 215, 0, 0.4), transparent);
  animation: goldenGlowSweep 5s ease-in-out infinite;
}

.golden-glow-shine-2 { top: 45%; animation-delay: 1.7s; }
.golden-glow-shine-3 { top: 75%; animation-delay: 3.4s; }

@keyframes goldenGlowSweep {
  0% { transform: translateX(-50%) rotate(-5deg); }
  100% { transform: translateX(50%) rotate(-5deg); }
}

.card-star-twinkle-layer,
.card-glass-bubble-layer,
.card-butterfly-layer,
.card-firefly-layer,
.card-light-beam-layer,
.card-rainbow-layer,
.card-heart-smoke-layer,
.card-gem-rain-layer,
.card-feather-layer,
.card-water-ripple-layer,
.card-shooting-star-layer,
.card-pearl-layer,
.card-gold-leaf-layer,
.card-dream-violet-layer,
.card-radiance-layer,
.card-halo-layer,
.card-light-jump-layer,
.card-ribbon-layer,
.card-lantern-float-layer,
.card-halo-spin-layer,
.card-light-flow-layer,
.card-star-blink-layer,
.card-halo-pulse-layer,
.card-confetti-celebrate-layer,
.card-gem-flash-layer,
.card-phoenix-layer,
.card-flame-text-layer,
.card-golden-glow-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 210000;
}

.card-star-twinkle {
  position: absolute;
  width: 6px;
  height: 6px;
  background: radial-gradient(circle, #fff, #ffd700);
  border-radius: 50%;
  animation: cardStarTwinkle 2s ease-in-out infinite;
  box-shadow: 0 0 6px rgba(255, 215, 0, 0.8);
}

@keyframes cardStarTwinkle {
  0%, 100% { transform: scale(0.5); opacity: 0.3; }
  50% { transform: scale(1.5); opacity: 1; }
}

.card-glass-bubble {
  position: absolute;
  bottom: -20px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.9), rgba(200, 230, 255, 0.4));
  animation: cardGlassBubble 4s ease-out infinite;
  box-shadow: inset 0 0 10px rgba(255, 255, 255, 0.5);
}

@keyframes cardGlassBubble {
  0% { transform: translateY(0); opacity: 0; }
  10% { opacity: 0.8; }
  100% { transform: translateY(-50vh); opacity: 0; }
}

.card-butterfly {
  position: absolute;
  bottom: -20px;
  width: 14px;
  height: 10px;
  background: linear-gradient(135deg, #ff6bd6, #ffd93d);
  border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
  animation: cardButterfly 5s ease-in-out infinite;
}

@keyframes cardButterfly {
  0% { transform: translateY(0) translateX(0); }
  50% { transform: translateY(-30vh) translateX(10px); }
  100% { transform: translateY(-60vh) translateX(0); opacity: 0; }
}

.card-firefly-dot {
  position: absolute;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #ffd700;
  box-shadow: 0 0 8px #ffd700;
  animation: cardFirefly 3s ease-in-out infinite;
}

@keyframes cardFirefly {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 1; }
}

.card-beam {
  position: absolute;
  width: 3px;
  height: 80%;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.8), transparent);
  animation: cardBeam 4s ease-in-out infinite;
}

.card-beam-1 { left: 30%; }
.card-beam-2 { left: 60%; animation-delay: 2s; }

@keyframes cardBeam {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.8; }
}

.card-rainbow-arc {
  position: absolute;
  width: 200px;
  height: 100px;
  left: 50%;
  top: 30%;
  transform: translateX(-50%);
  border-radius: 200px 200px 0 0;
  background: linear-gradient(180deg, rgba(255, 0, 0, 0.3), rgba(255, 165, 0, 0.3), rgba(255, 255, 0, 0.3), transparent);
  animation: cardRainbow 4s ease-in-out infinite;
}

@keyframes cardRainbow {
  0%, 100% { opacity: 0.4; transform: translateX(-50%) scale(0.9); }
  50% { opacity: 0.7; transform: translateX(-50%) scale(1.1); }
}

.card-heart-smoke {
  position: absolute;
  bottom: -15px;
  color: rgba(255, 100, 150, 0.5);
  animation: cardHeartSmoke 4s ease-out infinite;
  filter: blur(2px);
}

@keyframes cardHeartSmoke {
  0% { transform: translateY(0) scale(0.5); opacity: 0; }
  20% { opacity: 0.5; }
  100% { transform: translateY(-50vh) scale(1.2); opacity: 0; }
}

.card-gem-drop {
  position: absolute;
  top: -15px;
  border-radius: 3px;
  background: linear-gradient(135deg, #ffd700, #ff6b6b);
  animation: cardGemFall 3s linear infinite;
  box-shadow: 0 0 4px rgba(255, 215, 0, 0.5);
}

@keyframes cardGemFall {
  0% { transform: translateY(0); opacity: 1; }
  100% { transform: translateY(50vh); opacity: 0; }
}

.card-feather {
  position: absolute;
  top: -15px;
  width: 8px;
  height: 14px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(200, 220, 255, 0.5));
  border-radius: 50% 50% 50% 50% / 80% 80% 20% 20%;
  animation: cardFeather 6s linear infinite;
}

@keyframes cardFeather {
  0% { transform: translateY(0) translateX(0); opacity: 0.8; }
  100% { transform: translateY(50vh) translateX(30px); opacity: 0; }
}

.card-ripple {
  position: absolute;
  border: 2px solid rgba(100, 200, 255, 0.4);
  border-radius: 50%;
  animation: cardRipple 3s ease-out infinite;
}

.card-ripple-1 { width: 40px; height: 40px; left: 30%; top: 40%; }
.card-ripple-2 { width: 70px; height: 70px; left: 50%; top: 50%; animation-delay: 1s; }

@keyframes cardRipple {
  0% { transform: scale(0); opacity: 1; }
  100% { transform: scale(2); opacity: 0; }
}

.card-shooting-star {
  position: absolute;
  width: 50px;
  height: 2px;
  background: linear-gradient(90deg, #fff, #ffd700, transparent);
  animation: cardShootingStar 2s linear infinite;
}

@keyframes cardShootingStar {
  0% { transform: translateX(0); opacity: 1; }
  100% { transform: translateX(100px); opacity: 0; }
}

.card-pearl-dot {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #fff, #d0d0d0);
  box-shadow: 0 0 6px rgba(255, 255, 255, 0.8);
  animation: cardPearl 2.5s ease-in-out infinite;
}

@keyframes cardPearl {
  0%, 100% { opacity: 0.5; transform: scale(0.9); }
  50% { opacity: 1; transform: scale(1.1); }
}

.card-gold-leaf {
  position: absolute;
  top: -15px;
  width: 10px;
  height: 14px;
  background: linear-gradient(135deg, #ffd700, #ffec8b);
  border-radius: 50% 0 50% 0;
  animation: cardGoldLeaf 5s linear infinite;
  box-shadow: 0 0 5px rgba(255, 215, 0, 0.4);
}

@keyframes cardGoldLeaf {
  0% { transform: translateY(0) rotate(0deg); opacity: 0.8; }
  100% { transform: translateY(50vh) rotate(360deg); opacity: 0; }
}

.card-violet {
  position: absolute;
  width: 80%;
  height: 60px;
  left: 10%;
  border-radius: 50%;
  filter: blur(15px);
  animation: cardViolet 6s ease-in-out infinite;
}

.card-violet-1 { top: 20%; background: linear-gradient(90deg, transparent, rgba(138, 43, 226, 0.3), transparent); }
.card-violet-2 { top: 40%; background: linear-gradient(90deg, transparent, rgba(186, 85, 211, 0.25), transparent); animation-delay: 2s; }

@keyframes cardViolet {
  0%, 100% { opacity: 0.4; transform: scaleX(0.9); }
  50% { opacity: 0.7; transform: scaleX(1.1); }
}

.card-radiance-ray {
  position: absolute;
  width: 3px;
  height: 100%;
  left: 35%;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.8), rgba(255, 215, 0, 0.4), transparent);
  animation: cardRadiance 3s ease-out infinite;
}

.card-radiance-ray-2 { left: 55%; animation-delay: 1.5s; }

@keyframes cardRadiance {
  0%, 100% { opacity: 0.3; transform: scaleY(0.8); }
  50% { opacity: 0.9; transform: scaleY(1.2); }
}

.card-halo-ring {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 120px;
  height: 120px;
  transform: translate(-50%, -50%);
  border: 3px solid rgba(255, 215, 0, 0.5);
  border-radius: 50%;
  animation: cardHalo 4s ease-in-out infinite;
}

@keyframes cardHalo {
  0%, 100% { transform: translate(-50%, -50%) scale(0.9); opacity: 0.4; }
  50% { transform: translate(-50%, -50%) scale(1.1); opacity: 0.8; }
}

.card-light-jump {
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: radial-gradient(circle, #fff, #ffd700);
  box-shadow: 0 0 8px rgba(255, 215, 0, 0.7);
  animation: cardLightJump 2s ease-in-out infinite;
}

@keyframes cardLightJump {
  0%, 100% { transform: translateY(0); opacity: 0.3; }
  50% { transform: translateY(-15px); opacity: 1; }
}

.card-ribbon {
  position: absolute;
  top: -50%;
  width: 6px;
  height: 80px;
  border-radius: 3px;
  animation: cardRibbon 4s linear infinite;
  opacity: 0.6;
}

@keyframes cardRibbon {
  0% { transform: translateY(0) rotate(0deg); }
  100% { transform: translateY(100vh) rotate(180deg); }
}

.card-lantern-sway {
  position: absolute;
  bottom: -20px;
  width: 14px;
  height: 20px;
  background: radial-gradient(ellipse, #ff6b6b, #dc143c);
  border-radius: 50%;
  box-shadow: 0 0 10px rgba(255, 100, 100, 0.5);
  animation: cardLanternSway 4s ease-in-out infinite;
}

@keyframes cardLanternSway {
  0%, 100% { transform: rotate(-6deg); }
  50% { transform: rotate(6deg); }
}

.card-halo-spin-ring {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 100px;
  height: 100px;
  transform: translate(-50%, -50%);
  border: 3px solid transparent;
  border-top-color: rgba(255, 215, 0, 0.6);
  border-bottom-color: rgba(255, 182, 193, 0.4);
  border-radius: 50%;
  animation: cardHaloSpin 2s linear infinite;
}

@keyframes cardHaloSpin {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

.card-flow-line {
  position: absolute;
  width: 2px;
  height: 120%;
  left: 35%;
  background: linear-gradient(180deg, transparent, rgba(255, 255, 255, 0.6), transparent);
  animation: cardFlow 3s ease-in-out infinite;
}

.card-flow-line-2 { left: 60%; animation-delay: 1.5s; }

@keyframes cardFlow {
  0% { transform: translateY(-20%); opacity: 0; }
  20% { opacity: 1; }
  80% { opacity: 1; }
  100% { transform: translateY(20%); opacity: 0; }
}

.card-star-blink {
  position: absolute;
  color: #ffd700;
  text-shadow: 0 0 8px rgba(255, 215, 0, 0.7);
  animation: cardStarBlink 2.5s ease-in-out infinite;
}

@keyframes cardStarBlink {
  0%, 100% { opacity: 0.2; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.2); }
}

.card-halo-pulse-ring {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  border: 2px solid rgba(255, 215, 0, 0.5);
  border-radius: 50%;
  animation: cardHaloPulse 2.5s ease-out infinite;
}

.card-halo-pulse-ring-2 { width: 140px; height: 140px; animation-delay: 0.8s; }

@keyframes cardHaloPulse {
  0% { transform: translate(-50%, -50%) scale(0.5); opacity: 1; }
  100% { transform: translate(-50%, -50%) scale(1.2); opacity: 0; }
}

.card-confetti-pop {
  position: absolute;
  border-radius: 2px;
  animation: cardConfettiPop 3s ease-out infinite;
}

@keyframes cardConfettiPop {
  0% { transform: scale(0); opacity: 1; }
  50% { opacity: 0.8; }
  100% { transform: scale(0); opacity: 0; }
}

.card-gem-flash {
  position: absolute;
  border-radius: 2px;
  animation: cardGemFlash 1.5s ease-in-out infinite;
  box-shadow: 0 0 6px rgba(255, 215, 0, 0.5);
}

@keyframes cardGemFlash {
  0%, 100% { transform: scale(0.5); opacity: 0.2; }
  50% { transform: scale(1.2); opacity: 1; }
}

.card-phoenix-wing {
  position: absolute;
  width: 150px;
  height: 200px;
  top: 10%;
  border-radius: 50%;
  animation: cardPhoenix 4s ease-in-out infinite;
}

.card-phoenix-wing-1 {
  left: -30px;
  background: linear-gradient(135deg, rgba(255, 100, 50, 0.3), rgba(255, 200, 0, 0.2), transparent);
}

.card-phoenix-wing-2 {
  right: -30px;
  background: linear-gradient(225deg, rgba(255, 100, 50, 0.3), rgba(255, 200, 0, 0.2), transparent);
}

@keyframes cardPhoenix {
  0%, 100% { transform: scaleX(0.8); opacity: 0.5; }
  50% { transform: scaleX(1.1); opacity: 0.8; }
}

.card-flame-warp {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at center, rgba(255, 100, 50, 0.2), rgba(255, 200, 0, 0.15), transparent 70%);
  animation: cardFlame 2.5s ease-in-out infinite;
}

@keyframes cardFlame {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.05); }
}

.card-golden-glow-shine {
  position: absolute;
  width: 150%;
  height: 50px;
  left: -25%;
  top: 20%;
  background: linear-gradient(90deg, transparent, rgba(255, 215, 0, 0.3), rgba(255, 255, 255, 0.6), rgba(255, 215, 0, 0.3), transparent);
  animation: cardGoldenGlow 3s ease-in-out infinite;
}

.card-golden-glow-shine-2 { top: 50%; animation-delay: 1.5s; }

@keyframes cardGoldenGlow {
  0% { transform: translateX(-30%); }
  100% { transform: translateX(30%); }
}

.ink-spread-layer,
.cloud-float-layer,
.candle-layer,
.moon-glow-layer,
.silk-drift-layer,
.paper-crane-layer,
.ribbon-knot-layer,
.lotus-layer,
.cloud-mist-layer,
.star-wish-layer,
.stardust-layer,
.afterglow-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 15;
}

.ink-spot {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(50, 30, 30, 0.3), transparent);
  filter: blur(15px);
  animation: inkSpread 6s ease-out infinite;
}

.ink-spot-1 { width: 150px; height: 150px; left: 20%; top: 30%; }
.ink-spot-2 { width: 120px; height: 120px; left: 60%; top: 50%; animation-delay: 2s; }
.ink-spot-3 { width: 100px; height: 100px; left: 40%; top: 70%; animation-delay: 4s; }

@keyframes inkSpread {
  0% { transform: scale(0.3); opacity: 0; }
  30% { opacity: 0.5; }
  100% { transform: scale(2); opacity: 0; }
}

.cloud {
  position: absolute;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 50px;
  filter: blur(10px);
  animation: cloudFloat 10s ease-in-out infinite;
}

.cloud-1 { width: 180px; height: 60px; left: -50px; top: 15%; }
.cloud-2 { width: 150px; height: 50px; left: -40px; top: 35%; animation-delay: 3s; }
.cloud-3 { width: 200px; height: 70px; left: -60px; top: 55%; animation-delay: 6s; }

@keyframes cloudFloat {
  0% { transform: translateX(0); opacity: 0.4; }
  100% { transform: translateX(calc(100vw + 200px)); opacity: 0.6; }
}

.candle-flame {
  position: absolute;
  width: 12px;
  height: 40px;
  background: linear-gradient(180deg, rgba(255, 200, 100, 0.9), rgba(255, 100, 50, 0.6), transparent);
  border-radius: 50% 50% 0 0;
  animation: candleFlicker 0.4s ease-in-out infinite alternate;
  box-shadow: 0 0 25px rgba(255, 200, 100, 0.6), 0 0 50px rgba(255, 150, 50, 0.3);
}

.candle-flame { left: 35%; top: 10%; }
.candle-flame-2 { left: 55%; animation-delay: 0.2s; }

@keyframes candleFlicker {
  0% { transform: scaleY(0.9) scaleX(0.95); opacity: 0.8; }
  100% { transform: scaleY(1.1) scaleX(1.05); opacity: 1; }
}

.moon-sphere {
  position: absolute;
  width: 100px;
  height: 100px;
  right: 10%;
  top: 10%;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 240, 0.95), rgba(255, 255, 200, 0.5), transparent 70%);
  border-radius: 50%;
  box-shadow: 0 0 40px rgba(255, 255, 200, 0.5);
  animation: moonGlow 6s ease-in-out infinite;
}

@keyframes moonGlow {
  0%, 100% { box-shadow: 0 0 40px rgba(255, 255, 200, 0.4); }
  50% { box-shadow: 0 0 80px rgba(255, 255, 200, 0.7); }
}

.moon-rays {
  position: absolute;
  width: 200%;
  height: 60px;
  right: -50%;
  top: 5%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 220, 0.1), transparent);
  animation: moonRays 8s ease-in-out infinite;
}

@keyframes moonRays {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.5; }
}

.silk-drift {
  position: absolute;
  width: 250%;
  height: 100px;
  left: -75%;
  border-radius: 50%;
  filter: blur(12px);
  animation: silkDrift 8s ease-in-out infinite;
}

.silk-drift-1 { top: 20%; background: linear-gradient(90deg, transparent, rgba(255, 240, 250, 0.5), rgba(240, 220, 255, 0.4), transparent); }
.silk-drift-2 { top: 45%; background: linear-gradient(90deg, transparent, rgba(240, 220, 255, 0.4), rgba(255, 240, 250, 0.3), transparent); animation-delay: 2s; }

@keyframes silkDrift {
  0%, 100% { transform: translateX(-15%) rotate(-5deg); opacity: 0.4; }
  50% { transform: translateX(15%) rotate(5deg); opacity: 0.7; }
}

.paper-crane-fly {
  position: absolute;
  bottom: -40px;
  width: 24px;
  height: 20px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(220, 230, 255, 0.7));
  clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
  animation: paperCrane 8s ease-in-out infinite;
}

@keyframes paperCrane {
  0% { transform: translateY(0) translateX(0) rotate(-15deg); opacity: 0; }
  10% { opacity: 0.8; }
  50% { transform: translateY(-40vh) translateX(30px) rotate(5deg); opacity: 0.9; }
  90% { opacity: 0.8; }
  100% { transform: translateY(-80vh) translateX(-10px) rotate(-10deg); opacity: 0; }
}

.ribbon-circle {
  position: absolute;
  width: 80px;
  height: 80px;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  border: 4px solid rgba(255, 150, 180, 0.5);
  border-radius: 50%;
  animation: ribbonKnot 5s ease-in-out infinite;
}

.ribbon-ends {
  position: absolute;
  width: 60px;
  height: 100px;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -30%);
  background: linear-gradient(180deg, rgba(255, 150, 180, 0.3), transparent);
  clip-path: polygon(30% 0%, 70% 0%, 70% 100%, 30% 100%, 0% 50%);
  animation: ribbonKnot 5s ease-in-out infinite reverse;
}

@keyframes ribbonKnot {
  0%, 100% { transform: translate(-50%, -50%) scale(0.95) rotate(0deg); opacity: 0.5; }
  50% { transform: translate(-50%, -50%) scale(1.05) rotate(180deg); opacity: 0.8; }
}

.lotus-flower {
  position: absolute;
  border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
  animation: lotusBloom 6s ease-in-out infinite;
}

.lotus-flower-1 {
  width: 80px;
  height: 60px;
  left: 25%;
  top: 60%;
  background: radial-gradient(ellipse, rgba(255, 180, 200, 0.5), rgba(255, 200, 210, 0.3), transparent);
  filter: blur(5px);
}

.lotus-flower-2 {
  width: 60px;
  height: 45px;
  right: 25%;
  top: 65%;
  background: radial-gradient(ellipse, rgba(255, 200, 220, 0.4), rgba(255, 180, 200, 0.2), transparent);
  filter: blur(8px);
  animation-delay: 2s;
}

@keyframes lotusBloom {
  0%, 100% { transform: scale(0.9); opacity: 0.4; }
  50% { transform: scale(1.1); opacity: 0.7; }
}

.mist-wisp {
  position: absolute;
  width: 120%;
  height: 80px;
  left: -10%;
  border-radius: 50%;
  filter: blur(20px);
  animation: cloudMist 10s ease-in-out infinite;
}

.mist-wisp-1 { top: 20%; background: rgba(200, 200, 220, 0.25); }
.mist-wisp-2 { top: 40%; background: rgba(180, 180, 200, 0.2); animation-delay: 2s; }
.mist-wisp-3 { top: 60%; background: rgba(200, 200, 220, 0.15); animation-delay: 4s; }

@keyframes cloudMist {
  0%, 100% { transform: translateX(-5%) scaleX(0.95); opacity: 0.4; }
  50% { transform: translateX(5%) scaleX(1.05); opacity: 0.6; }
}

.wish-star {
  position: absolute;
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, #fff, #ffd700, transparent);
  animation: wishStar 3s linear infinite;
  border-radius: 50%;
}

@keyframes wishStar {
  0% { transform: translateX(0) translateY(0); opacity: 1; }
  100% { transform: translateX(100px) translateY(60px); opacity: 0; }
}

.dust-particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.9), transparent);
  border-radius: 50%;
  animation: dustFloat 4s ease-in-out infinite;
}

@keyframes dustFloat {
  0%, 100% { transform: translateY(0) scale(0.8); opacity: 0.3; }
  50% { transform: translateY(-15px) scale(1.2); opacity: 0.8; }
}

.glow-warm {
  position: absolute;
  inset: auto 10% 15% 10%;
  height: 100px;
  background: radial-gradient(ellipse at center bottom, rgba(255, 200, 150, 0.3), rgba(255, 180, 150, 0.2), transparent 70%);
  filter: blur(20px);
  animation: afterglowWarm 5s ease-in-out infinite;
}

.glow-warm-2 { inset: auto 20% 25% 20%; animation-delay: 1.5s; }

@keyframes afterglowWarm {
  0%, 100% { opacity: 0.3; transform: scaleX(0.95); }
  50% { opacity: 0.5; transform: scaleX(1.05); }
}
</style>
