<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useBlessingStore } from '@/stores/blessing'
import { deleteEffectProfile, getEffectProfiles, saveEffectProfile } from '@/utils/api'

const router = useRouter()
const store = useBlessingStore()

const welcomeEffects = [
  { value: 'mist-glow', label: '晨雾光影' },
  { value: 'light-particles', label: '轻粒子' },
  { value: 'silk-flow', label: '薄纱流动' },
  { value: 'letter-unfold', label: '信笺展开' },
  { value: 'confetti-burst', label: '彩带爆炸' },
  { value: 'floating-hearts', label: '漂浮爱心' },
  { value: 'firework-flash', label: '烟花绽放' },
  { value: 'aurora-wave', label: '极光波浪' },
  { value: 'sparkle-trail', label: '晶钻流光' },
  { value: 'lantern-rise', label: '福灯升腾' },
  { value: 'snowflake-drift', label: '飘雪纷飞' },
  { value: 'petal-fall', label: '花瓣雨' },
  { value: 'bubble-rise', label: '泡泡上浮' },
  { value: 'golden-shimmer', label: '鎏金闪耀' },
]

const introEffects = [
  { value: 'star-twinkle', label: '星光闪烁' },
  { value: 'glass-bubble', label: '琉璃气泡' },
  { value: 'butterfly-fly', label: '蝴蝶飞舞' },
  { value: 'firefly-glow', label: '萤火虫' },
  { value: 'light-beam', label: '光束穿透' },
  { value: 'rainbow-bridge', label: '彩虹桥' },
  { value: 'heart-smoke', label: '心形烟雾' },
  { value: 'gem-rain', label: '宝石雨' },
  { value: 'feather-fall', label: '羽毛飘落' },
  { value: 'water-ripple', label: '水波纹' },
  { value: 'shooting-star', label: '流星雨' },
  { value: 'pearl-string', label: '珍珠串' },
  { value: 'gold-leaf', label: '金箔飘落' },
  { value: 'dream-violet', label: '梦幻紫罗兰' },
]

const mainEffects = [
  { value: 'radiance-burst', label: '光芒四射' },
  { value: 'halo-ring', label: '光环环绕' },
  { value: 'light-jump', label: '光点跳跃' },
  { value: 'ribbon-fly', label: '彩带飞旋' },
  { value: 'lantern-float', label: '灯笼浮动' },
  { value: 'halo-spin', label: '光环旋转' },
  { value: 'light-flow', label: '光芒流动' },
  { value: 'star-blink', label: '星星眨眼' },
  { value: 'halo-pulse', label: '光环脉动' },
  { value: 'confetti-celebrate', label: '礼花绽放' },
  { value: 'gem-flash', label: '宝石闪光' },
  { value: 'phoenix-spread', label: '凤凰展翅' },
  { value: 'flame-text', label: '火焰文字' },
  { value: 'golden-glow', label: '金光普照' },
]

const closingEffects = [
  { value: 'signature-draw', label: '手写落款' },
  { value: 'seal-fade', label: '印章落下' },
  { value: 'ink-spread', label: '墨迹晕染' },
  { value: 'cloud-float', label: '云朵飘移' },
  { value: 'candle-flicker', label: '烛光摇曳' },
  { value: 'moon-glow', label: '月光倾洒' },
  { value: 'silk-drift', label: '丝绸轻飘' },
  { value: 'paper-crane', label: '纸鹤飞舞' },
  { value: 'ribbon-knot', label: '丝带结缘' },
  { value: 'lotus-bloom', label: '莲花绽放' },
  { value: 'cloud-mist', label: '云雾缭绕' },
  { value: 'star-wish', label: '流星许愿' },
  { value: 'stardust', label: '星尘余韵' },
  { value: 'afterglow', label: '余晖收束' },
]

const previewEffect = ref<{ value: string; label: string } | null>(null)

function previewEffectByDblClick(effect: { value: string; label: string }) {
  previewEffect.value = effect
}

function closePreview() {
  previewEffect.value = null
}

const profiles = ref<any[]>([])
const loading = ref(true)
const saving = ref(false)
const editingId = ref<number | null>(null)
const form = ref({
  name: '',
  welcome_effects: ['mist-glow', 'light-particles'],
  intro_effects: ['silk-flow', 'letter-unfold'],
  main_effects: ['stardust', 'festival-bokeh', 'card-highlight'],
  closing_effects: ['signature-draw', 'seal-fade', 'afterglow'],
  particle_density: 0.65,
  motion_level: 0.55,
  glow_intensity: 0.72,
  sort: 0,
})

const stepGroups = computed(() => [
  { key: 'welcome_effects', title: '欢迎页效果', effects: welcomeEffects },
  { key: 'intro_effects', title: '导语页效果', effects: introEffects },
  { key: 'main_effects', title: '主祝福页效果', effects: mainEffects },
  { key: 'closing_effects', title: '收尾页效果', effects: closingEffects },
])

function selectedEffects(key: 'welcome_effects' | 'intro_effects' | 'main_effects' | 'closing_effects') {
  return form.value[key]
}

onMounted(async () => {
  store.restoreUser()
  if (store.role !== 'admin') {
    router.push('/login')
    return
  }
  await loadProfiles()
})

async function loadProfiles() {
  loading.value = true
  try {
    const res: any = await getEffectProfiles()
    if (res.code === 200) profiles.value = res.data || []
  } catch {
    showToast('加载特效方案失败')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  editingId.value = null
  form.value = {
    name: '',
    welcome_effects: ['mist-glow', 'light-particles'],
    intro_effects: ['star-twinkle', 'glass-bubble'],
    main_effects: ['radiance-burst', 'halo-ring'],
    closing_effects: ['signature-draw', 'seal-fade', 'ink-spread', 'moon-glow'],
    particle_density: 0.65,
    motion_level: 0.55,
    glow_intensity: 0.72,
    sort: 0,
  }
}

function editProfile(profile: any) {
  editingId.value = profile.id
  form.value = {
    name: profile.name,
    welcome_effects: [...profile.welcome_effects],
    intro_effects: [...profile.intro_effects],
    main_effects: [...profile.main_effects],
    closing_effects: [...profile.closing_effects],
    particle_density: Number(profile.particle_density),
    motion_level: Number(profile.motion_level),
    glow_intensity: Number(profile.glow_intensity),
    sort: profile.sort || 0,
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function toggleEffect(listKey: 'welcome_effects' | 'intro_effects' | 'main_effects' | 'closing_effects', value: string) {
  const current = form.value[listKey]
  if (current.includes(value)) {
    form.value[listKey] = current.filter((item) => item !== value)
  } else {
    form.value[listKey] = [...current, value]
  }
}

async function handleSave() {
  if (!form.value.name.trim()) {
    showToast('请输入特效方案名称')
    return
  }
  saving.value = true
  try {
    const res: any = await saveEffectProfile({ ...form.value, id: editingId.value || undefined })
    if (res.code === 200) {
      showToast(editingId.value ? '特效方案已更新' : '特效方案已创建')
      resetForm()
      await loadProfiles()
    } else {
      showToast(res.msg || '保存失败')
    }
  } catch {
    showToast('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

async function handleDelete(profile: any) {
  if (!confirm(`确定删除特效方案「${profile.name}」吗？`)) return
  try {
    const res: any = await deleteEffectProfile(profile.id)
    if (res.code === 200) {
      showToast('特效方案已删除')
      if (editingId.value === profile.id) resetForm()
      await loadProfiles()
    } else {
      showToast(res.msg || '删除失败')
    }
  } catch {
    showToast('删除失败，请重试')
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
  <div class="effect-page">
    <header class="effect-header">
      <button class="btn-secondary" @click="router.push('/admin')">返回</button>
      <div>
        <p class="eyebrow">Effects</p>
        <h1>特效方案管理</h1>
      </div>
      <button class="btn-small" @click="resetForm">新建</button>
    </header>

    <main class="effect-content">
      <section class="editor-panel">
        <h2>{{ editingId ? '编辑特效方案' : '创建特效方案' }}</h2>
        <p class="panel-copy">默认已经预置了你指定的高级组合。这里可以继续调整每一步启用哪些动态元素，以及整体密度、动感和高亮强度。</p>

        <label class="field">
          <span>方案名称</span>
          <input v-model="form.name" class="input-field" placeholder="例如：默认高级流光" />
        </label>

        <section v-for="group in stepGroups" :key="group.key" class="effect-block">
          <h3>{{ group.title }} <span class="hint-text">（双击预览效果）</span></h3>
          <div class="chip-grid">
            <button
              v-for="effect in group.effects"
              :key="effect.value"
              type="button"
              class="effect-chip"
              :class="{ active: selectedEffects(group.key as any).includes(effect.value) }"
              @click="toggleEffect(group.key as any, effect.value)"
              @dblclick.stop="previewEffectByDblClick(effect)"
            >
              {{ effect.label }}
            </button>
          </div>
        </section>

        <section class="slider-grid">
          <label class="field">
            <span>粒子密度 {{ form.particle_density.toFixed(2) }}</span>
            <input v-model.number="form.particle_density" type="range" min="0.2" max="1" step="0.01" />
          </label>
          <label class="field">
            <span>动态速度 {{ form.motion_level.toFixed(2) }}</span>
            <input v-model.number="form.motion_level" type="range" min="0.2" max="1" step="0.01" />
          </label>
          <label class="field">
            <span>高亮强度 {{ form.glow_intensity.toFixed(2) }}</span>
            <input v-model.number="form.glow_intensity" type="range" min="0.2" max="1" step="0.01" />
          </label>
        </section>

        <button class="btn-primary save-btn" :disabled="saving" @click="handleSave">
          {{ saving ? '保存中' : '保存特效方案' }}
        </button>
      </section>

      <section class="library-panel">
        <h2>已创建方案</h2>
        <div v-if="loading" class="loading">加载中...</div>
        <div class="profile-list">
          <article v-for="profile in profiles" :key="profile.id" class="profile-card">
            <p class="profile-name">{{ profile.name }}</p>
            <p class="profile-line">欢迎页：{{ profile.welcome_effects.join(' / ') }}</p>
            <p class="profile-line">导语页：{{ profile.intro_effects.join(' / ') }}</p>
            <p class="profile-line">主祝福页：{{ profile.main_effects.join(' / ') }}</p>
            <p class="profile-line">收尾页：{{ profile.closing_effects.join(' / ') }}</p>
            <p class="profile-meta">粒子 {{ profile.particle_density }} | 动态 {{ profile.motion_level }} | 高亮 {{ profile.glow_intensity }}</p>
            <div class="card-actions">
              <button class="btn-small" @click="editProfile(profile)">编辑</button>
              <button class="btn-danger" @click="handleDelete(profile)">删除</button>
            </div>
          </article>
        </div>
      </section>
    </main>

    <div v-if="previewEffect" class="preview-modal" @click.self="closePreview">
      <div class="preview-content">
        <div class="preview-header">
          <h3>效果预览：{{ previewEffect.label }}</h3>
          <button class="close-btn" @click="closePreview">&times;</button>
        </div>
        <div class="preview-stage">
          <div :class="`effect-bg effect-${previewEffect.value}`"></div>
          <div class="preview-card">
            <h4 class="preview-title">祝福标题</h4>
            <p class="preview-text">这里展示祝福内容的文字效果</p>
            <p class="preview-signature">—— 落款签名</p>
          </div>
        </div>
        <p class="preview-tip">以上为效果示意图，实际效果以祝福展示页为准</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.effect-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f7f0fb 0%, #efe5f7 100%);
}

.effect-header {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 12px;
  align-items: center;
  padding: 18px;
  background: rgba(255, 250, 255, 0.9);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(103, 75, 142, 0.12);
  position: sticky;
  top: 0;
  z-index: 10;
}

.eyebrow {
  font-size: 0.74rem;
  font-weight: 800;
  text-transform: uppercase;
  color: #8768a9;
}

.effect-header h1,
.editor-panel h2,
.library-panel h2 {
  color: #30233e;
  font-weight: 900;
}

.effect-content {
  padding: 18px;
  display: grid;
  gap: 16px;
}

.editor-panel,
.library-panel,
.profile-card {
  border-radius: 18px;
  border: 1px solid rgba(103, 75, 142, 0.12);
  background: rgba(255, 250, 255, 0.9);
  box-shadow: 0 18px 40px rgba(77, 58, 90, 0.08);
}

.editor-panel,
.library-panel {
  padding: 18px;
}

.panel-copy,
.profile-line,
.profile-meta {
  color: #66587a;
  line-height: 1.7;
}

.field {
  display: block;
  margin-top: 14px;
}

.field span {
  display: block;
  margin-bottom: 8px;
  font-size: 0.8rem;
  font-weight: 800;
  color: #5b4b71;
}

.effect-block {
  margin-top: 16px;
}

.effect-block h3 {
  color: #3d2e52;
  font-size: 0.96rem;
  font-weight: 900;
  margin-bottom: 10px;
}

.chip-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.effect-chip {
  border: 1px solid rgba(103, 75, 142, 0.14);
  border-radius: 999px;
  padding: 10px 14px;
  background: #fff;
  color: #5b4b71;
  font-weight: 700;
}

.effect-chip.active {
  background: #6e56cf;
  color: #fff;
  border-color: #6e56cf;
}

.slider-grid {
  display: grid;
  gap: 10px;
  margin-top: 16px;
}

.save-btn {
  width: 100%;
  margin-top: 18px;
}

.profile-list {
  display: grid;
  gap: 12px;
  margin-top: 14px;
}

.profile-card {
  padding: 16px;
}

.profile-name {
  color: #30233e;
  font-size: 1rem;
  font-weight: 900;
  margin-bottom: 8px;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
}

.loading {
  color: #66587a;
  padding: 16px 0;
}

.hint-text {
  font-size: 0.75rem;
  font-weight: 400;
  color: #9b8a9b;
  margin-left: 8px;
}

.preview-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.preview-content {
  background: #fff;
  border-radius: 20px;
  padding: 24px;
  width: 90%;
  max-width: 400px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.preview-header h3 {
  color: #30233e;
  font-size: 1.1rem;
  font-weight: 900;
}

.close-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: #f0f0f0;
  color: #666;
  font-size: 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #e0e0e0;
}

.preview-stage {
  position: relative;
  height: 300px;
  border-radius: 16px;
  overflow: hidden;
  background: linear-gradient(180deg, #fef5f8 0%, #f8f0f5 100%);
}

.effect-bg { position: absolute; inset: 0; z-index: 1; pointer-events: none; overflow: hidden; } .preview-card {
  position: absolute;
  inset: 20px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.preview-title {
  color: #7b2f36;
  font-size: 1.2rem;
  font-weight: 900;
  margin-bottom: 10px;
}

.preview-text {
  color: #5a4a4a;
  font-size: 0.9rem;
  line-height: 1.6;
}

.preview-signature {
  color: #8b6b6b;
  font-size: 0.85rem;
  margin-top: 12px;
  font-style: italic;
}

.preview-tip {
  text-align: center;
  color: #9b8a9b;
  font-size: 0.75rem;
  margin-top: 12px;
}

:global(.effect-bg.effect-mist-glow) {
  background: linear-gradient(180deg, #e8f5f9 0%, #f3e5f5 100%);
}
:global(.effect-bg.effect-mist-glow)::before {
  content: '';
  position: absolute;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(255, 150, 180, 0.7) 0%, transparent 70%);
  border-radius: 50%;
  top: 30px;
  left: 30px;
  filter: blur(30px);
  animation: prevMistFloat 3s ease-in-out infinite;
}
:global(.effect-bg.effect-mist-glow)::after {
  content: '';
  position: absolute;
  width: 180px;
  height: 180px;
  background: radial-gradient(circle, rgba(150, 120, 255, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  bottom: 50px;
  right: 30px;
  filter: blur(25px);
  animation: prevMistFloat 3s ease-in-out infinite 1s;
}

@keyframes prevMistFloat {
  0%, 100% { transform: translate(0, 0) scale(1); opacity: 1; }
  50% { transform: translate(30px, -20px) scale(1.3); opacity: 0.8; }
}

:global(.effect-bg.effect-light-particles)::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 30%, rgba(255, 255, 255, 1) 4px, transparent 4px),
    radial-gradient(circle at 60% 50%, rgba(255, 255, 255, 1) 3px, transparent 3px),
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 1) 5px, transparent 5px),
    radial-gradient(circle at 40% 70%, rgba(255, 255, 255, 1) 4px, transparent 4px),
    radial-gradient(circle at 10% 60%, rgba(255, 255, 255, 1) 3px, transparent 3px),
    radial-gradient(circle at 90% 80%, rgba(255, 255, 255, 1) 4px, transparent 4px);
  animation: prevParticleFloat 2s linear infinite;
}

@keyframes prevParticleFloat {
  0% { transform: translateY(0); opacity: 1; }
  50% { transform: translateY(-30px); opacity: 0.8; }
  100% { transform: translateY(0); opacity: 1; }
}

:global(.effect-bg.effect-silk-flow)::before {
  content: '';
  position: absolute;
  width: 200%;
  height: 60px;
  left: -50%;
  top: 30%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent);
  filter: blur(5px);
  animation: prevSilkFlow 4s ease-in-out infinite;
}

@keyframes prevSilkFlow {
  0%, 100% { transform: translateX(-20%) rotate(-5deg); opacity: 0.5; }
  50% { transform: translateX(20%) rotate(5deg); opacity: 0.8; }
}

:global(.effect-bg.effect-confetti-burst)::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(45deg, #ff6b6b 2px, transparent 2px),
    linear-gradient(-45deg, #ffd93d 2px, transparent 2px),
    linear-gradient(90deg, #6bcb77 2px, transparent 2px),
    linear-gradient(0deg, #4d96ff 2px, transparent 2px);
  background-size: 30px 30px;
  animation: prevConfettiFall 2s linear infinite;
}

@keyframes prevConfettiFall {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100%); }
}

:global(.effect-bg.effect-floating-hearts)::before {
  content: '♥ ♥ ♥';
  position: absolute;
  inset: 0;
  color: #ff6b8a;
  font-size: 3rem;
  display: flex;
  justify-content: space-around;
  padding: 20px;
  text-shadow: 0 0 20px rgba(255, 107, 138, 0.8), 0 0 40px rgba(255, 107, 138, 0.5);
  animation: prevHeartFloat 2s ease-in-out infinite;
}

@keyframes prevHeartFloat {
  0%, 100% { transform: translateY(0) scale(1); opacity: 1; }
  50% { transform: translateY(-30px) scale(1.2); opacity: 0.8; }
}

:global(.effect-bg.effect-firework-flash)::before {
  content: '';
  position: absolute;
  width: 8px;
  height: 8px;
  background: radial-gradient(circle, #fff, #ffd700, #ff6b6b, transparent);
  border-radius: 50%;
  top: 30%;
  left: 50%;
  animation: prevFirework 1.5s ease-out infinite;
}

@keyframes prevFirework {
  0% { transform: scale(0); opacity: 1; box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.8); }
  50% { transform: scale(1.5); opacity: 1; box-shadow: 0 0 20px 10px rgba(255, 107, 107, 0.4); }
  100% { transform: scale(2); opacity: 0; box-shadow: 0 0 40px 20px transparent; }
}

:global(.effect-bg.effect-aurora-wave)::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(72, 219, 251, 0.3), rgba(180, 100, 255, 0.3), rgba(255, 180, 219, 0.2), transparent);
  filter: blur(20px);
  animation: prevAurora 6s ease-in-out infinite;
}

@keyframes prevAurora {
  0%, 100% { transform: scaleY(1) translateX(-5%); opacity: 0.5; }
  50% { transform: scaleY(1.3) translateX(5%); opacity: 0.8; }
}

:global(.effect-bg.effect-sparkle-trail)::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 30% 40%, rgba(255,215,0,1) 3px, transparent 3px),
    radial-gradient(circle at 70% 30%, rgba(255,215,0,1) 2px, transparent 2px),
    radial-gradient(circle at 50% 60%, rgba(255,215,0,1) 3px, transparent 3px);
  animation: prevSparkle 2s ease-in-out infinite;
}

@keyframes prevSparkle {
  0%, 100% { transform: scale(0.8); opacity: 0.3; }
  50% { transform: scale(1.2); opacity: 1; }
}

:global(.effect-bg.effect-lantern-rise)::before {
  content: '';
  position: absolute;
  width: 24px;
  height: 32px;
  background: radial-gradient(ellipse, #ff6b6b, #c0392b);
  border-radius: 50%;
  left: 50%;
  bottom: -40px;
  transform: translateX(-50%);
  box-shadow: 0 0 15px rgba(255, 100, 100, 0.6);
  animation: prevLanternRise 4s linear infinite;
}

@keyframes prevLanternRise {
  0% { transform: translateX(-50%) translateY(0); opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { transform: translateX(-50%) translateY(-350px); opacity: 0; }
}

:global(.effect-bg.effect-snowflake-drift)::before {
  content: '❄ ❄ ❄ ❄ ❄ ❄';
  position: absolute;
  inset: 0;
  color: #87ceeb;
  font-size: 2.5rem;
  display: flex;
  justify-content: space-around;
  padding: 15px;
  text-shadow: 0 0 15px rgba(135, 206, 235, 0.8), 0 0 30px rgba(135, 206, 235, 0.5);
  animation: prevSnow 2s linear infinite;
}

@keyframes prevSnow {
  0% { transform: translateY(-100%) rotate(0deg); opacity: 1; }
  50% { opacity: 0.8; }
  100% { transform: translateY(100%) rotate(360deg); opacity: 1; }
}

:global(.effect-bg.effect-petal-fall)::before {
  content: '🌸 🌸 🌸 🌸 🌸';
  position: absolute;
  inset: 0;
  color: #ffb6c1;
  font-size: 2.5rem;
  display: flex;
  justify-content: space-around;
  padding: 15px;
  text-shadow: 0 0 15px rgba(255, 182, 193, 0.8), 0 0 30px rgba(255, 182, 193, 0.5);
  animation: prevPetalFall 3s linear infinite;
}

@keyframes prevPetalFall {
  0% { transform: translateY(-100%) rotate(0deg); opacity: 1; }
  50% { transform: translateY(0%) rotate(180deg); opacity: 0.8; }
  100% { transform: translateY(100%) rotate(360deg); opacity: 1; }
}

:global(.effect-bg.effect-bubble-rise)::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 30% 80%, rgba(255,255,255,0.9) 8px, transparent 8px),
    radial-gradient(circle at 60% 60%, rgba(255,255,255,0.9) 6px, transparent 6px),
    radial-gradient(circle at 80% 40%, rgba(255,255,255,0.9) 10px, transparent 10px);
  animation: prevBubbleRise 3s ease-out infinite;
}

@keyframes prevBubbleRise {
  0% { transform: translateY(30px); opacity: 0; }
  20% { opacity: 0.8; }
  100% { transform: translateY(-30px); opacity: 0; }
}

:global(.effect-bg.effect-golden-shimmer)::before {
  content: '';
  position: absolute;
  width: 200%;
  height: 50px;
  left: -50%;
  top: 30%;
  background: linear-gradient(90deg, transparent, rgba(255,215,0,0.4), rgba(255,255,255,0.6), rgba(255,215,0,0.4), transparent);
  animation: prevGoldenSweep 3s ease-in-out infinite;
}

@keyframes prevGoldenSweep {
  0% { transform: translateX(-30%) rotate(-10deg); }
  100% { transform: translateX(30%) rotate(-10deg); }
}

:global(.effect-bg.effect-star-twinkle)::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 25% 35%, rgba(255,255,255,1) 4px, transparent 4px),
    radial-gradient(circle at 65% 25%, rgba(255,255,255,1) 3px, transparent 3px),
    radial-gradient(circle at 45% 65%, rgba(255,255,255,1) 4px, transparent 4px);
  animation: prevStarTwinkle 2s ease-in-out infinite;
}

@keyframes prevStarTwinkle {
  0%, 100% { transform: scale(0.7); opacity: 0.4; }
  50% { transform: scale(1.3); opacity: 1; }
}

:global(.effect-bg.effect-glass-bubble)::before {
  content: '';
  position: absolute;
  width: 40px;
  height: 40px;
  background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.95), rgba(200,230,255,0.5));
  border: 1px solid rgba(255,255,255,0.8);
  border-radius: 50%;
  left: 50%;
  bottom: -50px;
  transform: translateX(-50%);
  box-shadow: inset 0 0 15px rgba(255,255,255,0.5);
  animation: prevGlassBubble 4s ease-out infinite;
}

@keyframes prevGlassBubble {
  0% { transform: translateX(-50%) translateY(0); opacity: 0; }
  10% { opacity: 0.9; }
  90% { opacity: 0.9; }
  100% { transform: translateX(-50%) translateY(-350px) scale(1.2); opacity: 0; }
}

:global(.effect-bg.effect-butterfly-fly)::before {
  content: '';
  position: absolute;
  width: 20px;
  height: 16px;
  background: linear-gradient(135deg, #ff6bd6, #ffd93d);
  border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
  left: 50%;
  bottom: -30px;
  transform: translateX(-50%);
  box-shadow: 0 0 10px rgba(255, 107, 214, 0.5);
  animation: prevButterfly 5s ease-in-out infinite;
}

@keyframes prevButterfly {
  0% { transform: translateX(-50%) translateY(0) rotate(-5deg); }
  50% { transform: translateX(-30%) translateY(-150px) rotate(5deg); }
  100% { transform: translateX(-50%) translateY(-300px) rotate(0deg); opacity: 0; }
}

:global(.effect-bg.effect-firefly-glow)::before {
  content: '';
  position: absolute;
  width: 8px;
  height: 8px;
  background: #ffd700;
  border-radius: 50%;
  left: 40%;
  top: 50%;
  box-shadow: 0 0 15px #ffd700, 0 0 30px rgba(255,215,0,0.5);
  animation: prevFirefly 3s ease-in-out infinite;
}

@keyframes prevFirefly {
  0%, 100% { opacity: 0.2; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.3); }
}

:global(.effect-bg.effect-light-beam)::before {
  content: '';
  position: absolute;
  width: 4px;
  height: 150%;
  left: 50%;
  background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(255,215,0,0.5), transparent);
  filter: blur(3px);
  animation: prevBeam 3s ease-in-out infinite;
}

@keyframes prevBeam {
  0%, 100% { opacity: 0.3; transform: scaleY(0.8); }
  50% { opacity: 0.9; transform: scaleY(1.2); }
}

:global(.effect-bg.effect-rainbow-bridge)::before {
  content: '';
  position: absolute;
  width: 200px;
  height: 100px;
  left: 50%;
  top: 50%;
  transform: translateX(-50%);
  border-radius: 200px 200px 0 0;
  background: linear-gradient(180deg,
    rgba(255,0,0,0.4) 0%,
    rgba(255,165,0,0.4) 16%,
    rgba(255,255,0,0.4) 33%,
    rgba(0,128,0,0.4) 50%,
    rgba(0,0,255,0.4) 66%,
    rgba(128,0,128,0.4) 83%,
    transparent 100%);
  animation: prevRainbow 4s ease-in-out infinite;
}

@keyframes prevRainbow {
  0%, 100% { opacity: 0.5; transform: translateX(-50%) scale(0.9); }
  50% { opacity: 0.8; transform: translateX(-50%) scale(1.1); }
}

:global(.effect-bg.effect-heart-smoke)::before {
  content: '♥';
  position: absolute;
  font-size: 3rem;
  color: rgba(255, 100, 150, 0.5);
  left: 50%;
  bottom: -30px;
  transform: translateX(-50%);
  filter: blur(3px);
  animation: prevHeartSmoke 4s ease-out infinite;
}

@keyframes prevHeartSmoke {
  0% { transform: translateX(-50%) translateY(0) scale(0.5); opacity: 0; }
  20% { opacity: 0.6; }
  100% { transform: translateX(-50%) translateY(-300px) scale(1.5); opacity: 0; }
}

:global(.effect-bg.effect-gem-rain)::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(135deg, #ffd700 3px, transparent 3px),
    linear-gradient(225deg, #ff6b6b 3px, transparent 3px),
    linear-gradient(45deg, #4d96ff 3px, transparent 3px);
  background-size: 30px 30px;
  animation: prevGemFall 2s linear infinite;
}

@keyframes prevGemFall {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100%); }
}

:global(.effect-bg.effect-feather-fall)::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(180deg, rgba(255,255,255,0.9) 3px, transparent 3px);
  background-size: 20px 20px;
  animation: prevFeather 5s linear infinite;
}

@keyframes prevFeather {
  0% { transform: translateY(-50px) translateX(0) rotate(0deg); }
  100% { transform: translateY(50px) translateX(30px) rotate(360deg); }
}

:global(.effect-bg.effect-water-ripple)::before {
  content: '';
  position: absolute;
  width: 60px;
  height: 60px;
  border: 2px solid rgba(100,200,255,0.5);
  border-radius: 50%;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  animation: prevRipple 3s ease-out infinite;
}

@keyframes prevRipple {
  0% { transform: translate(-50%, -50%) scale(0.3); opacity: 1; }
  100% { transform: translate(-50%, -50%) scale(2); opacity: 0; }
}

:global(.effect-bg.effect-shooting-star)::before {
  content: '';
  position: absolute;
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, #fff, #ffd700, transparent);
  left: 20%;
  top: 30%;
  animation: prevShootingStar 2s linear infinite;
}

@keyframes prevShootingStar {
  0% { transform: translateX(0) translateY(0); opacity: 1; }
  100% { transform: translateX(100px) translateY(60px); opacity: 0; }
}

:global(.effect-bg.effect-pearl-string)::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 40%, rgba(255,255,255,1) 6px, transparent 6px),
    radial-gradient(circle at 40% 45%, rgba(255,255,255,1) 6px, transparent 6px),
    radial-gradient(circle at 60% 50%, rgba(255,255,255,1) 6px, transparent 6px),
    radial-gradient(circle at 80% 55%, rgba(255,255,255,1) 6px, transparent 6px);
  animation: prevPearl 2s ease-in-out infinite;
}

@keyframes prevPearl {
  0%, 100% { opacity: 0.5; transform: scale(0.9); }
  50% { opacity: 1; transform: scale(1.1); }
}

:global(.effect-bg.effect-gold-leaf)::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(135deg, rgba(255,215,0,0.8) 3px, transparent 3px);
  background-size: 25px 25px;
  animation: prevGoldLeaf 4s linear infinite;
}

@keyframes prevGoldLeaf {
  0% { transform: translateY(-50px) rotate(0deg); opacity: 0.8; }
  100% { transform: translateY(50px) rotate(360deg); opacity: 0.2; }
}

:global(.effect-bg.effect-dream-violet)::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg,
    rgba(138,43,226,0.3),
    rgba(186,85,211,0.25),
    rgba(221,160,221,0.2),
    transparent);
  filter: blur(20px);
  animation: prevViolet 6s ease-in-out infinite;
}

@keyframes prevViolet {
  0%, 100% { transform: translateX(-10%) scaleY(1); opacity: 0.5; }
  50% { transform: translateX(10%) scaleY(1.3); opacity: 0.8; }
}

:global(.effect-bg.effect-radiance-burst)::before {
  content: '';
  position: absolute;
  width: 4px;
  height: 150%;
  left: 50%;
  top: -25%;
  background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(255,215,0,0.6), transparent);
  animation: prevRadiance 2s ease-out infinite;
}

@keyframes prevRadiance {
  0%, 100% { transform: scaleY(0.6); opacity: 0.4; }
  50% { transform: scaleY(1.3); opacity: 1; }
}

:global(.effect-bg.effect-halo-ring)::before {
  content: '';
  position: absolute;
  width: 100px;
  height: 100px;
  border: 3px solid rgba(255,215,0,0.6);
  border-radius: 50%;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  animation: prevHalo 3s ease-in-out infinite;
}

@keyframes prevHalo {
  0%, 100% { transform: translate(-50%, -50%) scale(0.9); opacity: 0.4; }
  50% { transform: translate(-50%, -50%) scale(1.1); opacity: 0.9; }
}

:global(.effect-bg.effect-light-jump)::before {
  content: '';
  position: absolute;
  width: 10px;
  height: 10px;
  background: radial-gradient(circle, #fff, #ffd700);
  border-radius: 50%;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 15px rgba(255,215,0,0.8);
  animation: prevLightJump 1.5s ease-in-out infinite;
}

@keyframes prevLightJump {
  0%, 100% { transform: translate(-50%, -50%) translateY(0) scale(0.8); opacity: 0.3; }
  50% { transform: translate(-50%, -50%) translateY(-20px) scale(1.3); opacity: 1; }
}

:global(.effect-bg.effect-ribbon-fly)::before {
  content: '';
  position: absolute;
  width: 6px;
  height: 150%;
  background: linear-gradient(180deg, #ff6b6b, #ffd93d, #6bcb77, #4d96ff, #ff6bd6);
  left: 30%;
  top: -75%;
  border-radius: 3px;
  animation: prevRibbon 3s linear infinite;
}

@keyframes prevRibbon {
  0% { transform: translateY(0) rotate(0deg); opacity: 0.7; }
  100% { transform: translateY(400px) rotate(360deg); opacity: 0.7; }
}

:global(.effect-bg.effect-lantern-float)::before {
  content: '';
  position: absolute;
  width: 20px;
  height: 28px;
  background: radial-gradient(ellipse, #ff6b6b, #dc143c);
  border-radius: 50%;
  left: 50%;
  bottom: -40px;
  transform: translateX(-50%);
  box-shadow: 0 0 15px rgba(255,100,100,0.6);
  animation: prevLanternFloat 4s ease-in-out infinite;
}

@keyframes prevLanternFloat {
  0%, 100% { transform: translateX(-50%) translateY(0) rotate(-8deg); }
  50% { transform: translateX(-50%) translateY(-150px) rotate(8deg); }
}

:global(.effect-bg.effect-halo-spin)::before {
  content: '';
  position: absolute;
  width: 100px;
  height: 100px;
  border: 4px solid transparent;
  border-top-color: rgba(255,215,0,0.8);
  border-bottom-color: rgba(255,182,193,0.6);
  border-radius: 50%;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  animation: prevHaloSpin 2s linear infinite;
}

@keyframes prevHaloSpin {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

:global(.effect-bg.effect-light-flow)::before {
  content: '';
  position: absolute;
  width: 3px;
  height: 200%;
  left: 40%;
  top: -50%;
  background: linear-gradient(180deg, transparent, rgba(255,255,255,0.7), rgba(255,215,0,0.5), transparent);
  animation: prevLightFlow 3s ease-in-out infinite;
}

@keyframes prevLightFlow {
  0% { transform: translateY(0); opacity: 0; }
  20% { opacity: 1; }
  80% { opacity: 1; }
  100% { transform: translateY(50px); opacity: 0; }
}

:global(.effect-bg.effect-star-blink)::before {
  content: '★ ★ ★ ★ ★';
  position: absolute;
  inset: 0;
  color: #ffd700;
  font-size: 2.5rem;
  display: flex;
  justify-content: space-around;
  padding: 20px;
  text-shadow: 0 0 20px #ffd700, 0 0 40px #ffd700, 0 0 60px #ff8c00;
  animation: prevStarBlink 1.5s ease-in-out infinite;
}

@keyframes prevStarBlink {
  0%, 100% { transform: scale(1); opacity: 1; text-shadow: 0 0 20px #ffd700, 0 0 40px #ffd700; }
  50% { transform: scale(1.3); opacity: 0.6; text-shadow: 0 0 40px #ffd700, 0 0 80px #ffd700; }
}

:global(.effect-bg.effect-halo-pulse)::before {
  content: '';
  position: absolute;
  width: 80px;
  height: 80px;
  border: 2px solid rgba(255,215,0,0.6);
  border-radius: 50%;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  animation: prevHaloPulse 2.5s ease-out infinite;
}

@keyframes prevHaloPulse {
  0% { transform: translate(-50%, -50%) scale(0.5); opacity: 1; }
  100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
}

:global(.effect-bg.effect-confetti-celebrate)::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(45deg, #ff6b6b 2px, transparent 2px),
    linear-gradient(-45deg, #ffd93d 2px, transparent 2px),
    linear-gradient(90deg, #6bcb77 2px, transparent 2px),
    linear-gradient(0deg, #4d96ff 2px, transparent 2px),
    linear-gradient(135deg, #ff6bd6 2px, transparent 2px);
  background-size: 25px 25px;
  animation: prevConfettiCelebrate 2s ease-out infinite;
}

@keyframes prevConfettiCelebrate {
  0% { transform: scale(0); opacity: 1; }
  50% { opacity: 0.8; }
  100% { transform: scale(2); opacity: 0; }
}

:global(.effect-bg.effect-gem-flash)::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 30% 40%, rgba(255,215,0,1) 4px, transparent 4px),
    radial-gradient(circle at 70% 30%, rgba(255,107,107,1) 4px, transparent 4px),
    radial-gradient(circle at 50% 60%, rgba(77,150,255,1) 4px, transparent 4px);
  animation: prevGemFlash 1.5s ease-in-out infinite;
}

@keyframes prevGemFlash {
  0%, 100% { transform: scale(0.5); opacity: 0.2; }
  50% { transform: scale(1.5); opacity: 1; }
}

:global(.effect-bg.effect-phoenix-spread)::before {
  content: '';
  position: absolute;
  width: 200px;
  height: 150px;
  left: 50%;
  top: 40%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, rgba(255,100,50,0.4), rgba(255,200,0,0.3), transparent);
  border-radius: 50%;
  animation: prevPhoenix 4s ease-in-out infinite;
}

@keyframes prevPhoenix {
  0%, 100% { transform: translateX(-50%) scaleX(0.8); opacity: 0.5; }
  50% { transform: translateX(-50%) scaleX(1.2); opacity: 0.9; }
}

:global(.effect-bg.effect-flame-text)::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at center bottom, rgba(255,100,50,0.3), rgba(255,200,0,0.2), transparent 70%);
  animation: prevFlame 2.5s ease-in-out infinite;
}

@keyframes prevFlame {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 0.9; transform: scale(1.1); }
}

:global(.effect-bg.effect-golden-glow)::before {
  content: '';
  position: absolute;
  width: 200%;
  height: 80px;
  left: -50%;
  top: 30%;
  background: linear-gradient(90deg, transparent, rgba(255,215,0,0.5), rgba(255,255,255,0.8), rgba(255,215,0,0.5), transparent);
  animation: prevGoldenGlow 3s ease-in-out infinite;
}

@keyframes prevGoldenGlow {
  0% { transform: translateX(-30%) rotate(-5deg); }
  100% { transform: translateX(30%) rotate(-5deg); }
}

:global(.effect-signature-draw) .preview-card .preview-signature {
  font-family: "Segoe Script", cursive;
  overflow: hidden;
  white-space: nowrap;
  border-right: 2px solid rgba(123, 47, 54, 0.7);
  animation: prevWriteName 2s steps(20, end) forwards;
  max-width: 0;
}

@keyframes prevWriteName {
  from { max-width: 0; }
  to { max-width: 150px; }
}

:global(.effect-bg.effect-seal-fade)::after {
  content: '祝福';
  position: absolute;
  right: 30px;
  bottom: 30px;
  width: 60px;
  height: 60px;
  border: 2px solid rgba(180,44,44,0.5);
  border-radius: 50%;
  color: rgba(180,44,44,0.6);
  display: grid;
  place-items: center;
  font-weight: 900;
  font-size: 0.9rem;
  transform: rotate(-12deg);
  animation: prevStampDrop 3s ease-in-out infinite;
}

@keyframes prevStampDrop {
  0%, 100% { transform: rotate(-12deg) translateY(0); opacity: 0.5; }
  30% { transform: rotate(-9deg) translateY(5px); opacity: 0.9; }
  60% { transform: rotate(-12deg) translateY(0); opacity: 0.6; }
}

:global(.effect-bg.effect-ink-spread)::before {
  content: '';
  position: absolute;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(50,30,30,0.3), transparent);
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  filter: blur(10px);
  animation: prevInkSpread 5s ease-out infinite;
}

@keyframes prevInkSpread {
  0% { transform: translate(-50%, -50%) scale(0.3); opacity: 0; }
  30% { opacity: 0.6; }
  100% { transform: translate(-50%, -50%) scale(2); opacity: 0; }
}

:global(.effect-bg.effect-cloud-float)::before {
  content: '';
  position: absolute;
  width: 120px;
  height: 50px;
  background: rgba(255,255,255,0.6);
  border-radius: 50px;
  left: -30px;
  top: 30px;
  filter: blur(8px);
  animation: prevCloudFloat 8s ease-in-out infinite;
}

@keyframes prevCloudFloat {
  0%, 100% { transform: translateX(0); opacity: 0.5; }
  50% { transform: translateX(300px); opacity: 0.7; }
}

:global(.effect-bg.effect-candle-flicker)::before {
  content: '';
  position: absolute;
  width: 10px;
  height: 30px;
  background: linear-gradient(180deg, rgba(255,200,100,0.9), rgba(255,100,50,0.6), transparent);
  left: 50%;
  top: 20px;
  transform: translateX(-50%);
  border-radius: 50% 50% 0 0;
  animation: prevCandle 0.5s ease-in-out infinite alternate;
  box-shadow: 0 0 20px rgba(255,200,100,0.6), 0 0 40px rgba(255,150,50,0.3);
}

@keyframes prevCandle {
  0% { transform: translateX(-50%) scaleY(0.9) scaleX(0.95); }
  100% { transform: translateX(-50%) scaleY(1.1) scaleX(1.05); }
}

:global(.effect-bg.effect-moon-glow)::before {
  content: '';
  position: absolute;
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, rgba(255,255,240,0.9), rgba(255,255,200,0.4), transparent 70%);
  border-radius: 50%;
  right: 30px;
  top: 20px;
  animation: prevMoon 6s ease-in-out infinite;
}

@keyframes prevMoon {
  0%, 100% { box-shadow: 0 0 30px rgba(255,255,200,0.4); }
  50% { box-shadow: 0 0 60px rgba(255,255,200,0.7); }
}

:global(.effect-bg.effect-silk-drift)::before {
  content: '';
  position: absolute;
  width: 200%;
  height: 80px;
  left: -50%;
  top: 35%;
  background: linear-gradient(90deg, transparent, rgba(255,240,250,0.6), rgba(240,220,255,0.4), transparent);
  filter: blur(8px);
  animation: prevSilkDrift 6s ease-in-out infinite;
}

@keyframes prevSilkDrift {
  0%, 100% { transform: translateX(-30%) rotate(-8deg); opacity: 0.4; }
  50% { transform: translateX(30%) rotate(8deg); opacity: 0.7; }
}

:global(.effect-bg.effect-paper-crane)::before {
  content: '✿';
  position: absolute;
  font-size: 2rem;
  color: rgba(255,255,255,0.7);
  left: 50%;
  bottom: -30px;
  transform: translateX(-50%);
  animation: prevPaperCrane 6s ease-in-out infinite;
}

@keyframes prevPaperCrane {
  0% { transform: translateX(-50%) translateY(0) rotate(-10deg); opacity: 0; }
  20% { opacity: 0.8; }
  80% { opacity: 0.8; }
  100% { transform: translateX(100px) translateY(-350px) rotate(20deg); opacity: 0; }
}

:global(.effect-bg.effect-ribbon-knot)::before {
  content: '';
  position: absolute;
  width: 50px;
  height: 50px;
  border: 3px solid rgba(255,150,180,0.5);
  border-radius: 50%;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  animation: prevRibbonKnot 4s ease-in-out infinite;
}

@keyframes prevRibbonKnot {
  0%, 100% { transform: translate(-50%, -50%) scale(0.9) rotate(0deg); opacity: 0.5; }
  50% { transform: translate(-50%, -50%) scale(1.1) rotate(180deg); opacity: 0.8; }
}

:global(.effect-bg.effect-lotus-bloom)::before {
  content: '❀';
  position: absolute;
  font-size: 3rem;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  color: rgba(255,180,200,0.6);
  animation: prevLotus 5s ease-in-out infinite;
}

@keyframes prevLotus {
  0%, 100% { transform: translate(-50%, -50%) scale(0.5); opacity: 0.3; }
  50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.8; }
}

:global(.effect-bg.effect-cloud-mist)::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 30% 40%, rgba(200,200,220,0.4), transparent 50%),
    radial-gradient(ellipse at 70% 60%, rgba(180,180,200,0.3), transparent 50%);
  filter: blur(15px);
  animation: prevCloudMist 8s ease-in-out infinite;
}

@keyframes prevCloudMist {
  0%, 100% { opacity: 0.4; transform: scaleX(0.95); }
  50% { opacity: 0.7; transform: scaleX(1.05); }
}

:global(.effect-bg.effect-star-wish)::before {
  content: '';
  position: absolute;
  width: 50px;
  height: 2px;
  background: linear-gradient(90deg, #fff, #ffd700, transparent);
  left: 30%;
  top: 30%;
  animation: prevStarWish 3s linear infinite;
}

@keyframes prevStarWish {
  0% { transform: translateX(0) translateY(0); opacity: 1; }
  100% { transform: translateX(80px) translateY(50px); opacity: 0; }
}

:global(.effect-letter-unfold) .preview-card {
  perspective: 500px;
}
:global(.effect-bg.effect-letter-unfold)::before {
  content: '';
  position: absolute;
  width: 60%;
  height: 50%;
  left: 20%;
  top: 25%;
  background: rgba(255,255,255,0.9);
  border-radius: 8px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
  transform-origin: bottom center;
  animation: prevLetterOpen 4s ease-in-out infinite;
}

@keyframes prevLetterOpen {
  0%, 100% { transform: rotateX(0deg); opacity: 0.8; }
  50% { transform: rotateX(-20deg); opacity: 1; }
}

:global(.effect-bg.effect-stardust)::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 30%, rgba(255,255,255,1) 3px, transparent 3px),
    radial-gradient(circle at 60% 20%, rgba(255,255,255,1) 2px, transparent 2px),
    radial-gradient(circle at 80% 50%, rgba(255,255,255,1) 3px, transparent 3px),
    radial-gradient(circle at 40% 70%, rgba(255,255,255,1) 2px, transparent 2px),
    radial-gradient(circle at 70% 80%, rgba(255,255,255,1) 3px, transparent 3px);
  animation: prevStardust 3s linear infinite;
}

@keyframes prevStardust {
  0% { transform: translateY(0); }
  100% { transform: translateY(-30px); }
}

:global(.effect-bg.effect-festival-bokeh)::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 25% 35%, rgba(255,200,150,0.5) 15px, transparent 15px),
    radial-gradient(circle at 70% 25%, rgba(255,180,200,0.4) 20px, transparent 20px),
    radial-gradient(circle at 50% 65%, rgba(200,220,255,0.3) 25px, transparent 25px);
  animation: prevBokeh 4s ease-in-out infinite;
}

@keyframes prevBokeh {
  0%, 100% { opacity: 0.4; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.05); }
}

:global(.effect-card-highlight) .effect-bg { position: absolute; inset: 0; z-index: 1; pointer-events: none; overflow: hidden; } .preview-card {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1), 0 0 30px rgba(255, 215, 0, 0.3);
}

:global(.effect-bg.effect-afterglow)::after {
  content: '';
  position: absolute;
  inset: auto 20% 20% 20%;
  height: 60px;
  background: radial-gradient(ellipse, rgba(255,200,150,0.4), transparent 70%);
  filter: blur(15px);
  animation: prevAfterglow 4s ease-in-out infinite;
}

@keyframes prevAfterglow {
  0%, 100% { opacity: 0.3; transform: scaleX(0.95); }
  50% { opacity: 0.6; transform: scaleX(1.05); }
}
</style>
