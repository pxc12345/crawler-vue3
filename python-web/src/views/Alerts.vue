<template>
  <div class="alerts-page">
    <NavBar />
    <div class="alerts-content">
      <div class="page-header">
        <div class="header-left">
          <h1 class="page-title">告警中心</h1>
          <span class="unread-count" v-if="unreadCount > 0">{{ unreadCount }} 条未读</span>
        </div>
        <button class="btn-mark-all" @click="markAllRead" :disabled="unreadCount === 0">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          全部已读
        </button>
      </div>

      <div class="filter-bar">
        <div class="type-filter">
          <button
            v-for="t in typeOptions"
            :key="t.value"
            class="type-btn"
            :class="{ active: activeType === t.value }"
            @click="activeType = t.value"
          >{{ t.label }}</button>
        </div>
        <label class="read-toggle">
          <input type="checkbox" v-model="showUnreadOnly" />
          <span>仅显示未读</span>
        </label>
      </div>

      <div v-if="loading" class="skeleton-list">
        <div v-for="n in 4" :key="n" class="skeleton-card">
          <div class="skeleton-line w-60"></div>
          <div class="skeleton-line w-40"></div>
          <div class="skeleton-line w-80"></div>
        </div>
      </div>

      <div v-else-if="filteredAlerts.length === 0" class="empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
          </svg>
        </div>
        <p class="empty-text">暂无告警记录</p>
        <p class="empty-desc">一切运行正常，没有新的告警信息</p>
      </div>

      <div v-else class="alert-list">
        <div
          v-for="alert in paginatedAlerts"
          :key="alert.id"
          class="alert-card"
          :class="{ unread: !alert.read, expanded: expandedId === alert.id }"
          @click="toggleExpand(alert)"
        >
          <div class="alert-card-main">
            <div class="alert-left">
              <div class="alert-icon" :class="'icon-' + alert.type">
                <svg v-if="alert.type === 'task_failed'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <svg v-else-if="alert.type === 'timeout'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
                <svg v-else-if="alert.type === 'data_error'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                  <line x1="12" y1="9" x2="12" y2="13"/>
                  <line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
                <svg v-else-if="alert.type === 'ip_blocked'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="16" x2="12" y2="12"/>
                  <line x1="12" y1="8" x2="12.01" y2="8"/>
                </svg>
              </div>
              <div class="alert-info">
                <div class="alert-message">{{ alert.message }}</div>
                <div class="alert-meta">
                  <span class="alert-task">{{ alert.taskName }}</span>
                  <span class="alert-time">{{ alert.time }}</span>
                </div>
              </div>
            </div>
            <div class="alert-right">
              <span v-if="!alert.read" class="unread-dot"></span>
              <svg class="expand-icon" :class="{ rotated: expandedId === alert.id }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="6 9 12 15 18 9"/>
              </svg>
            </div>
          </div>

          <div v-if="expandedId === alert.id" class="alert-detail" @click.stop>
            <div class="detail-section">
              <h4 class="detail-label">告警详情</h4>
              <p class="detail-text">{{ alert.detail }}</p>
            </div>
            <div class="detail-section">
              <h4 class="detail-label">建议操作</h4>
              <p class="detail-text">{{ alert.suggestion }}</p>
            </div>
            <div class="detail-actions">
              <button class="detail-btn" @click="markRead(alert)" v-if="!alert.read">标记已读</button>
              <button class="detail-btn primary" @click="goToTask(alert)">查看任务</button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="filteredAlerts.length > 0 && !loading" class="pagination">
        <button class="page-btn" :disabled="currentPage <= 1" @click="currentPage--">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button class="page-btn" :disabled="currentPage >= totalPages" @click="currentPage++">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '../components/NavBar.vue'
import { alertAPI } from '../api/alert'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(true)
const alerts = ref([])
const total = ref(0)
const unreadCount = ref(0)
const activeType = ref('all')
const showUnreadOnly = ref(false)
const currentPage = ref(1)
const expandedId = ref(null)
const pageSize = 10

const typeOptions = [
  { label: '全部', value: 'all' },
  { label: '任务失败', value: 'task_failed' },
  { label: '超时', value: 'timeout' },
  { label: '数据异常', value: 'data_error' },
  { label: 'IP被封', value: 'ip_blocked' }
]

const filteredAlerts = computed(() => alerts.value)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

const paginatedAlerts = computed(() => alerts.value)

function toggleExpand(alert) {
  expandedId.value = expandedId.value === alert.id ? null : alert.id
  if (!alert.read) {
    markRead(alert)
  }
}

async function markRead(alert) {
  try {
    await alertAPI.markAsRead(alert.id)
    alert.read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch (e) {
    ElMessage.error('标记已读失败')
  }
}

async function markAllRead() {
  try {
    await alertAPI.markAllAsRead()
    alerts.value.forEach(a => { a.read = true })
    unreadCount.value = 0
    ElMessage.success('已全部标记为已读')
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

function goToTask(alert) {
  if (alert.taskId) {
    router.push(`/tasks/${alert.taskId}`)
  }
}

function mapAlertFromApi(item) {
  return {
    id: item.id,
    type: item.type,
    message: item.message,
    taskName: item.task_name || '',
    taskId: item.task_id,
    time: item.created_at || '',
    read: item.is_read === 1 || item.is_read === true,
    detail: item.detail || '',
    suggestion: item.suggestion || ''
  }
}

async function fetchAlerts() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize
    }
    if (activeType.value !== 'all') {
      params.type = activeType.value
    }
    if (showUnreadOnly.value) {
      params.is_read = 0
    }
    const res = await alertAPI.getAlerts(params)
    if (res.data.success) {
      alerts.value = (res.data.data.list || []).map(mapAlertFromApi)
      total.value = res.data.data.total || 0
    } else {
      ElMessage.error(res.data.message || '获取告警列表失败')
    }
  } catch (e) {
    ElMessage.error('获取告警列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchUnreadCount() {
  try {
    const res = await alertAPI.getUnreadCount()
    if (res.data.success) {
      unreadCount.value = res.data.data.count || 0
    }
  } catch (e) {
    // silent
  }
}

watch([activeType, showUnreadOnly], () => {
  currentPage.value = 1
  fetchAlerts()
})

watch(currentPage, () => {
  fetchAlerts()
})

onMounted(() => {
  fetchAlerts()
  fetchUnreadCount()
})
</script>

<style scoped>
.alerts-page {
  min-height: 100vh;
  background-color: var(--bg-primary);
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px);
  background-size: 40px 40px;
}

.alerts-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background:
    radial-gradient(ellipse 80% 60% at 50% -20%, rgba(var(--accent-rgb), 0.06), transparent),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(52, 211, 153, 0.04), transparent);
  pointer-events: none;
  z-index: 0;
}

.alerts-content {
  max-width: 960px;
  margin: 0 auto;
  padding: 40px 24px 80px;
  position: relative;
  z-index: 1;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 14px;
}

.page-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.unread-count {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  background: rgba(239, 68, 68, 0.12);
  color: #f87171;
  border-radius: 20px;
}

.btn-mark-all {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  font-size: 13px;
  font-weight: 600;
  background: rgba(var(--accent-rgb), 0.12);
  border: 1px solid rgba(var(--accent-rgb), 0.2);
  border-radius: 10px;
  color: var(--active-color);
  cursor: pointer;
  transition: all 0.25s ease;
}

.btn-mark-all:hover:not(:disabled) {
  background: rgba(76, 110, 245, 0.2);
}

.btn-mark-all:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.btn-mark-all svg { width: 16px; height: 16px; }

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 14px;
}

.type-filter {
  display: flex;
  gap: 4px;
  background: var(--bg-card);
  border-radius: 10px;
  padding: 4px;
  border: 1px solid var(--border-color);
}

.type-btn {
  padding: 7px 15px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.type-btn:hover { color: var(--text-primary); }
.type-btn.active { color: var(--accent-primary); background: rgba(var(--accent-rgb), 0.15); font-weight: 600; }

.read-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
  cursor: pointer;
}

.read-toggle input { accent-color: var(--accent-primary); }

.skeleton-list { display: flex; flex-direction: column; gap: 12px; }
.skeleton-card {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.04);
}
.skeleton-line {
  height: 14px;
  background: var(--border-color);
  border-radius: 7px;
  margin-bottom: 10px;
  animation: shimmer 1.5s ease-in-out infinite;
}
.skeleton-line.w-60 { width: 60%; }
.skeleton-line.w-40 { width: 40%; }
.skeleton-line.w-80 { width: 80%; }
@keyframes shimmer {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}

.empty-state { text-align: center; padding: 80px 20px; }
.empty-icon {
  width: 80px; height: 80px; margin: 0 auto 24px;
  border-radius: 20px; background: var(--border-color);
  display: flex; align-items: center; justify-content: center;
  color: var(--text-muted);
}
.empty-icon svg { width: 36px; height: 36px; }
.empty-text { font-size: 18px; font-weight: 600; color: var(--text-muted); margin-bottom: 8px; }
.empty-desc { font-size: 13px; color: var(--text-muted); }

.alert-list { display: flex; flex-direction: column; gap: 10px; }

.alert-card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.alert-card:hover {
  background: var(--bg-card);
  border-color: rgba(255, 255, 255, 0.1);
}

.alert-card.unread {
  border-left: 3px solid #f87171;
}

.alert-card-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 22px;
}

.alert-left {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  flex: 1;
  min-width: 0;
}

.alert-icon {
  width: 42px; height: 42px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.alert-icon svg { width: 20px; height: 20px; }

.icon-task_failed { background: rgba(239, 68, 68, 0.12); color: #f87171; }
.icon-timeout { background: rgba(245, 158, 11, 0.12); color: #fbbf24; }
.icon-data_error { background: rgba(var(--accent-rgb), 0.12); color: var(--accent-primary); }
.icon-ip_blocked { background: rgba(239, 68, 68, 0.12); color: #f87171; }

.alert-info { flex: 1; min-width: 0; }

.alert-message {
  font-size: 14px; font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px; line-height: 1.4;
}

.alert-meta {
  display: flex; gap: 14px;
  font-size: 12px; color: var(--text-muted);
}

.alert-task { font-weight: 500; color: var(--text-muted); }

.alert-right {
  display: flex; align-items: center; gap: 10px;
  flex-shrink: 0;
}

.unread-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--error-text, #f87171);
  box-shadow: 0 0 6px rgba(248, 113, 113, 0.5);
}

.expand-icon {
  width: 18px; height: 18px;
  color: var(--text-muted);
  transition: transform 0.25s ease;
}

.expand-icon.rotated { transform: rotate(180deg); }

.alert-detail {
  padding: 0 22px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  animation: slideDown 0.25s ease;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}

.detail-section { margin-top: 16px; }

.detail-label {
  font-size: 11px; font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase; letter-spacing: 0.5px;
  margin-bottom: 6px;
}

.detail-text {
  font-size: 13px; color: var(--text-secondary);
  line-height: 1.6;
}

.detail-actions {
  display: flex; gap: 8px; margin-top: 16px;
}

.detail-btn {
  padding: 7px 16px; font-size: 12px; font-weight: 500;
  border: 1px solid var(--border-color); border-radius: 8px;
  cursor: pointer; transition: all 0.2s ease;
  background: var(--border-color); color: var(--text-secondary);
}

.detail-btn:hover { background: var(--card-hover-bg); color: var(--text-primary); }

.detail-btn.primary {
  background: rgba(var(--accent-rgb), 0.15);
  color: var(--active-color); border-color: rgba(var(--accent-rgb), 0.2);
}
.detail-btn.primary:hover { background: rgba(var(--accent-rgb), 0.22); }

.pagination {
  display: flex; justify-content: center; align-items: center;
  gap: 16px; margin-top: 32px;
}

.page-btn {
  width: 38px; height: 38px; display: flex; align-items: center; justify-content: center;
  background: var(--bg-card); border: 1px solid var(--border-color);
  border-radius: 10px; color: var(--text-secondary);
  cursor: pointer; transition: all 0.25s ease;
}

.page-btn:hover:not(:disabled) { color: var(--text-primary); border-color: rgba(var(--accent-rgb), 0.2); }
.page-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.page-btn svg { width: 18px; height: 18px; }
.page-info { font-size: 13px; font-weight: 600; color: var(--text-muted); }

@media (max-width: 768px) {
  .alerts-content { padding: 24px 16px 64px; }
  .page-title { font-size: 22px; }
  .type-filter { overflow-x: auto; }
  .alert-card-main { padding: 14px 16px; }
}

@media (max-width: 560px) {
  .alert-meta { flex-direction: column; gap: 2px; }
}
</style>