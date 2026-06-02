<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useBlessingStore } from '@/stores/blessing'
import { getSettings, refreshNearestFestival, updateSettings } from '@/utils/api'

const router = useRouter()
const store = useBlessingStore()

const globalMode = ref('birthday')
const birthdayText = ref('')
const festivalText = ref('')
const currentFestival = ref('')
const updateTime = ref('')
const saving = ref(false)
const refreshing = ref(false)

onMounted(async () => {
  store.restoreUser()
  if (store.role !== 'admin') {
    router.push('/login')
    return
  }
  await loadSettings()
})

async function loadSettings() {
  try {
    const res: any = await getSettings()
    if (res.code === 200) {
      const data = res.data
      globalMode.value = data.global_mode
      birthdayText.value = data.birthday_default_text
      festivalText.value = data.festival_default_text
      currentFestival.value = data.current_nearest_festival
      updateTime.value = data.update_time
      store.setSettings(data.global_mode, data.current_nearest_festival, data.birthday_default_text, data.festival_default_text, data.update_time, data.content_steps || [])
    }
  } catch {
    showToast('加载配置失败')
  }
}

async function handleSave() {
  saving.value = true
  try {
    const res: any = await updateSettings({
      global_mode: globalMode.value,
      birthday_default_text: birthdayText.value,
      festival_default_text: festivalText.value,
    })
    if (res.code === 200) {
      showToast('全局配置已保存')
      await loadSettings()
    } else {
      showToast(res.msg || '保存失败')
    }
  } catch {
    showToast('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

async function handleRefreshFestival() {
  refreshing.value = true
  try {
    const res: any = await refreshNearestFestival()
    if (res.code === 200) {
      currentFestival.value = res.data.festival_name
      festivalText.value = res.data.festival_text || festivalText.value
      showToast('最近节日已刷新')
      await loadSettings()
    } else {
      showToast(res.msg || '刷新失败')
    }
  } catch {
    showToast('刷新失败，请重试')
  } finally {
    refreshing.value = false
  }
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
  <div class="admin-page">
    <header class="admin-header">
      <div>
        <p class="eyebrow">Admin Console</p>
        <h1 class="admin-title">祝福后台</h1>
      </div>
      <button class="btn-secondary" @click="goBack">退出</button>
    </header>

    <main class="admin-content">
      <section class="panel">
        <h2 class="section-title">全局模式锁定</h2>
        <div class="mode-switch">
          <button class="mode-btn" :class="{ active: globalMode === 'birthday' }" @click="globalMode = 'birthday'">生日模式</button>
          <button class="mode-btn" :class="{ active: globalMode === 'festival' }" @click="globalMode = 'festival'">节日模式</button>
        </div>
        <div v-if="globalMode === 'festival'" class="festival-line">
          <div>
            <p class="festival-name">{{ currentFestival || '未匹配节日' }}</p>
            <p class="festival-time" v-if="updateTime">更新时间：{{ updateTime }}</p>
          </div>
          <button class="btn-small" :disabled="refreshing" @click="handleRefreshFestival">
            {{ refreshing ? '刷新中' : '刷新最近节日' }}
          </button>
        </div>
        <button class="btn-primary wide" :disabled="saving" @click="handleSave">
          {{ saving ? '保存中' : '保存全局模式' }}
        </button>
      </section>

      <section class="nav-grid">
        <button class="nav-tile theme" @click="router.push('/admin/theme')">
          <span class="tile-title">主题模板管理</span>
          <span class="tile-desc">批量维护成套配色，账号只能选择模板</span>
        </button>
        <button class="nav-tile content" @click="router.push('/admin/content')">
          <span class="tile-title">分步文案配置</span>
          <span class="tile-desc">生日和节日两套四步文案独立维护</span>
        </button>
        <button class="nav-tile effect" @click="router.push('/admin/effect')">
          <span class="tile-title">特效方案管理</span>
          <span class="tile-desc">配置四个步骤的动态元素组合，并分配给账号</span>
        </button>
        <button class="nav-tile user" @click="router.push('/admin/user')">
          <span class="tile-title">账号管理</span>
          <span class="tile-desc">为账号同时分配主题模板和特效方案</span>
        </button>
      </section>
    </main>
  </div>
</template>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: #f6f2ea;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  background: #fffdf8;
  border-bottom: 1px solid #e9dfd1;
  position: sticky;
  top: 0;
  z-index: 10;
}

.eyebrow {
  color: #8b735b;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
}

.admin-title {
  color: #2e2a24;
  font-size: 1.25rem;
  font-weight: 800;
}

.admin-content {
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.panel {
  background: #fffdf8;
  border: 1px solid #eadfce;
  border-radius: 8px;
  padding: 18px;
  box-shadow: 0 10px 24px rgba(55, 43, 28, 0.06);
}

.section-title {
  color: #2e2a24;
  font-size: 1rem;
  font-weight: 800;
  margin-bottom: 14px;
}

.mode-switch {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.mode-btn {
  border: 1px solid #dfd2be;
  border-radius: 8px;
  background: #ffffff;
  color: #685847;
  min-height: 50px;
  font-weight: 700;
  cursor: pointer;
}

.mode-btn.active {
  color: #ffffff;
  background: #2f6f73;
  border-color: #2f6f73;
}

.festival-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 0 4px;
}

.festival-name {
  font-weight: 800;
  color: #b55738;
}

.festival-time {
  color: #9b8a78;
  font-size: 0.75rem;
  margin-top: 3px;
}

.wide {
  width: 100%;
  margin-top: 16px;
}

.nav-grid {
  display: grid;
  gap: 12px;
}

.nav-tile {
  text-align: left;
  border: 1px solid transparent;
  border-radius: 8px;
  padding: 18px;
  min-height: 112px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.tile-title {
  font-size: 1.05rem;
  font-weight: 900;
}

.tile-desc {
  font-size: 0.82rem;
  line-height: 1.5;
}

.theme {
  background: #f7dfe6;
  color: #75334a;
}

.content {
  background: #dfeefa;
  color: #25516f;
}

.effect {
  background: #efe2fb;
  color: #5c3f83;
}

.user {
  background: #e8efd9;
  color: #465f30;
}
</style>
