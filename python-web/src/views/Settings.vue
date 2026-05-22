<template>
  <div class="page">
    <NavBar />
    <div class="content">
      <div class="page-header">
        <h1 class="page-title">系统设置</h1>
      </div>

      <div class="layout">
        <div class="card sidebar-nav">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="sidebar-tab"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            <svg v-html="tab.icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></svg>
            <span>{{ tab.label }}</span>
          </button>
        </div>

        <div class="tab-content-area">
          <div v-if="activeTab === 'preference'" class="card">
            <h3 class="section-title">个人偏好</h3>
            <div class="form-group">
              <label class="form-label">主题设置</label>
              <div class="theme-toggle">
                <div class="theme-option" :class="{ active: !isDark }" @click="isDark = false">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
                  <span>浅色</span>
                </div>
                <div class="theme-option" :class="{ active: isDark }" @click="isDark = true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
                  <span>深色</span>
                </div>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">默认导出路径</label>
              <input v-model="prefExportPath" class="input" placeholder="/data/exports/" />
            </div>
            <div class="form-group">
              <label class="form-label">语言</label>
              <select v-model="prefLang" class="input input-select">
                <option value="zh-CN">简体中文</option>
                <option value="en">English</option>
                <option value="ja">日本語</option>
              </select>
            </div>
            <button class="btn-save" @click="savePreference">保存偏好设置</button>
          </div>

          <div v-if="activeTab === 'notification'" class="card">
            <h3 class="section-title">通知设置</h3>
            <div class="notif-section">
              <h4 class="notif-subtitle">告警通知</h4>
              <div class="toggle-list">
                <label class="toggle-item">
                  <span>任务失败</span>
                  <input type="checkbox" v-model="notifTaskFail" />
                </label>
                <label class="toggle-item">
                  <span>任务超时</span>
                  <input type="checkbox" v-model="notifTimeout" />
                </label>
                <label class="toggle-item">
                  <span>数据异常</span>
                  <input type="checkbox" v-model="notifDataError" />
                </label>
                <label class="toggle-item">
                  <span>IP被封</span>
                  <input type="checkbox" v-model="notifIpBlocked" />
                </label>
              </div>
            </div>
            <div class="notif-section">
              <h4 class="notif-subtitle">通知方式</h4>
              <div class="toggle-list">
                <label class="toggle-item">
                  <span>系统通知</span>
                  <input type="checkbox" v-model="notifSystem" />
                </label>
                <label class="toggle-item">
                  <span>邮件通知</span>
                  <input type="checkbox" v-model="notifEmail" />
                </label>
                <label class="toggle-item">
                  <span>企业微信</span>
                  <input type="checkbox" v-model="notifWechat" />
                </label>
              </div>
            </div>
            <button class="btn-save" @click="saveNotification">保存通知设置</button>
          </div>

          <div v-if="activeTab === 'global'" class="card">
            <h3 class="section-title">全局配置</h3>
            <div class="form-group">
              <label class="form-label">日志保留天数</label>
              <input v-model.number="globalLogDays" type="number" class="input" min="1" max="365" />
            </div>
            <div class="form-group">
              <label class="form-label">代理刷新间隔（分钟）</label>
              <input v-model.number="globalProxyRefresh" type="number" class="input" min="1" max="1440" />
            </div>
            <div class="form-group">
              <label class="form-label">默认请求间隔（毫秒）</label>
              <input v-model.number="globalReqInterval" type="number" class="input" min="100" max="10000" />
            </div>
            <div class="form-group">
              <label class="form-label">默认并发数</label>
              <input v-model.number="globalConcurrency" type="number" class="input" min="1" max="100" />
            </div>
            <button class="btn-save" @click="saveGlobal">保存全局配置</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { systemAPI } from '../api/system'
import NavBar from '../components/NavBar.vue'

const activeTab = ref('preference')

const tabs = [
  { key: 'preference', label: '个人偏好', icon: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>' },
  { key: 'notification', label: '通知设置', icon: '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>' },
  { key: 'global', label: '全局配置', icon: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>' }
]

const isDark = ref(true)
const prefExportPath = ref('/data/exports')
const prefLang = ref('zh-CN')

const notifTaskFail = ref(true)
const notifTimeout = ref(true)
const notifDataError = ref(true)
const notifIpBlocked = ref(true)
const notifSystem = ref(true)
const notifEmail = ref(false)
const notifWechat = ref(false)

const globalLogDays = ref(30)
const globalProxyRefresh = ref(60)
const globalReqInterval = ref(2000)
const globalConcurrency = ref(5)

async function savePreference() {
  try {
    await systemAPI.saveUserPreferences({
      theme: isDark.value ? 'dark' : 'light',
      export_path: prefExportPath.value,
      language: prefLang.value
    })
    ElMessage.success('个人偏好已保存')
  } catch (error) {
    ElMessage.error('保存偏好失败')
  }
}

async function saveNotification() {
  try {
    await systemAPI.saveUserPreferences({
      notif_task_fail: notifTaskFail.value,
      notif_timeout: notifTimeout.value,
      notif_data_error: notifDataError.value,
      notif_ip_blocked: notifIpBlocked.value,
      notif_system: notifSystem.value,
      notif_email: notifEmail.value,
      notif_wechat: notifWechat.value
    })
    ElMessage.success('通知设置已保存')
  } catch (error) {
    ElMessage.error('保存通知设置失败')
  }
}

async function saveGlobal() {
  try {
    await systemAPI.updateSetting('log_retention_days', { value: globalLogDays.value })
    await systemAPI.updateSetting('proxy_refresh_interval', { value: globalProxyRefresh.value })
    await systemAPI.updateSetting('default_request_interval', { value: globalReqInterval.value })
    await systemAPI.updateSetting('default_concurrency', { value: globalConcurrency.value })
    ElMessage.success('全局配置已保存')
  } catch (error) {
    ElMessage.error('保存全局配置失败')
  }
}

async function loadSettings() {
  try {
    const res = await systemAPI.getSettings()
    if (res.data.success) {
      const settings = res.data.data || {}
      if (settings.log_retention_days) globalLogDays.value = settings.log_retention_days
      if (settings.proxy_refresh_interval) globalProxyRefresh.value = settings.proxy_refresh_interval
      if (settings.default_request_interval) globalReqInterval.value = settings.default_request_interval
      if (settings.default_concurrency) globalConcurrency.value = settings.default_concurrency
    }
  } catch (error) {
    // 静默处理
  }
}

async function loadPreferences() {
  try {
    const res = await systemAPI.getUserPreferences()
    if (res.data.success) {
      const prefs = res.data.data || {}
      if (prefs.theme) isDark.value = prefs.theme === 'dark'
      if (prefs.export_path) prefExportPath.value = prefs.export_path
      if (prefs.language) prefLang.value = prefs.language
      if (prefs.notif_task_fail !== undefined) notifTaskFail.value = prefs.notif_task_fail
      if (prefs.notif_timeout !== undefined) notifTimeout.value = prefs.notif_timeout
      if (prefs.notif_data_error !== undefined) notifDataError.value = prefs.notif_data_error
      if (prefs.notif_ip_blocked !== undefined) notifIpBlocked.value = prefs.notif_ip_blocked
      if (prefs.notif_system !== undefined) notifSystem.value = prefs.notif_system
      if (prefs.notif_email !== undefined) notifEmail.value = prefs.notif_email
      if (prefs.notif_wechat !== undefined) notifWechat.value = prefs.notif_wechat
    }
  } catch (error) {
    // 静默处理
  }
}

onMounted(() => {
  loadSettings()
  loadPreferences()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background-color: #0d1117;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px);
  background-size: 40px 40px;
}
.page::before {
  content: '';
  position: fixed; top: 0; left: 0;
  width: 100%; height: 100%;
  background:
    radial-gradient(ellipse 80% 60% at 50% -20%, rgba(76, 110, 245, 0.06), transparent),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(124, 58, 237, 0.04), transparent);
  pointer-events: none; z-index: 0;
}
.content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 24px 80px;
  position: relative; z-index: 1;
}
.page-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px;
}
.page-title {
  font-size: 26px; font-weight: 700;
  color: rgba(255, 255, 255, 0.9); letter-spacing: -0.5px;
}
.layout { display: grid; grid-template-columns: 220px 1fr; gap: 20px; align-items: start; }
.card {
  background: rgba(22, 27, 34, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 24px;
}
.sidebar-nav { padding: 8px; }
.sidebar-tab {
  display: flex; align-items: center; gap: 10px;
  width: 100%; padding: 11px 16px; font-size: 13px; font-weight: 500;
  color: rgba(255,255,255,0.4); background: transparent; border: none;
  border-radius: 10px; cursor: pointer; transition: all 0.2s ease;
  text-align: left;
}
.sidebar-tab:hover { color: rgba(255,255,255,0.65); background: rgba(255,255,255,0.03); }
.sidebar-tab.active { background: rgba(76,110,245,0.1); color: #7c8aff; font-weight: 600; }
.sidebar-tab svg { width: 18px; height: 18px; flex-shrink: 0; }
.tab-content-area { animation: fadeIn 0.25s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateX(6px); } to { opacity: 1; transform: translateX(0); } }
.section-title { font-size: 16px; font-weight: 700; color: rgba(255,255,255,0.8); margin-bottom: 24px; }
.form-group { margin-bottom: 20px; }
.form-label { display: block; font-size: 12px; font-weight: 500; color: rgba(255,255,255,0.35); margin-bottom: 6px; }
.input {
  width: 100%; padding: 10px 14px; font-size: 13px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px; color: rgba(255, 255, 255, 0.75);
  outline: none; transition: all 0.2s ease; box-sizing: border-box;
}
.input:focus { border-color: rgba(76, 110, 245, 0.4); background: rgba(255, 255, 255, 0.06); }
.input-select { cursor: pointer; color-scheme: dark; }
.theme-toggle { display: flex; gap: 10px; }
.theme-option {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px;
  padding: 16px; background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06); border-radius: 12px;
  cursor: pointer; transition: all 0.2s ease; color: rgba(255,255,255,0.35);
}
.theme-option:hover { border-color: rgba(76,110,245,0.2); }
.theme-option.active { background: rgba(76,110,245,0.1); border-color: rgba(76,110,245,0.3); color: #7c8aff; }
.theme-option svg { width: 24px; height: 24px; }
.theme-option span { font-size: 12px; font-weight: 600; }
.notif-section { margin-bottom: 24px; }
.notif-subtitle { font-size: 13px; font-weight: 600; color: rgba(255,255,255,0.5); margin-bottom: 12px; }
.toggle-list { display: flex; flex-direction: column; gap: 4px; }
.toggle-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 11px 16px; background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.04); border-radius: 10px;
  font-size: 13px; color: rgba(255,255,255,0.55); cursor: pointer;
  transition: all 0.15s ease;
}
.toggle-item:hover { background: rgba(255,255,255,0.04); }
.toggle-item input { accent-color: #4c6ef5; width: 18px; height: 18px; }
.btn-save {
  padding: 11px 28px; font-size: 13px; font-weight: 600;
  background: linear-gradient(135deg, #4c6ef5, #7c3aed);
  border: none; border-radius: 10px; color: #fff; cursor: pointer;
  transition: all 0.25s ease; margin-top: 8px;
  box-shadow: 0 2px 12px rgba(76, 110, 245, 0.3);
}
.btn-save:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(76, 110, 245, 0.45); }

@media (max-width: 768px) {
  .content { padding: 24px 16px 64px; }
  .page-title { font-size: 22px; }
  .layout { grid-template-columns: 1fr; }
  .sidebar-nav { display: flex; gap: 4px; padding: 4px; }
  .sidebar-tab { width: auto; }
}
@media (max-width: 560px) {
  .theme-toggle { flex-direction: column; }
  .sidebar-tab span { display: none; }
}
</style>