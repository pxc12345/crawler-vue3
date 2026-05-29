<template>
  <div class="home-page">
    <NavBar />
    <div class="home-content">
      <div class="welcome-section">
        <div class="welcome-card">
          <div class="welcome-card-inner">
            <div class="welcome-avatar">{{ authStore.user?.username?.charAt(0)?.toUpperCase() }}</div>
            <div class="welcome-text">
              <h1 class="welcome-title">{{ greetingTitle }}, {{ authStore.user?.username }}</h1>
              <p class="welcome-subtitle">今天是美好的一天，开始您的管理工作吧</p>
            </div>
          </div>
          <div class="welcome-meta">
            <div class="welcome-time">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              <span>{{ currentDate }}</span>
            </div>
            <div class="welcome-greeting">{{ greeting }}</div>
          </div>
        </div>
      </div>

      <div class="feature-grid">
        <div class="feature-card card-crawler" @click="$router.push('/crawler')">
          <div class="feature-card-glow"></div>
          <div class="feature-icon crawler-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
              <path d="M11 8v6"/>
              <path d="M8 11h6"/>
            </svg>
          </div>
          <div class="feature-info">
            <h3 class="feature-title">爬虫管理</h3>
            <p class="feature-desc">管理和监控数据采集任务，实时追踪爬取状态</p>
          </div>
          <div class="feature-arrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
            </svg>
          </div>
          <div class="feature-indicator"></div>
        </div>

        <div class="feature-card card-stats">
          <div class="feature-card-glow"></div>
          <div class="feature-icon stats-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/>
            </svg>
          </div>
          <div class="feature-info">
            <h3 class="feature-title">今日统计</h3>
            <p class="feature-desc">查看今日数据概览：采集量、活跃任务、系统状态</p>
          </div>
          <div class="feature-stats-preview">
            <div class="stat-item">
              <span class="stat-value">{{ todayStats.collected }}</span>
              <span class="stat-label">采集</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-value">{{ todayStats.tasks }}</span>
              <span class="stat-label">任务</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-value on">正常</span>
              <span class="stat-label">状态</span>
            </div>
          </div>
          <div class="feature-indicator green"></div>
        </div>

        <div class="feature-card card-actions" @click="expandQuickActions">
          <div class="feature-card-glow"></div>
          <div class="feature-icon actions-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
          </div>
          <div class="feature-info">
            <h3 class="feature-title">快捷操作</h3>
            <p class="feature-desc">一键执行常用功能，提升工作效率</p>
          </div>
          <div class="feature-quick-links">
            <span class="quick-link" @click.stop="$router.push('/tasks')">新建任务</span>
            <span class="quick-link" @click.stop="$router.push('/data-export')">数据导出</span>
          </div>
          <div class="feature-indicator amber"></div>
        </div>

        <div class="feature-card card-notice" @click="$router.push('/alerts')">
          <div class="feature-card-glow"></div>
          <div class="feature-icon notice-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
            </svg>
          </div>
          <div class="feature-info">
            <h3 class="feature-title">系统通知</h3>
            <p class="feature-desc">查看最新系统消息和告警通知</p>
          </div>
          <div class="feature-notice-badge">{{ unreadAlertCount > 0 ? unreadAlertCount + ' 条新消息' : '暂无新消息' }}</div>
          <div class="feature-indicator red"></div>
        </div>
      </div>

      <div class="data-overview-section">
        <h2 class="section-title">今日数据概览</h2>
        <div class="data-cards">
          <div class="data-card">
            <div class="data-card-icon blue">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
                <path d="M21 3v5h-5"/>
                <path d="M7 10v7"/>
                <path d="M11 13v4"/>
                <path d="M15 8v9"/>
              </svg>
            </div>
            <div class="data-card-info">
              <span class="data-card-value">12,847</span>
              <span class="data-card-label">今日采集量</span>
              <span class="data-card-trend up">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
                  <polyline points="17 6 23 6 23 12"/>
                </svg>
                12.5%
              </span>
            </div>
          </div>

          <div class="data-card">
            <div class="data-card-icon green">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </div>
            <div class="data-card-info">
              <span class="data-card-value">156</span>
              <span class="data-card-label">成功任务</span>
              <span class="data-card-trend up">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
                  <polyline points="17 6 23 6 23 12"/>
                </svg>
                8.3%
              </span>
            </div>
          </div>

          <div class="data-card">
            <div class="data-card-icon red">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <line x1="15" y1="9" x2="9" y2="15"/>
                <line x1="9" y1="9" x2="15" y2="15"/>
              </svg>
            </div>
            <div class="data-card-info">
              <span class="data-card-value">3</span>
              <span class="data-card-label">失败任务</span>
              <span class="data-card-trend down">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/>
                  <polyline points="17 18 23 18 23 12"/>
                </svg>
                5.2%
              </span>
            </div>
          </div>

          <div class="data-card">
            <div class="data-card-icon purple">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                <line x1="8" y1="21" x2="16" y2="21"/>
                <line x1="12" y1="17" x2="12" y2="21"/>
              </svg>
            </div>
            <div class="data-card-info">
              <span class="data-card-value status-ok">运行中</span>
              <span class="data-card-label">系统状态</span>
              <span class="data-card-trend stable">正常运行</span>
            </div>
          </div>
        </div>

        <div class="chart-section">
          <div class="chart-card">
            <h3 class="chart-title">
              今日采集趋势
              <span v-if="statsTime" class="chart-time">
                更新于 {{ statsTime }}（{{ statsTimezone }}）
              </span>
            </h3>
            <div class="chart-container">
              <svg class="trend-chart" viewBox="0 0 600 140" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#4c6ef5" stop-opacity="0.25"/>
                    <stop offset="100%" stop-color="#4c6ef5" stop-opacity="0"/>
                  </linearGradient>
                </defs>
                <path class="chart-area" :d="chartAreaPath" />
                <path class="chart-line" :d="chartLinePath" />
              </svg>
              <div class="chart-labels">
                <span v-for="label in chartLabels" :key="label">{{ label }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="quick-actions-section">
        <h2 class="section-title">快捷操作区</h2>
        <div class="quick-actions-grid">
          <button class="quick-action-btn" @click="$router.push('/tasks')">
            <span class="qa-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
            </span>
            <span class="qa-text">新建任务</span>
          </button>
          <button class="quick-action-btn" @click="restartFailedTasks">
            <span class="qa-icon warning">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="23 4 23 10 17 10"/>
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
              </svg>
            </span>
            <span class="qa-text">重启失败任务</span>
          </button>
          <button class="quick-action-btn" @click="$router.push('/data-export')">
            <span class="qa-icon purple">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
            </span>
            <span class="qa-text">导出数据</span>
          </button>
          <button class="quick-action-btn" @click="$router.push('/proxy-pool')">
            <span class="qa-icon green">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="16 3 21 3 21 8"/>
                <line x1="4" y1="20" x2="21" y2="3"/>
                <polyline points="21 16 21 21 16 21"/>
                <line x1="15" y1="15" x2="21" y2="21"/>
                <line x1="4" y1="4" x2="9" y2="9"/>
              </svg>
            </span>
            <span class="qa-text">刷新代理池</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import NavBar from '../components/NavBar.vue'
import { useAuthStore } from '../stores/auth'
import { systemAPI } from '../api/system'
import { alertAPI } from '../api/alert'
import { taskAPI } from '../api/task'

const authStore = useAuthStore()
const loaded = ref(false)

const todayStats = reactive({
  collected: '0',
  tasks: '0'
})

const unreadAlertCount = ref(0)

const chartPoints = ref([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
const chartLabels = ref(['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'])
const statsTime = ref('')
const statsTimezone = ref('Asia/Shanghai')

const chartLinePath = computed(() => {
  const w = 600
  const h = 140
  const pad = 10
  const max = Math.max(...chartPoints.value, 1)
  const stepX = (w - pad * 2) / (chartPoints.value.length - 1)
  let d = ''
  chartPoints.value.forEach((p, i) => {
    const x = pad + i * stepX
    const y = h - pad - (p / max) * (h - pad * 2)
    d += `${i === 0 ? 'M' : 'L'}${x},${y} `
  })
  return d.trim()
})

const chartAreaPath = computed(() => {
  const w = 600
  const h = 140
  const pad = 10
  const max = Math.max(...chartPoints.value, 1)
  const stepX = (w - pad * 2) / (chartPoints.value.length - 1)
  let d = ''
  chartPoints.value.forEach((p, i) => {
    const x = pad + i * stepX
    const y = h - pad - (p / max) * (h - pad * 2)
    d += `${i === 0 ? 'M' : 'L'}${x},${y} `
  })
  d += `L${w - pad},${h - pad} L${pad},${h - pad} Z`
  return d.trim()
})

const currentDate = computed(() => {
  const now = new Date()
  const y = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  const weekDays = ['日', '一', '二', '三', '四', '五', '六']
  const wd = weekDays[now.getDay()]
  return `${y}年${m}月${d}日 星期${wd}`
})

const greetingTitle = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 11) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了，注意休息'
  if (hour < 11) return '上午好，精力充沛的一天'
  if (hour < 14) return '中午好，别忘了休息一下'
  if (hour < 18) return '下午好，继续加油'
  return '晚上好，回顾一下今天的成果'
})

function expandQuickActions() {
  window.scrollTo({ top: document.querySelector('.quick-actions-section')?.offsetTop - 80, behavior: 'smooth' })
}

async function restartFailedTasks() {
  try {
    const res = await taskAPI.restartFailedTasks()
    if (res.data.success) {
      ElMessage.success(res.data.message || '正在重启失败任务...')
      fetchDashboardStats()
    } else {
      ElMessage.error(res.data.message || '重启失败')
    }
  } catch (e) {
    ElMessage.error('重启失败任务出错')
  }
}

async function fetchDashboardStats() {
  try {
    const [statsRes, alertRes] = await Promise.all([
      systemAPI.getDashboardStats(),
      alertAPI.getUnreadCount()
    ])

    if (statsRes.data.success) {
      const data = statsRes.data.data
      todayStats.collected = String(data.today_collected || 0)
      todayStats.tasks = String((data.running_tasks || 0) + (data.pending_tasks || 0))
      if (data.today_trend && Array.isArray(data.today_trend)) {
        chartPoints.value = data.today_trend
      }
      if (data.hour_labels && Array.isArray(data.hour_labels) && data.hour_labels.length === 24) {
        chartLabels.value = data.hour_labels.filter((_, index) => index % 3 === 0)
      }
      if (data.stats_time) {
        statsTime.value = data.stats_time
      }
      if (data.timezone) {
        statsTimezone.value = data.timezone
      }
    }

    if (alertRes.data.success) {
      unreadAlertCount.value = alertRes.data.data?.count || 0
    }
  } catch (e) {
    console.error('获取仪表盘数据失败:', e)
  }
}

onMounted(() => {
  setTimeout(() => {
    loaded.value = true
  }, 100)
  fetchDashboardStats()
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background-color: var(--bg-primary);
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px);
  background-size: 40px 40px;
  position: relative;
}

.home-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background:
    radial-gradient(ellipse 80% 60% at 50% -20%, var(--glow-color), transparent),
    radial-gradient(ellipse 60% 40% at 80% 80%, var(--glow-color-2), transparent);
  pointer-events: none;
  z-index: 0;
}

.home-content {
  max-width: 1080px;
  margin: 0 auto;
  padding: 48px 24px 80px;
  position: relative;
  z-index: 1;
}

.welcome-section {
  margin-bottom: 40px;
  opacity: 0;
  transform: translateY(20px);
  animation: fadeInUp 0.6s cubic-bezier(0.22, 0.61, 0.36, 1) forwards;
}

.welcome-card {
  background: var(--bg-card);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 24px;
  padding: 40px 48px;
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.2),
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-color);
  position: relative;
  overflow: hidden;
}

.welcome-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--gradient-primary);
}

.welcome-card-inner {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 20px;
}

.welcome-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--avatar-bg);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: 0 4px 20px rgba(var(--accent-rgb), 0.35);
}

.welcome-text {
  flex: 1;
}

.welcome-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
  letter-spacing: -0.5px;
}

.welcome-subtitle {
  font-size: 14px;
  color: var(--text-muted);
}

.welcome-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.welcome-time {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 20px;
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
  border: 1px solid var(--border-color);
}

.welcome-time svg {
  width: 16px;
  height: 16px;
  color: var(--active-color);
}

.welcome-greeting {
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 500;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 48px;
}

.feature-card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 18px;
  padding: 28px 24px 24px;
  transition: all 0.35s cubic-bezier(0.22, 0.61, 0.36, 1);
  cursor: default;
  position: relative;
  overflow: hidden;
  opacity: 0;
  transform: translateY(24px);
}

.feature-card:nth-child(1) { animation: fadeInUp 0.5s 0.15s cubic-bezier(0.22, 0.61, 0.36, 1) forwards; }
.feature-card:nth-child(2) { animation: fadeInUp 0.5s 0.25s cubic-bezier(0.22, 0.61, 0.36, 1) forwards; }
.feature-card:nth-child(3) { animation: fadeInUp 0.5s 0.35s cubic-bezier(0.22, 0.61, 0.36, 1) forwards; }
.feature-card:nth-child(4) { animation: fadeInUp 0.5s 0.45s cubic-bezier(0.22, 0.61, 0.36, 1) forwards; }

.feature-card:hover {
  transform: translateY(-8px);
  background: var(--bg-card);
  border-color: rgba(255, 255, 255, 0.14);
  box-shadow:
    0 4px 6px rgba(0, 0, 0, 0.15),
    0 16px 48px rgba(0, 0, 0, 0.35);
}

.feature-card-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at center, var(--glow-color), transparent 60%);
  opacity: 0;
  transition: opacity 0.35s ease;
  pointer-events: none;
}

.feature-card:hover .feature-card-glow {
  opacity: 1;
}

.card-crawler { cursor: pointer; }

.card-crawler:hover {
  border-color: rgba(var(--accent-rgb), 0.3);
  box-shadow:
    0 4px 6px rgba(0, 0, 0, 0.15),
    0 16px 48px rgba(0, 0, 0, 0.35),
    0 0 30px var(--glow-color);
}

.card-notice { cursor: pointer; }

.feature-indicator {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--active-color);
  box-shadow: 0 0 8px rgba(var(--accent-rgb), 0.5);
  animation: pulse 2s ease-in-out infinite;
}

.feature-indicator.green {
  background: #34d399;
  box-shadow: 0 0 8px rgba(52, 211, 153, 0.5);
}

.feature-indicator.amber {
  background: #fbbf24;
  box-shadow: 0 0 8px rgba(251, 191, 36, 0.5);
}

.feature-indicator.red {
  background: #f87171;
  box-shadow: 0 0 8px rgba(248, 113, 113, 0.5);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.feature-icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 18px;
}

.feature-icon svg {
  width: 22px;
  height: 22px;
}

.crawler-icon {
  background: rgba(var(--accent-rgb), 0.14);
  color: var(--active-color);
}

.stats-icon {
  background: rgba(16, 185, 129, 0.14);
  color: #34d399;
}

.actions-icon {
  background: rgba(245, 158, 11, 0.14);
  color: #fbbf24;
}

.notice-icon {
  background: rgba(239, 68, 68, 0.14);
  color: #f87171;
}

.feature-info {
  margin-bottom: 16px;
}

.feature-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
  letter-spacing: -0.2px;
}

.feature-desc {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
}

.feature-arrow {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  color: rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.feature-arrow svg {
  width: 18px;
  height: 18px;
}

.card-crawler:hover .feature-arrow {
  color: var(--active-color);
  transform: translateX(4px);
}

.feature-stats-preview {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 12px 0 0;
  border-top: 1px solid var(--border-color);
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 20px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.stat-value.on {
  font-size: 14px;
  color: #34d399;
}

.stat-label {
  display: block;
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-divider {
  width: 1px;
  height: 28px;
  background: var(--border-color);
}

.feature-quick-links {
  display: flex;
  gap: 8px;
  padding-top: 4px;
}

.quick-link {
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
  border: 1px solid transparent;
}

.quick-link:hover {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
  border-color: rgba(245, 158, 11, 0.2);
}

.feature-notice-badge {
  display: inline-flex;
  padding: 6px 14px;
  background: rgba(239, 68, 68, 0.12);
  border-radius: 20px;
  font-size: 12px;
  color: #f87171;
  font-weight: 600;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 20px;
  letter-spacing: -0.3px;
}

.data-overview-section {
  margin-bottom: 48px;
  opacity: 0;
  transform: translateY(24px);
  animation: fadeInUp 0.5s 0.55s cubic-bezier(0.22, 0.61, 0.36, 1) forwards;
}

.data-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.data-card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 22px 20px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  transition: all 0.3s ease;
}

.data-card:hover {
  background: var(--bg-card);
  border-color: rgba(255, 255, 255, 0.12);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
}

.data-card-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.data-card-icon svg {
  width: 20px;
  height: 20px;
}

.data-card-icon.blue {
  background: rgba(var(--accent-rgb), 0.15);
  color: var(--active-color);
}

.data-card-icon.green {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
}

.data-card-icon.red {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

.data-card-icon.purple {
  background: rgba(124, 58, 237, 0.15);
  color: #a78bfa;
}

.data-card-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.data-card-value {
  font-size: 24px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.data-card-value.status-ok {
  font-size: 16px;
  color: #34d399;
}

.data-card-label {
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.data-card-trend {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  margin-top: 4px;
}

.data-card-trend svg {
  width: 14px;
  height: 14px;
}

.data-card-trend.up {
  color: #34d399;
}

.data-card-trend.down {
  color: #f87171;
}

.data-card-trend.stable {
  color: #a78bfa;
  font-weight: 500;
}

.chart-section {
  margin-top: 0;
}

.chart-card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 16px;
  display: flex;
  align-items: baseline;
  gap: 10px;
  flex-wrap: wrap;
}

.chart-time {
  font-size: 12px;
  font-weight: 400;
  color: var(--text-tertiary, #888);
}

.chart-container {
  width: 100%;
}

.trend-chart {
  width: 100%;
  height: 140px;
}

.chart-area {
  fill: url(#chartGrad);
  stroke: none;
}

.chart-line {
  fill: none;
  stroke: var(--accent-primary);
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.chart-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  padding: 0 8px;
}

.chart-labels span {
  font-size: 11px;
  color: var(--text-muted);
}

.quick-actions-section {
  opacity: 0;
  transform: translateY(24px);
  animation: fadeInUp 0.5s 0.65s cubic-bezier(0.22, 0.61, 0.36, 1) forwards;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.quick-action-btn {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px 24px;
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 600;
}

.quick-action-btn:hover {
  background: var(--bg-card);
  border-color: rgba(255, 255, 255, 0.14);
  transform: translateY(-3px);
  box-shadow:
    0 4px 6px rgba(0, 0, 0, 0.15),
    0 12px 36px rgba(0, 0, 0, 0.3),
    0 0 24px var(--glow-color);
}

.qa-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(var(--accent-rgb), 0.14);
  color: var(--active-color);
  flex-shrink: 0;
}

.qa-icon svg {
  width: 20px;
  height: 20px;
}

.qa-icon.warning {
  background: rgba(245, 158, 11, 0.14);
  color: #fbbf24;
}

.qa-icon.purple {
  background: rgba(124, 58, 237, 0.14);
  color: #a78bfa;
}

.qa-icon.green {
  background: rgba(16, 185, 129, 0.14);
  color: #34d399;
}

.qa-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  letter-spacing: -0.2px;
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 900px) {
  .feature-grid,
  .data-cards,
  .quick-actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .welcome-card {
    padding: 32px 28px;
  }

  .welcome-title {
    font-size: 22px;
  }

  .welcome-card-inner {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }

  .welcome-meta {
    flex-direction: column;
    gap: 10px;
    align-items: center;
  }
}

@media (max-width: 560px) {
  .feature-grid,
  .data-cards,
  .quick-actions-grid {
    grid-template-columns: 1fr;
  }

  .home-content {
    padding: 32px 16px 64px;
  }

  .welcome-card {
    padding: 28px 20px;
  }

  .welcome-title {
    font-size: 20px;
  }

  .data-card-value {
    font-size: 20px;
  }
}
</style>