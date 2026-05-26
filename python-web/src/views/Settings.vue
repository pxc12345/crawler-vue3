<template>
  <div class="page">
    <NavBar />
    <div class="content">
      <div class="page-header">
        <h1 class="page-title">系统设置</h1>
        <p class="page-sub">管理你的账户、安全与个性化偏好</p>
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
          <!-- ========== 个人资料 ========== -->
          <div v-if="activeTab === 'profile'" class="card section-card">
            <h3 class="section-title">个人资料</h3>
            <div class="form-group">
              <label class="form-label">用户名</label>
              <input class="input" :value="profileData.username" disabled />
            </div>
            <div class="form-group">
              <label class="form-label">昵称</label>
              <input v-model="profileData.nickname" class="input" placeholder="请输入昵称" />
            </div>
            <div class="form-group">
              <label class="form-label">头像URL</label>
              <input v-model="profileData.avatar_url" class="input" placeholder="https://example.com/avatar.jpg" />
            </div>
            <div class="form-group">
              <label class="form-label">个人简介</label>
              <textarea v-model="profileData.bio" class="input input-textarea" rows="3" placeholder="介绍一下自己..."></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">邮箱</label>
              <input class="input" :value="profileData.email || '未绑定'" disabled />
            </div>
            <div class="form-group">
              <label class="form-label">手机号</label>
              <input class="input" :value="profileData.phone || '未绑定'" disabled />
            </div>
            <button class="btn-save" :disabled="profileSaving" @click="saveProfile">
              {{ profileSaving ? '保存中...' : '保存个人资料' }}
            </button>
          </div>

          <!-- ========== 账号安全 ========== -->
          <div v-if="activeTab === 'security'" class="card section-card">
            <h3 class="section-title">账号安全</h3>
            <div class="form-group">
              <label class="form-label">原密码</label>
              <input v-model="pwdData.old_password" type="password" class="input" placeholder="请输入当前密码" />
            </div>
            <div class="form-group">
              <label class="form-label">新密码</label>
              <input v-model="pwdData.new_password" type="password" class="input" placeholder="请输入新密码（至少6位）" />
            </div>
            <div class="form-group">
              <label class="form-label">确认新密码</label>
              <input v-model="pwdData.confirm_password" type="password" class="input" placeholder="请再次输入新密码" />
            </div>
            <button class="btn-save" :disabled="pwdSaving" @click="savePassword">
              {{ pwdSaving ? '修改中...' : '修改密码' }}
            </button>
          </div>

          <!-- ========== 系统通用 ========== -->
          <div v-if="activeTab === 'system'" class="card section-card">
            <h3 class="section-title">系统通用设置</h3>
            <div class="form-group">
              <label class="form-label">网站标题</label>
              <input v-model="sysSettings.site_title" class="input" placeholder="CrawlMaster" />
            </div>
            <div class="form-group">
              <label class="form-label">网站Logo</label>
              <input v-model="sysSettings.site_logo" class="input" placeholder="Logo URL或文字" />
            </div>
            <div class="toggle-list">
              <label class="toggle-item">
                <span>页面动画效果</span>
                <input type="checkbox" v-model="sysSettings.animation_enabled" />
              </label>
              <label class="toggle-item">
                <span>面包屑导航</span>
                <input type="checkbox" v-model="sysSettings.breadcrumb_enabled" />
              </label>
              <label class="toggle-item">
                <span>侧边栏默认折叠</span>
                <input type="checkbox" v-model="sysSettings.sidebar_collapsed" />
              </label>
            </div>
            <h4 class="notif-subtitle" style="margin-top: 24px;">消息通知</h4>
            <div class="toggle-list">
              <label class="toggle-item">
                <span>任务告警通知</span>
                <input type="checkbox" v-model="sysSettings.notif_alerts" />
              </label>
              <label class="toggle-item">
                <span>系统消息通知</span>
                <input type="checkbox" v-model="sysSettings.notif_system" />
              </label>
            </div>
            <button class="btn-save" :disabled="sysSaving" @click="saveSystemSettings">
              {{ sysSaving ? '保存中...' : '保存通用设置' }}
            </button>
          </div>

          <!-- ========== 爬虫业务 ========== -->
          <div v-if="activeTab === 'crawler'" class="card section-card">
            <h3 class="section-title">爬虫业务设置</h3>
            <p class="section-desc">这些全局配置将影响所有爬虫任务的默认运行行为</p>
            <div class="form-group">
              <label class="form-label">默认请求间隔（毫秒）</label>
              <input v-model.number="crawlerConfig.default_request_interval" type="number" class="input" min="100" max="60000" />
            </div>
            <div class="form-group">
              <label class="form-label">默认并发数</label>
              <input v-model.number="crawlerConfig.default_concurrency" type="number" class="input" min="1" max="100" />
            </div>
            <div class="form-group">
              <label class="form-label">任务失败重试次数</label>
              <input v-model.number="crawlerConfig.retry_count" type="number" class="input" min="0" max="10" />
            </div>
            <div class="form-group">
              <label class="form-label">日志保留天数</label>
              <input v-model.number="crawlerConfig.log_retention_days" type="number" class="input" min="1" max="365" />
            </div>
            <div class="form-group">
              <label class="form-label">代理刷新间隔（分钟）</label>
              <input v-model.number="crawlerConfig.proxy_refresh_interval" type="number" class="input" min="1" max="1440" />
            </div>
            <button class="btn-save" :disabled="crawlerSaving" @click="saveCrawlerConfig">
              {{ crawlerSaving ? '保存中...' : '保存爬虫设置' }}
            </button>
          </div>

          <!-- ========== 主题切换 ========== -->
          <div v-if="activeTab === 'theme'" class="card section-card">
            <h3 class="section-title">主题配色</h3>
            <p class="section-desc">选择一套你喜欢的主题配色，整套系统将全局同步变色</p>
            <div class="theme-grid">
              <div
                v-for="(theme, key) in themeStore.themeList"
                :key="key"
                class="theme-card"
                :class="{ active: themeStore.currentTheme === key }"
                @click="handleSwitchTheme(key)"
              >
                <div class="theme-preview" :style="{ background: getThemePreviewBg(key) }">
                  <div class="theme-preview-bar" :style="{ background: theme.colors['--gradient-primary'] }"></div>
                  <div class="theme-preview-row">
                    <span class="theme-preview-dot" :style="{ background: theme.colors['--accent-primary'] }"></span>
                    <span class="theme-preview-line" :style="{ background: theme.colors['--text-muted'] }"></span>
                  </div>
                  <div class="theme-preview-row">
                    <span class="theme-preview-square" :style="{ background: theme.colors['--accent-secondary'] }"></span>
                    <span class="theme-preview-line short" :style="{ background: theme.colors['--text-muted'] }"></span>
                  </div>
                </div>
                <div class="theme-info">
                  <span class="theme-name">{{ theme.name }}</span>
                  <span class="theme-label">{{ theme.label }}</span>
                </div>
                <div v-if="themeStore.currentTheme === key" class="theme-active-badge">当前</div>
              </div>
            </div>
            <button
              v-if="themeStore.currentTheme !== 'default'"
              class="btn-reset"
              @click="handleSwitchTheme('default')"
            >
              恢复默认主题
            </button>
          </div>

          <!-- ========== 通知设置 ========== -->
          <div v-if="activeTab === 'notification'" class="card section-card">
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
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { systemAPI } from '../api/system'
import { userAPI, authAPI } from '../api/index'
import { useAuthStore } from '../stores/auth'
import { useThemeStore } from '../stores/theme'
import NavBar from '../components/NavBar.vue'

const authStore = useAuthStore()
const themeStore = useThemeStore()

const activeTab = ref('profile')

const tabs = [
  { key: 'profile', label: '个人资料', icon: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>' },
  { key: 'security', label: '账号安全', icon: '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>' },
  { key: 'system', label: '系统通用', icon: '<circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>' },
  { key: 'crawler', label: '爬虫业务', icon: '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>' },
  { key: 'theme', label: '主题配色', icon: '<path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/>' },
  { key: 'notification', label: '通知设置', icon: '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>' },
]

// Profile state
const profileData = reactive({ username: '', nickname: '', avatar_url: '', bio: '', email: '', phone: '' })
const profileSaving = ref(false)

// Password state
const pwdData = reactive({ old_password: '', new_password: '', confirm_password: '' })
const pwdSaving = ref(false)

// System settings state
const sysSettings = reactive({
  site_title: 'CrawlMaster',
  site_logo: '',
  animation_enabled: true,
  breadcrumb_enabled: true,
  sidebar_collapsed: false,
  notif_alerts: true,
  notif_system: true
})
const sysSaving = ref(false)

// Crawler config state
const crawlerConfig = reactive({
  default_request_interval: 2000,
  default_concurrency: 5,
  retry_count: 3,
  log_retention_days: 30,
  proxy_refresh_interval: 60
})
const crawlerSaving = ref(false)

// Notification state
const notifTaskFail = ref(true)
const notifTimeout = ref(true)
const notifDataError = ref(true)
const notifIpBlocked = ref(true)
const notifSystem = ref(true)
const notifEmail = ref(false)
const notifWechat = ref(false)

// --- Profile ---
async function loadProfile() {
  try {
    const res = await userAPI.getProfile()
    if (res.data.success) {
      const d = res.data.data
      Object.assign(profileData, {
        username: d.username || '',
        nickname: d.nickname || '',
        avatar_url: d.avatar_url || '',
        bio: d.bio || '',
        email: d.email || '',
        phone: d.phone || ''
      })
    }
  } catch { /* ignore */ }
}

async function saveProfile() {
  profileSaving.value = true
  try {
    const res = await userAPI.updateProfile({
      nickname: profileData.nickname,
      avatar_url: profileData.avatar_url,
      bio: profileData.bio
    })
    if (res.data.success) {
      authStore.fetchProfile()
      ElMessage.success('个人资料已保存')
    } else {
      ElMessage.error(res.data.message || '保存失败')
    }
  } catch (error) {
    ElMessage.error('保存个人资料失败')
  } finally {
    profileSaving.value = false
  }
}

// --- Security ---
async function savePassword() {
  if (!pwdData.old_password || !pwdData.new_password || !pwdData.confirm_password) {
    ElMessage.warning('请填写完整密码信息')
    return
  }
  if (pwdData.new_password.length < 6) {
    ElMessage.warning('新密码至少6个字符')
    return
  }
  if (pwdData.new_password !== pwdData.confirm_password) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  pwdSaving.value = true
  try {
    const res = await authAPI.changePassword({
      old_password: pwdData.old_password,
      new_password: pwdData.new_password
    })
    if (res.data.success) {
      ElMessage.success('密码修改成功，下次登录请使用新密码')
      pwdData.old_password = ''
      pwdData.new_password = ''
      pwdData.confirm_password = ''
    } else {
      ElMessage.error(res.data.message || '密码修改失败')
    }
  } catch (error) {
    ElMessage.error('修改密码失败')
  } finally {
    pwdSaving.value = false
  }
}

// --- System Settings ---
async function loadSystemSettings() {
  try {
    const res = await systemAPI.getSettingsBatch()
    if (res.data.success) {
      const d = res.data.data || {}
      if (d.site_title !== undefined) sysSettings.site_title = d.site_title
      if (d.site_logo !== undefined) sysSettings.site_logo = d.site_logo
      if (d.animation_enabled !== undefined) sysSettings.animation_enabled = d.animation_enabled
      if (d.breadcrumb_enabled !== undefined) sysSettings.breadcrumb_enabled = d.breadcrumb_enabled
      if (d.sidebar_collapsed !== undefined) sysSettings.sidebar_collapsed = d.sidebar_collapsed
      if (d.notif_alerts !== undefined) sysSettings.notif_alerts = d.notif_alerts
      if (d.notif_system !== undefined) sysSettings.notif_system = d.notif_system
      if (d.default_request_interval !== undefined) crawlerConfig.default_request_interval = Number(d.default_request_interval)
      if (d.default_concurrency !== undefined) crawlerConfig.default_concurrency = Number(d.default_concurrency)
      if (d.retry_count !== undefined) crawlerConfig.retry_count = Number(d.retry_count)
      if (d.log_retention_days !== undefined) crawlerConfig.log_retention_days = Number(d.log_retention_days)
      if (d.proxy_refresh_interval !== undefined) crawlerConfig.proxy_refresh_interval = Number(d.proxy_refresh_interval)
    }
  } catch { /* ignore */ }
}

async function saveSystemSettings() {
  sysSaving.value = true
  try {
    const data = { ...sysSettings }
    const res = await systemAPI.saveSettingsBatch(data)
    if (res.data.success) {
      ElMessage.success('系统通用设置已保存')
    } else {
      ElMessage.error(res.data.message || '保存失败')
    }
  } catch (error) {
    ElMessage.error('保存设置失败')
  } finally {
    sysSaving.value = false
  }
}

// --- Crawler Config ---
async function saveCrawlerConfig() {
  crawlerSaving.value = true
  try {
    const data = { ...crawlerConfig }
    const res = await systemAPI.saveSettingsBatch(data)
    if (res.data.success) {
      ElMessage.success('爬虫业务设置已保存')
    } else {
      ElMessage.error(res.data.message || '保存失败')
    }
  } catch (error) {
    ElMessage.error('保存设置失败')
  } finally {
    crawlerSaving.value = false
  }
}

// --- Theme ---
function getThemePreviewBg(key) {
  const bgColors = {
    'pure-black': '#050505',
    default: '#0d1117',
    'space-gray': '#0f172a',
    'ice-blue': '#0c1119',
    'night-green': '#1c1412',
    'purple-gold': '#0f0d14',
    'cyber-aurora': '#0a0e17',
    'pure-black': '#050505'
  }
  return bgColors[key] || '#0d1117'
}

async function handleSwitchTheme(key) {
  await themeStore.switchTheme(key)
  ElMessage.success(`已切换至「${themeStore.getThemeInfo(key).name}」主题`)
}

// --- Notification ---
async function loadPreferences() {
  try {
    const res = await systemAPI.getUserPreferences()
    if (res.data.success) {
      const prefs = res.data.data || {}
      if (prefs.notif_task_fail !== undefined) notifTaskFail.value = prefs.notif_task_fail
      if (prefs.notif_timeout !== undefined) notifTimeout.value = prefs.notif_timeout
      if (prefs.notif_data_error !== undefined) notifDataError.value = prefs.notif_data_error
      if (prefs.notif_ip_blocked !== undefined) notifIpBlocked.value = prefs.notif_ip_blocked
      if (prefs.notif_system !== undefined) notifSystem.value = prefs.notif_system
      if (prefs.notif_email !== undefined) notifEmail.value = prefs.notif_email
      if (prefs.notif_wechat !== undefined) notifWechat.value = prefs.notif_wechat
    }
  } catch { /* ignore */ }
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

onMounted(() => {
  loadProfile()
  loadSystemSettings()
  loadPreferences()
  themeStore.syncFromServer()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background-color: var(--bg-primary, #0d1117);
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
    radial-gradient(ellipse 80% 60% at 50% -20%, var(--glow-color, rgba(76, 110, 245, 0.06)), transparent),
    radial-gradient(ellipse 60% 40% at 80% 80%, var(--glow-color-2, rgba(124, 58, 237, 0.04)), transparent);
  pointer-events: none; z-index: 0;
}
.content {
  max-width: 1080px;
  margin: 0 auto;
  padding: 40px 24px 80px;
  position: relative; z-index: 1;
}
.page-header { margin-bottom: 28px; }
.page-title {
  font-size: 26px; font-weight: 700;
  color: var(--text-primary, rgba(255, 255, 255, 0.9));
  letter-spacing: -0.5px; margin-bottom: 4px;
}
.page-sub {
  font-size: 13px; color: var(--text-secondary);
}

.layout { display: grid; grid-template-columns: 220px 1fr; gap: 20px; align-items: start; }
.card {
  background: var(--bg-card, rgba(22, 27, 34, 0.8));
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.06));
  border-radius: 16px; padding: 24px;
}
.sidebar-nav { padding: 8px; }
.sidebar-tab {
  display: flex; align-items: center; gap: 10px;
  width: 100%; padding: 11px 16px; font-size: 13px; font-weight: 500;
  color: var(--text-secondary, rgba(255,255,255,0.4)); background: transparent; border: none;
  border-radius: 10px; cursor: pointer; transition: all 0.2s ease; text-align: left;
}
.sidebar-tab:hover { color: var(--text-primary, rgba(255,255,255,0.65)); background: rgba(255,255,255,0.03); }
.sidebar-tab.active {
  background: var(--active-bg, rgba(76,110,245,0.1));
  color: var(--active-color, #7c8aff); font-weight: 600;
}
.sidebar-tab svg { width: 18px; height: 18px; flex-shrink: 0; }
.tab-content-area { animation: fadeIn 0.25s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateX(6px); } to { opacity: 1; transform: translateX(0); } }

.section-card { padding: 28px; }
.section-title {
  font-size: 16px; font-weight: 700;
  color: var(--text-primary, rgba(255,255,255,0.8));
  margin-bottom: 24px;
}
.section-desc {
  font-size: 12px; color: var(--text-muted, rgba(255,255,255,0.35));
  margin: -16px 0 20px 0;
}

.form-group { margin-bottom: 20px; }
.form-label {
  display: block; font-size: 12px; font-weight: 500;
  color: var(--text-muted, rgba(255,255,255,0.35));
  margin-bottom: 6px;
}
.input {
  width: 100%; padding: 10px 14px; font-size: 13px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-color);
  border-radius: 8px; color: var(--text-primary, rgba(255, 255, 255, 0.75));
  outline: none; transition: all 0.2s ease; box-sizing: border-box;
}
.input:focus {
  border-color: var(--accent-primary, rgba(76, 110, 245, 0.4));
  background: rgba(255, 255, 255, 0.06);
}
.input:disabled { opacity: 0.5; cursor: not-allowed; }
.input-textarea { resize: vertical; min-height: 72px; font-family: inherit; }

.toggle-list { display: flex; flex-direction: column; gap: 4px; margin-bottom: 20px; }
.toggle-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 11px 16px; background: rgba(255,255,255,0.02);
  border: 1px solid var(--border-color, rgba(255,255,255,0.04));
  border-radius: 10px; font-size: 13px;
  color: var(--text-secondary, rgba(255,255,255,0.55));
  cursor: pointer; transition: all 0.15s ease;
}
.toggle-item:hover { background: rgba(255,255,255,0.04); }
.toggle-item input { accent-color: var(--accent-primary, #4c6ef5); width: 18px; height: 18px; }

.notif-section { margin-bottom: 24px; }
.notif-subtitle {
  font-size: 13px; font-weight: 600;
  color: var(--text-secondary, rgba(255,255,255,0.5));
  margin-bottom: 12px;
}

.btn-save {
  padding: 11px 28px; font-size: 13px; font-weight: 600;
  background: var(--gradient-primary, linear-gradient(135deg, #4c6ef5, #7c3aed));
  border: none; border-radius: 10px; color: #fff; cursor: pointer;
  transition: all 0.25s ease; margin-top: 8px;
  box-shadow: 0 2px 12px var(--accent-primary, rgba(76, 110, 245, 0.3));
}
.btn-save:hover { transform: translateY(-1px); box-shadow: var(--btn-hover-shadow, 0 4px 20px rgba(76, 110, 245, 0.45)); }
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

.btn-reset {
  padding: 10px 24px; font-size: 13px; font-weight: 600;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border-color, rgba(255,255,255,0.08));
  border-radius: 10px; color: var(--text-secondary, rgba(255,255,255,0.55));
  cursor: pointer; transition: all 0.2s ease; margin-top: 16px;
}
.btn-reset:hover {
  background: rgba(255,255,255,0.08);
  color: var(--text-primary, rgba(255,255,255,0.8));
}

/* Theme Grid */
.theme-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
.theme-card {
  background: rgba(255,255,255,0.02);
  border: 1px solid var(--border-color, rgba(255,255,255,0.06));
  border-radius: 14px; padding: 12px; cursor: pointer;
  transition: all 0.25s ease; position: relative;
}
.theme-card:hover {
  border-color: var(--accent-primary, rgba(76,110,245,0.25));
  background: var(--card-hover-bg, rgba(76,110,245,0.06));
  transform: translateY(-2px);
}
.theme-card.active {
  border-color: var(--accent-primary, rgba(76,110,245,0.4));
  background: var(--active-bg, rgba(76,110,245,0.1));
  box-shadow: 0 0 20px rgba(var(--accent-rgb, 76,110,245), 0.15);
}
.theme-preview {
  height: 72px; border-radius: 10px; padding: 10px;
  display: flex; flex-direction: column; gap: 6px;
  border: 1px solid rgba(255,255,255,0.04);
}
.theme-preview-bar {
  height: 12px; border-radius: 6px; width: 60%;
}
.theme-preview-row {
  display: flex; align-items: center; gap: 6px;
}
.theme-preview-dot {
  width: 8px; height: 8px; border-radius: 50%;
}
.theme-preview-line {
  height: 4px; border-radius: 2px; width: 40%;
}
.theme-preview-line.short { width: 25%; }
.theme-preview-square {
  width: 8px; height: 8px; border-radius: 2px;
}
.theme-info {
  margin-top: 10px; display: flex; flex-direction: column; gap: 2px;
}
.theme-name {
  font-size: 13px; font-weight: 700; color: var(--text-primary, rgba(255,255,255,0.8));
}
.theme-label {
  font-size: 11px; color: var(--text-muted, rgba(255,255,255,0.35));
}
.theme-active-badge {
  position: absolute; top: 10px; right: 10px;
  padding: 2px 8px; font-size: 10px; font-weight: 700;
  background: var(--gradient-primary, linear-gradient(135deg, #4c6ef5, #7c3aed));
  color: #fff; border-radius: 6px;
}

@media (max-width: 768px) {
  .content { padding: 24px 16px 64px; }
  .page-title { font-size: 22px; }
  .layout { grid-template-columns: 1fr; }
  .sidebar-nav { display: flex; gap: 4px; padding: 4px; overflow-x: auto; }
  .sidebar-tab { width: auto; white-space: nowrap; }
  .theme-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 560px) {
  .theme-grid { grid-template-columns: 1fr; }
  .sidebar-tab span { display: none; }
}
</style>