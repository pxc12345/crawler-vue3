<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useBlessingStore } from '@/stores/blessing'
import { getContentConfig, getSettings, saveContentConfig } from '@/utils/api'

const router = useRouter()
const store = useBlessingStore()

type StepItem = {
  step_key: string
  step_name: string
  step_order: number
  title: string
  body: string
}

const activeMode = ref<'birthday' | 'festival'>('birthday')
const configs = ref<Record<'birthday' | 'festival', StepItem[]>>({
  birthday: [],
  festival: [],
})
const saving = ref(false)
const currentFestival = ref('')

const stepNameMap: Record<string, string> = {
  welcome: '开场欢迎页',
  intro: '导语页',
  main: '主祝福页',
  closing: '收尾落款页',
}

const birthdayDefaults: StepItem[] = [
  { step_key: 'welcome', step_name: '开场欢迎页', step_order: 1, title: '今夜为你亮灯', body: '把日历翻到今天，连风都像替你轻声报喜。愿你推开这一页时，先被温柔接住，再被喜悦慢慢包围。' },
  { step_key: 'intro', step_name: '导语页', step_order: 2, title: '把好时光留给你', body: '愿你走过的每一步都算数，认真喜欢过的事情都能开花，努力熬过的夜晚都能在未来变成星光。' },
  { step_key: 'main', step_name: '主祝福页', step_order: 3, title: '愿望开始靠近', body: '愿你新一岁的生活有热烈也有安稳，有奔赴远方的勇气，也有回到日常的松弛。愿欢喜有回应，期待有着落，生日快乐。' },
  { step_key: 'closing', step_name: '收尾落款页', step_order: 4, title: '把祝福珍藏', body: '把这一份偏爱好好收下吧。愿它陪你度过明亮的时刻，也陪你穿过普通的日子，提醒你一直值得被认真祝福。' },
]

const festivalDefaults: StepItem[] = [
  { step_key: 'welcome', step_name: '开场欢迎页', step_order: 1, title: '节日已至', body: '节日像一封刚拆开的信，先把热闹送到门前，再把惦念慢慢放进心里。今天这一份祝福，也专门为你而来。' },
  { step_key: 'intro', step_name: '导语页', step_order: 2, title: '愿此刻被照亮', body: '愿你无论身在何处，都能在这个节点里感受到陪伴、松弛和被惦记的安心，让生活暂时停下来，对你多一点温柔。' },
  { step_key: 'main', step_name: '主祝福页', step_order: 3, title: '平安喜乐常在', body: '愿这个节日替你带来轻松和好消息，愿平安常在，喜乐常在，心之所向都有回音。' },
  { step_key: 'closing', step_name: '收尾落款页', step_order: 4, title: '心意缓缓落下', body: '把这份节日心意留在今天，也带进之后的日子里。愿你接下来遇见的人和事，都能继续把温暖递给你。' },
]

const steps = computed(() => configs.value[activeMode.value])
const modeLabel = computed(() => activeMode.value === 'birthday' ? '生日模式' : '节日模式')

onMounted(async () => {
  store.restoreUser()
  if (store.role !== 'admin') {
    router.push('/login')
    return
  }
  await Promise.all([loadContent(), loadSettings()])
})

function cloneSteps(items: StepItem[]) {
  return items.map((item) => ({ ...item }))
}

function normalizeSteps(items: any[] | undefined, fallback: StepItem[]) {
  if (!items || !items.length) return cloneSteps(fallback)
  const source = new Map(items.map((item) => [item.step_key, item]))
  return fallback.map((item) => {
    const matched = source.get(item.step_key) || {}
    return {
      ...item,
      title: matched.title || item.title,
      body: matched.body || item.body,
      step_order: matched.step_order || item.step_order,
      step_name: matched.step_name || item.step_name,
    }
  })
}

async function loadSettings() {
  try {
    const res: any = await getSettings()
    if (res.code === 200) {
      currentFestival.value = res.data.current_nearest_festival || ''
    }
  } catch {
    currentFestival.value = ''
  }
}

async function loadContent() {
  try {
    const res: any = await getContentConfig()
    if (res.code === 200) {
      configs.value = {
        birthday: normalizeSteps(res.data.birthday, birthdayDefaults),
        festival: normalizeSteps(res.data.festival, festivalDefaults),
      }
      return
    }
  } catch {
    showToast('加载文案失败，已切换到默认文案')
  }

  configs.value = {
    birthday: cloneSteps(birthdayDefaults),
    festival: cloneSteps(festivalDefaults),
  }
}

async function handleSave() {
  saving.value = true
  try {
    const res: any = await saveContentConfig({
      mode: activeMode.value,
      steps: steps.value.map((item) => ({
        step_key: item.step_key,
        step_order: item.step_order,
        title: item.title.trim(),
        body: item.body.trim(),
      })),
    })
    if (res.code === 200) {
      showToast(`${modeLabel.value}文案已保存`)
      await loadContent()
    } else {
      showToast(res.msg || '保存失败')
    }
  } catch {
    showToast('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

function restoreDefaults() {
  if (activeMode.value === 'birthday') {
    configs.value.birthday = cloneSteps(birthdayDefaults)
  } else {
    configs.value.festival = cloneSteps(festivalDefaults)
  }
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
  <div class="content-page">
    <header class="content-header">
      <button class="btn-secondary" @click="router.push('/admin')">返回</button>
      <div class="header-copy">
        <p class="header-eyebrow">Step Copy</p>
        <h1>分步文案配置</h1>
      </div>
      <button class="btn-primary header-save" :disabled="saving" @click="handleSave">保存</button>
    </header>

    <main class="content-main">
      <section class="hero-panel">
        <div>
          <p class="hero-kicker">四段式祝福流程</p>
          <h2>每一步都单独设置，让情绪层层递进</h2>
          <p class="hero-text">现在这里会始终显示完整四步，不会再出现空白页。你可以直接编辑标题和正文，也可以一键恢复默认高级文案。</p>
        </div>
        <button class="btn-secondary restore-btn" @click="restoreDefaults">恢复当前模式默认文案</button>
      </section>

      <div class="tabs">
        <button :class="{ active: activeMode === 'birthday' }" @click="activeMode = 'birthday'">生日模式</button>
        <button :class="{ active: activeMode === 'festival' }" @click="activeMode = 'festival'">节日模式</button>
      </div>

      <section class="mode-banner" :class="activeMode">
        <div class="mode-copy">
          <p class="mode-name">{{ modeLabel }}</p>
          <h3>{{ activeMode === 'birthday' ? '适合层层铺陈暖意与偏爱' : `当前最近节日：${currentFestival || '自动匹配中'}` }}</h3>
          <p>{{ activeMode === 'birthday' ? '建议从欢迎、肯定、祝福、收藏四个情绪层次来写。' : '节日模式仍然沿用原有自动匹配规则，这里只负责编辑四步展示文案。' }}</p>
        </div>
      </section>

      <section class="step-list">
        <article v-for="(step, index) in steps" :key="step.step_key" class="step-card">
          <div class="step-head">
            <div class="step-badge">{{ index + 1 }}</div>
            <div>
              <p class="step-type">{{ step.step_name || stepNameMap[step.step_key] }}</p>
              <h2>{{ step.title || '请输入当前步骤标题' }}</h2>
            </div>
          </div>

          <label class="editor-block">
            <span>页面标题</span>
            <input v-model="step.title" class="input-field soft-input" maxlength="120" placeholder="请输入当前步骤标题" />
          </label>

          <label class="editor-block">
            <span>页面正文</span>
            <textarea v-model="step.body" class="textarea-field soft-input step-textarea" placeholder="请输入当前步骤正文"></textarea>
          </label>

          <div class="step-preview">
            <p class="preview-label">实时预览</p>
            <h3>{{ step.title }}</h3>
            <p>{{ step.body }}</p>
          </div>
        </article>
      </section>

      <button class="btn-primary save-bottom" :disabled="saving" @click="handleSave">
        {{ saving ? '保存中' : `保存${modeLabel}文案` }}
      </button>
    </main>
  </div>
</template>

<style scoped>
.content-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(228, 146, 112, 0.14), transparent 30%),
    radial-gradient(circle at top right, rgba(87, 135, 177, 0.18), transparent 28%),
    linear-gradient(180deg, #f8f3eb 0%, #f1e8dd 100%);
}

.content-header {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 12px;
  padding: 18px;
  background: rgba(255, 250, 244, 0.9);
  backdrop-filter: blur(18px);
  border-bottom: 1px solid rgba(124, 97, 70, 0.14);
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-copy {
  min-width: 0;
}

.header-eyebrow {
  color: #997a57;
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
}

.content-header h1 {
  color: #2f2721;
  font-size: 1.12rem;
  font-weight: 900;
}

.header-save {
  padding-inline: 20px;
}

.content-main {
  padding: 18px;
  display: grid;
  gap: 16px;
}

.hero-panel,
.mode-banner,
.step-card {
  border-radius: 20px;
  border: 1px solid rgba(121, 94, 68, 0.12);
  box-shadow: 0 18px 40px rgba(77, 58, 39, 0.08);
}

.hero-panel {
  background: linear-gradient(145deg, rgba(255, 250, 246, 0.92), rgba(255, 244, 236, 0.82));
  padding: 20px;
  display: grid;
  gap: 16px;
}

.hero-kicker,
.preview-label,
.step-type,
.mode-name {
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.hero-kicker,
.preview-label {
  color: #9f7857;
}

.hero-panel h2,
.mode-banner h3,
.step-head h2,
.step-preview h3 {
  color: #2f2721;
  font-weight: 900;
}

.hero-panel h2 {
  font-size: 1.32rem;
  line-height: 1.35;
  margin: 6px 0 8px;
}

.hero-text,
.mode-banner p,
.step-preview p {
  color: #645244;
  line-height: 1.7;
}

.restore-btn {
  justify-self: start;
}

.tabs {
  background: rgba(121, 94, 68, 0.08);
  padding: 5px;
  border-radius: 16px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}

.tabs button {
  min-height: 48px;
  border: 0;
  border-radius: 12px;
  background: transparent;
  color: #81674e;
  font-weight: 800;
}

.tabs button.active {
  background: #fffaf4;
  color: #2d7d8c;
  box-shadow: 0 8px 20px rgba(58, 48, 35, 0.08);
}

.mode-banner {
  padding: 18px;
  color: #fff;
}

.mode-banner.birthday {
  background: linear-gradient(135deg, #8a2d3b 0%, #cf6f5d 100%);
}

.mode-banner.festival {
  background: linear-gradient(135deg, #245777 0%, #3a8e79 100%);
}

.mode-copy h3 {
  color: #fff;
  font-size: 1.15rem;
  margin: 4px 0 8px;
}

.mode-copy p,
.mode-name {
  color: rgba(255, 255, 255, 0.86);
}

.step-list {
  display: grid;
  gap: 14px;
}

.step-card {
  background: rgba(255, 251, 246, 0.92);
  padding: 18px;
}

.step-head {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 12px;
  align-items: start;
  margin-bottom: 14px;
}

.step-badge {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #c77a59, #8f4553);
  color: #fff;
  font-weight: 900;
  box-shadow: 0 10px 24px rgba(137, 67, 64, 0.18);
}

.step-type {
  color: #a07c5e;
}

.step-head h2 {
  font-size: 1.08rem;
  line-height: 1.35;
  margin-top: 4px;
}

.editor-block {
  display: block;
  margin-top: 14px;
}

.editor-block span {
  display: block;
  color: #7a6250;
  font-size: 0.79rem;
  font-weight: 800;
  margin-bottom: 7px;
}

.soft-input {
  background: rgba(255, 255, 255, 0.84);
  border-color: rgba(177, 146, 118, 0.2);
}

.step-textarea {
  min-height: 148px;
}

.step-preview {
  margin-top: 14px;
  background: linear-gradient(160deg, #fffdf9, #f8f0e7);
  border-radius: 16px;
  padding: 16px;
}

.step-preview h3 {
  font-size: 1rem;
  margin: 6px 0 8px;
}

.save-bottom {
  width: 100%;
}
</style>
