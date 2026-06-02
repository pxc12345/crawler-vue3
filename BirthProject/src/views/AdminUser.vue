<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useBlessingStore } from '@/stores/blessing'
import { deleteUser, getEffectProfiles, getThemeList, getUserList, saveUser } from '@/utils/api'

interface ThemeItem {
  id: number
  name: string
  category: string
  background_color: string
  title_color: string
  body_color: string
  button_color: string
  card_color: string
}

interface EffectProfile {
  id: number
  name: string
  welcome_effects: string[]
  intro_effects: string[]
  main_effects: string[]
  closing_effects: string[]
  particle_density: number
  motion_level: number
  glow_intensity: number
}

interface UserItem {
  id: number
  username: string
  theme_id: number | null
  effect_profile_id: number | null
  create_time: string
  theme: ThemeItem
  effect_profile: EffectProfile
}

const router = useRouter()
const store = useBlessingStore()

const users = ref<UserItem[]>([])
const themes = ref<ThemeItem[]>([])
const effectProfiles = ref<EffectProfile[]>([])
const loading = ref(true)
const showModal = ref(false)
const editMode = ref(false)
const editId = ref<number | null>(null)
const formUsername = ref('')
const formThemeId = ref<number | null>(null)
const formEffectProfileId = ref<number | null>(null)
const saving = ref(false)
const showDeleteConfirm = ref(false)
const deleteTarget = ref<UserItem | null>(null)

const selectedTheme = computed(() => themes.value.find((item) => item.id === formThemeId.value) || themes.value[0])
const selectedEffectProfile = computed(() => effectProfiles.value.find((item) => item.id === formEffectProfileId.value) || effectProfiles.value[0])
const groupedThemes = computed(() => {
  const groups = new Map<string, ThemeItem[]>()
  themes.value.forEach((theme) => {
    if (!groups.has(theme.category)) groups.set(theme.category, [])
    groups.get(theme.category)!.push(theme)
  })
  return Array.from(groups.entries()).map(([category, items]) => ({ category, items }))
})

onMounted(async () => {
  store.restoreUser()
  if (store.role !== 'admin') {
    router.push('/login')
    return
  }
  await Promise.all([loadThemes(), loadEffects(), loadUsers()])
})

async function loadThemes() {
  try {
    const res: any = await getThemeList()
    if (res.code === 200) themes.value = res.data || []
  } catch {
    showToast('加载主题失败')
  }
}

async function loadEffects() {
  try {
    const res: any = await getEffectProfiles()
    if (res.code === 200) effectProfiles.value = res.data || []
  } catch {
    showToast('加载特效方案失败')
  }
}

async function loadUsers() {
  loading.value = true
  try {
    const res: any = await getUserList()
    if (res.code === 200) users.value = res.data || []
  } catch {
    showToast('加载账号列表失败')
  } finally {
    loading.value = false
  }
}

function openAdd() {
  editMode.value = false
  editId.value = null
  formUsername.value = ''
  formThemeId.value = themes.value[0]?.id || null
  formEffectProfileId.value = effectProfiles.value[0]?.id || null
  showModal.value = true
}

function openEdit(user: UserItem) {
  editMode.value = true
  editId.value = user.id
  formUsername.value = user.username
  formThemeId.value = user.theme_id || user.theme?.id || themes.value[0]?.id || null
  formEffectProfileId.value = user.effect_profile_id || user.effect_profile?.id || effectProfiles.value[0]?.id || null
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

async function handleSave() {
  const username = formUsername.value.trim()
  if (!username) {
    showToast('请输入账号名')
    return
  }
  if (!formThemeId.value) {
    showToast('请选择主题')
    return
  }
  if (!formEffectProfileId.value) {
    showToast('请选择特效方案')
    return
  }

  saving.value = true
  try {
    const payload: any = {
      username,
      theme_id: formThemeId.value,
      effect_profile_id: formEffectProfileId.value,
    }
    if (editMode.value && editId.value) payload.id = editId.value
    const res: any = await saveUser(payload)
    if (res.code === 200) {
      showToast(editMode.value ? '账号已更新' : '账号已创建')
      closeModal()
      await loadUsers()
    } else {
      showToast(res.msg || '保存失败')
    }
  } catch {
    showToast('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

function confirmDelete(user: UserItem) {
  deleteTarget.value = user
  showDeleteConfirm.value = true
}

async function handleDelete() {
  if (!deleteTarget.value) return
  try {
    const res: any = await deleteUser(deleteTarget.value.id)
    if (res.code === 200) {
      showToast('账号已删除')
      showDeleteConfirm.value = false
      deleteTarget.value = null
      await loadUsers()
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
  <div class="user-page">
    <header class="user-header">
      <button class="btn-secondary" @click="router.push('/admin')">返回</button>
      <div class="header-copy">
        <p class="header-eyebrow">Account Mapping</p>
        <h1 class="user-title">账号管理</h1>
      </div>
      <button class="btn-small" @click="openAdd">新增</button>
    </header>

    <main class="user-content">
      <section class="intro-panel">
        <h2>账号同时绑定主题和特效方案</h2>
        <p>现在 admin 可以决定一个账号看起来是什么气质，也可以决定它四步页面出现什么动态效果。</p>
      </section>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="users.length === 0" class="empty-state">
        <p class="empty-text">暂无账号，先新增一个专属账号。</p>
      </div>

      <div v-else class="user-list">
        <article v-for="user in users" :key="user.id" class="user-card">
          <div class="user-info">
            <div class="user-avatar" :style="{ backgroundColor: user.theme?.background_color, color: user.theme?.title_color }">
              {{ user.username.charAt(0).toUpperCase() }}
            </div>
            <div class="user-detail">
              <p class="user-name">{{ user.username }}</p>
              <p class="theme-name">{{ user.theme?.category }} / {{ user.theme?.name }}</p>
              <p class="effect-name">特效：{{ user.effect_profile?.name || '未选择' }}</p>
              <div class="color-dots" v-if="user.theme">
                <span v-for="color in [user.theme.background_color, user.theme.title_color, user.theme.body_color, user.theme.button_color, user.theme.card_color]" :key="color" class="color-dot" :style="{ backgroundColor: color }"></span>
              </div>
            </div>
          </div>
          <div class="user-actions">
            <button class="btn-small" @click="openEdit(user)">编辑</button>
            <button class="btn-danger" @click="confirmDelete(user)">删除</button>
          </div>
        </article>
      </div>
    </main>

    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h3 class="modal-title">{{ editMode ? '编辑账号' : '新增账号' }}</h3>
        <div class="form-group">
          <label class="form-label">账号名</label>
          <input v-model="formUsername" class="input-field" type="text" placeholder="请输入账号名" maxlength="30" :disabled="editMode" />
        </div>

        <div class="form-group">
          <label class="form-label">主题模板</label>
          <select v-model.number="formThemeId" class="input-field">
            <optgroup v-for="group in groupedThemes" :key="group.category" :label="group.category">
              <option v-for="theme in group.items" :key="theme.id" :value="theme.id">{{ theme.name }}</option>
            </optgroup>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">特效方案</label>
          <select v-model.number="formEffectProfileId" class="input-field">
            <option v-for="profile in effectProfiles" :key="profile.id" :value="profile.id">{{ profile.name }}</option>
          </select>
        </div>

        <div v-if="selectedTheme" class="theme-preview" :style="{ backgroundColor: selectedTheme.background_color, color: selectedTheme.body_color }">
          <div class="preview-card" :style="{ backgroundColor: selectedTheme.card_color }">
            <p class="preview-category">{{ selectedTheme.category }}</p>
            <h4 :style="{ color: selectedTheme.title_color }">{{ selectedTheme.name }}</h4>
            <p>当前主题决定页面的整体气质。</p>
            <div class="preview-swatches">
              <span v-for="color in [selectedTheme.background_color, selectedTheme.title_color, selectedTheme.body_color, selectedTheme.button_color, selectedTheme.card_color]" :key="color" :style="{ backgroundColor: color }"></span>
            </div>
            <p class="effect-preview" v-if="selectedEffectProfile">当前特效方案：{{ selectedEffectProfile.name }}</p>
            <p class="effect-tags" v-if="selectedEffectProfile">{{ selectedEffectProfile.welcome_effects.join(' / ') }} | {{ selectedEffectProfile.main_effects.join(' / ') }}</p>
            <button :style="{ backgroundColor: selectedTheme.button_color }">进入祝福</button>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="closeModal">取消</button>
          <button class="btn-primary" :disabled="saving" @click="handleSave">
            {{ saving ? '保存中' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="showDeleteConfirm = false">
      <div class="modal-content">
        <h3 class="modal-title">确认删除</h3>
        <p class="confirm-text">确定删除账号「{{ deleteTarget?.username }}」吗？</p>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showDeleteConfirm = false">取消</button>
          <button class="btn-danger" @click="handleDelete">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.user-page {
  min-height: 100vh;
  background: radial-gradient(circle at top left, rgba(210, 130, 92, 0.12), transparent 24%), linear-gradient(180deg, #f8f3eb 0%, #efe7dc 100%);
}

.user-header {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 12px;
  padding: 18px;
  background: rgba(255, 250, 244, 0.9);
  backdrop-filter: blur(18px);
  border-bottom: 1px solid rgba(124, 97, 70, 0.12);
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-eyebrow,
.preview-category {
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #9f7857;
}

.user-title,
.intro-panel h2 {
  color: #2f2721;
  font-weight: 900;
}

.user-title {
  font-size: 1.12rem;
}

.user-content {
  padding: 18px;
}

.intro-panel,
.user-card {
  border-radius: 20px;
  border: 1px solid rgba(121, 94, 68, 0.12);
  background: rgba(255, 251, 246, 0.88);
  box-shadow: 0 18px 40px rgba(77, 58, 39, 0.08);
}

.intro-panel {
  padding: 18px;
  margin-bottom: 16px;
}

.intro-panel p,
.theme-name,
.effect-name,
.empty-state,
.loading-state,
.confirm-text {
  color: #6a5849;
  line-height: 1.7;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 52px 0;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(0, 0, 0, 0.08);
  border-top-color: #2f6f73;
  border-radius: 50%;
  margin: 0 auto 12px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.user-list {
  display: grid;
  gap: 12px;
}

.user-card {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.user-info {
  display: flex;
  gap: 12px;
  min-width: 0;
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  font-weight: 900;
  flex-shrink: 0;
}

.user-name {
  color: #2f2721;
  font-weight: 900;
}

.theme-name,
.effect-name {
  font-size: 0.8rem;
  margin-top: 3px;
}

.color-dots,
.preview-swatches {
  display: flex;
  gap: 7px;
  margin-top: 8px;
}

.color-dot,
.preview-swatches span {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.12);
}

.user-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.theme-preview {
  border-radius: 18px;
  padding: 12px;
}

.preview-card {
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 16px 28px rgba(52, 37, 28, 0.1);
}

.preview-card h4 {
  font-size: 1.12rem;
  margin: 6px 0 8px;
}

.preview-card p {
  line-height: 1.7;
}

.effect-preview,
.effect-tags {
  color: #5d4a3f;
  font-size: 0.78rem;
  margin-top: 10px;
}

.preview-card button {
  border: 0;
  color: #fff;
  border-radius: 14px;
  padding: 10px 16px;
  margin-top: 14px;
  font-weight: 800;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 18px;
}
</style>
