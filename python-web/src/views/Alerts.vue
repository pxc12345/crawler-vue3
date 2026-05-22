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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '../components/NavBar.vue'

const router = useRouter()
const loading = ref(true)
const alerts = ref([])
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

const unreadCount = computed(() => alerts.value.filter(a => !a.read).length)

const filteredAlerts = computed(() => {
  let result = alerts.value
  if (activeType.value !== 'all') {
    result = result.filter(a => a.type === activeType.value)
  }
  if (showUnreadOnly.value) {
    result = result.filter(a => !a.read)
  }
  return result
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredAlerts.value.length / pageSize)))

const paginatedAlerts = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredAlerts.value.slice(start, start + pageSize)
})

function toggleExpand(alert) {
  expandedId.value = expandedId.value === alert.id ? null : alert.id
  if (!alert.read) {
    alert.read = true
  }
}

function markRead(alert) {
  alert.read = true
}

function markAllRead() {
  alerts.value.forEach(a => { a.read = true })
}

function goToTask(alert) {
  if (alert.taskId) {
    router.push(`/tasks/${alert.taskId}`)
  }
}

async function fetchAlerts() {
  loading.value = true
  await new Promise(r => setTimeout(r, 500))
  alerts.value = [
    { id: 1, type: 'task_failed', message: '任务「竞品价格追踪」执行失败：目标站点返回 503', taskName: '竞品价格追踪', taskId: 5, time: '10分钟前', read: false, detail: '任务在执行到第3页时，目标站点返回HTTP 503 Service Unavailable错误。可能是服务器负载过高或临时维护。连续重试3次均失败。', suggestion: '等待5分钟后手动重启任务；检查目标站点是否可正常访问；考虑增加请求间隔降低访问频率。' },
    { id: 2, type: 'timeout', message: '任务「电商商品数据采集」请求超时：响应超过30秒', taskName: '电商商品数据采集', taskId: 1, time: '28分钟前', read: false, detail: '在采集商品详情页时，第47条数据的请求超过了预设的30秒超时限制。返回的数据不完整，该条记录已被标记为可疑。', suggestion: '检查目标站点响应速度；适当增加超时阈值到60秒；考虑更换代理服务器。' },
    { id: 3, type: 'data_error', message: '任务「金融数据采集」数据解析异常：JSON格式错误', taskName: '金融数据采集', taskId: 9, time: '1小时前', read: false, detail: '目标站点返回的数据结构与预设的JSON Schema不匹配。某些字段缺失或类型错误，导致数据无法正确入库。', suggestion: '检查目标站点是否更改了API返回格式；更新数据解析规则；将异常数据写入死信队列以便后续分析。' },
    { id: 4, type: 'ip_blocked', message: '代理IP池耗尽警告：当前可用IP少于5个', taskName: '系统监控', taskId: null, time: '1小时前', read: true, detail: '系统代理池中可用IP地址数量已降至5个以下。多个任务因缺少可用代理而暂停执行。当前活跃任务包括：社交媒体评论采集、地图POI数据。', suggestion: '立即前往代理管理页面添加新的代理IP；检查现有代理IP是否被目标站点封锁；启用自动代理轮换策略。' },
    { id: 5, type: 'task_failed', message: '任务「视频元数据采集」部分失败：128条数据未能解析', taskName: '视频元数据采集', taskId: 10, time: '2小时前', read: true, detail: '在采集过程中，有128条视频的元数据解析失败。原因可能是视频已下架或页面结构变更。其余数据正常入库。', suggestion: '检查解析失败的URL列表；更新页面解析规则以适配新的页面结构；考虑添加数据完整性校验。' },
    { id: 6, type: 'timeout', message: '任务「地图POI数据」请求延迟警告：平均响应4.8秒', taskName: '地图POI数据', taskId: 12, time: '3小时前', read: true, detail: '地图服务接口响应时间持续增加，已超过预设的3秒告警阈值。当前平均响应时间为4.8秒，可能影响整体采集效率。', suggestion: '检查网络连接质量；考虑切换到备用代理线路；适当降低并发数以缓解延迟问题。' },
    { id: 7, type: 'data_error', message: '任务「新闻资讯爬取」数据去重失败：数据库连接超时', taskName: '新闻资讯爬取', taskId: 2, time: '4小时前', read: true, detail: '在写入采集数据到数据库时，MongoDB连接超时。数据暂时缓存在内存中，可能导致数据丢失风险。', suggestion: '检查数据库服务器运行状态；检查网络连接；考虑启用数据持久化缓存机制。' },
    { id: 8, type: 'ip_blocked', message: '代理IP 192.168.1.50 已被目标站点封锁', taskName: '电商商品数据采集', taskId: 1, time: '5小时前', read: true, detail: '代理服务器IP地址 192.168.1.50 被目标站点检测到异常访问并列入黑名单。系统已自动从代理池中移除该IP。', suggestion: '检查IP访问频率是否过高；启用随机User-Agent轮换；增加请求间隔降低检测风险。' }
  ]
  loading.value = false
}

onMounted(() => {
  fetchAlerts()
})
</script>

<style scoped>
.alerts-page {
  min-height: 100vh;
  background-color: #0d1117;
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
    radial-gradient(ellipse 80% 60% at 50% -20%, rgba(76, 110, 245, 0.06), transparent),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(16, 185, 129, 0.04), transparent);
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
  color: rgba(255, 255, 255, 0.9);
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
  background: rgba(76, 110, 245, 0.12);
  border: 1px solid rgba(76, 110, 245, 0.2);
  border-radius: 10px;
  color: #7c8aff;
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
  background: rgba(22, 27, 34, 0.6);
  border-radius: 10px;
  padding: 4px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.type-btn {
  padding: 7px 15px;
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.45);
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.type-btn:hover { color: rgba(255, 255, 255, 0.75); }
.type-btn.active { color: #7c8aff; background: rgba(76, 110, 245, 0.15); font-weight: 600; }

.read-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
}

.read-toggle input { accent-color: #4c6ef5; }

.skeleton-list { display: flex; flex-direction: column; gap: 12px; }
.skeleton-card {
  background: rgba(22, 27, 34, 0.5);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.04);
}
.skeleton-line {
  height: 14px;
  background: rgba(255, 255, 255, 0.04);
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
  border-radius: 20px; background: rgba(255, 255, 255, 0.03);
  display: flex; align-items: center; justify-content: center;
  color: rgba(255, 255, 255, 0.1);
}
.empty-icon svg { width: 36px; height: 36px; }
.empty-text { font-size: 18px; font-weight: 600; color: rgba(255, 255, 255, 0.35); margin-bottom: 8px; }
.empty-desc { font-size: 13px; color: rgba(255, 255, 255, 0.2); }

.alert-list { display: flex; flex-direction: column; gap: 10px; }

.alert-card {
  background: rgba(22, 27, 34, 0.55);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.alert-card:hover {
  background: rgba(22, 27, 34, 0.75);
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
.icon-data_error { background: rgba(99, 102, 241, 0.12); color: #818cf8; }
.icon-ip_blocked { background: rgba(239, 68, 68, 0.12); color: #f87171; }

.alert-info { flex: 1; min-width: 0; }

.alert-message {
  font-size: 14px; font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 6px; line-height: 1.4;
}

.alert-meta {
  display: flex; gap: 14px;
  font-size: 12px; color: rgba(255, 255, 255, 0.3);
}

.alert-task { font-weight: 500; color: rgba(255, 255, 255, 0.4); }

.alert-right {
  display: flex; align-items: center; gap: 10px;
  flex-shrink: 0;
}

.unread-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #f87171;
  box-shadow: 0 0 6px rgba(248, 113, 113, 0.5);
}

.expand-icon {
  width: 18px; height: 18px;
  color: rgba(255, 255, 255, 0.2);
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
  color: rgba(255, 255, 255, 0.35);
  text-transform: uppercase; letter-spacing: 0.5px;
  margin-bottom: 6px;
}

.detail-text {
  font-size: 13px; color: rgba(255, 255, 255, 0.5);
  line-height: 1.6;
}

.detail-actions {
  display: flex; gap: 8px; margin-top: 16px;
}

.detail-btn {
  padding: 7px 16px; font-size: 12px; font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px;
  cursor: pointer; transition: all 0.2s ease;
  background: rgba(255, 255, 255, 0.04); color: rgba(255, 255, 255, 0.5);
}

.detail-btn:hover { background: rgba(255, 255, 255, 0.08); color: rgba(255, 255, 255, 0.75); }

.detail-btn.primary {
  background: rgba(76, 110, 245, 0.15);
  color: #7c8aff; border-color: rgba(76, 110, 245, 0.2);
}
.detail-btn.primary:hover { background: rgba(76, 110, 245, 0.22); }

.pagination {
  display: flex; justify-content: center; align-items: center;
  gap: 16px; margin-top: 32px;
}

.page-btn {
  width: 38px; height: 38px; display: flex; align-items: center; justify-content: center;
  background: rgba(22, 27, 34, 0.6); border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px; color: rgba(255, 255, 255, 0.5);
  cursor: pointer; transition: all 0.25s ease;
}

.page-btn:hover:not(:disabled) { color: rgba(255, 255, 255, 0.85); border-color: rgba(255, 255, 255, 0.15); }
.page-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.page-btn svg { width: 18px; height: 18px; }
.page-info { font-size: 13px; font-weight: 600; color: rgba(255, 255, 255, 0.4); }

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