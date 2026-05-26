<template>
  <div class="task-detail-page">
    <NavBar />
    <div class="detail-content">
      <div class="detail-header">
        <button class="btn-back" @click="$router.back()">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
        <div class="header-info">
          <h1 class="detail-title">{{ task.name }}</h1>
          <div class="header-meta">
            <span class="task-status-tag" :class="'status-' + task.status">
              <span class="status-dot"></span>
              {{ statusLabel(task.status) }}
            </span>
            <button class="btn-version" @click="task.id && $router.push(`/tasks/${task.id}/versions`)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="6" y1="3" x2="6" y2="15"/>
                <circle cx="18" cy="6" r="3"/>
                <circle cx="6" cy="18" r="3"/>
                <path d="M18 9a9 9 0 0 1-9 9"/>
              </svg>
              版本历史
            </button>
          </div>
        </div>
      </div>

      <div class="tab-nav">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >{{ tab.label }}</button>
      </div>

      <div class="tab-content">
        <div v-if="activeTab === 'info'" class="tab-panel info-panel">
          <div class="config-form">
            <div class="form-row">
              <div class="form-group full">
                <label class="form-label">任务名称</label>
                <input v-model="form.name" type="text" class="form-input" :disabled="!editing" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group full">
                <label class="form-label">目标 URL</label>
                <input v-model="form.url" type="text" class="form-input" :disabled="!editing" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">执行周期（分钟）</label>
                <input v-model.number="form.intervalMinutes" type="number" class="form-input" :disabled="!editing" placeholder="例如：30" min="1" />
              </div>
              <div class="form-group">
                <label class="form-label">并发数</label>
                <input v-model="form.concurrency" type="number" class="form-input" :disabled="!editing" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">请求间隔 (ms)</label>
                <input v-model="form.interval" type="number" class="form-input" :disabled="!editing" />
              </div>
              <div class="form-group">
                <label class="form-label">最大重试次数</label>
                <input v-model="form.maxRetries" type="number" class="form-input" :disabled="!editing" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">爬取模式</label>
                <select v-model="form.crawlMode" class="form-input" :disabled="!editing">
                  <option value="link">链接模式</option>
                  <option value="image">图片模式</option>
                  <option value="mixed">混合模式</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">爬取页数</label>
                <input v-model.number="form.totalPages" type="number" class="form-input" :disabled="!editing" min="1" max="100" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group full">
                <label class="form-label">请求头 (JSON)</label>
                <textarea v-model="form.headers" class="form-textarea" :disabled="!editing" rows="3"></textarea>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <template v-if="!editing">
              <button class="action-btn primary" @click="editing = true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
                编辑
              </button>
            </template>
            <template v-else>
              <button class="action-btn success" @click="saveConfig">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                保存
              </button>
              <button class="action-btn cancel" @click="cancelEdit">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
                取消
              </button>
            </template>
          </div>
        </div>

        <div v-if="activeTab === 'logs'" class="tab-panel logs-panel">
          <div class="log-controls">
            <div class="log-control-left">
              <label class="auto-scroll-label">
                <input type="checkbox" v-model="autoScroll" />
                <span>自动滚动</span>
              </label>
            </div>
            <div class="log-control-right">
              <button class="btn-refresh-log" @click="refreshLogs" :disabled="logsLoading">
                {{ logsLoading ? '加载中...' : '刷新日志' }}
              </button>
              <button class="btn-clear-log" @click="logs = []">清空日志</button>
            </div>
          </div>
          <div class="log-viewer" ref="logViewerRef">
            <div v-for="(line, idx) in logs" :key="idx" class="log-line" :class="line.type">
              <span class="log-time">{{ line.time }}</span>
              <span class="log-level" :class="line.type">{{ line.level }}</span>
              <span class="log-msg" v-html="line.message"></span>
            </div>
            <div v-if="logs.length === 0" class="log-empty">暂无日志输出</div>
          </div>
        </div>

        <div v-if="activeTab === 'records'" class="tab-panel records-panel">
          <div class="timeline">
            <div v-for="record in executionRecords" :key="record.id" class="timeline-item">
              <div class="timeline-dot" :class="'dot-' + record.status"></div>
              <div class="timeline-card">
                <div class="timeline-card-top">
                  <span class="record-version">v{{ record.version }}</span>
                  <span class="record-status" :class="'status-' + record.status">{{ statusLabel(record.status) }}</span>
                </div>
                <div class="timeline-card-meta">
                  <span>持续时间: {{ record.duration }}</span>
                  <span>采集数据: {{ record.dataCount }} 条</span>
                </div>
                <div class="timeline-card-time">{{ record.time }}</div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'preview'" class="tab-panel preview-panel">
          <div v-if="dataSummaryLoading" class="loading-state">
            <div class="spinner"></div>
            <span>加载中...</span>
          </div>
          <div v-else-if="!dataSummary" class="empty-state">
            <div class="empty-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
                <polyline points="13 2 13 9 20 9"/>
              </svg>
            </div>
            <p class="empty-text">暂无数据</p>
            <p class="empty-desc">启动任务后将自动采集数据</p>
          </div>
          <div v-else class="data-overview">
            <div class="overview-header">
              <h3 class="overview-title">{{ dataSummary.task_name }}</h3>
              <span class="overview-badge" :class="task.status">{{ statusLabel(task.status) }}</span>
            </div>
            <div class="stats-grid">
              <div class="stat-card">
                <div class="stat-icon blue">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                  </svg>
                </div>
                <div class="stat-info">
                  <span class="stat-value">{{ dataSummary.total_count || dataSummary.data_count || 0 }}</span>
                  <span class="stat-label">采集数据条数</span>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon green">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                    <line x1="16" y1="2" x2="16" y2="6"/>
                    <line x1="8" y1="2" x2="8" y2="6"/>
                    <line x1="3" y1="10" x2="21" y2="10"/>
                  </svg>
                </div>
                <div class="stat-info">
                  <span class="stat-value">{{ dataSummary.today_count || 0 }}</span>
                  <span class="stat-label">今日采集</span>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon yellow">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                  </svg>
                </div>
                <div class="stat-info">
                  <span class="stat-value">{{ formatDuration(dataSummary.execution_time) }}</span>
                  <span class="stat-label">总执行时间</span>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon purple">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                  </svg>
                </div>
                <div class="stat-info">
                  <span class="stat-value">{{ dataSummary.success_rate || 0 }}%</span>
                  <span class="stat-label">成功率</span>
                </div>
              </div>
            </div>
            
            <div v-if="dataSummary.type_distribution && Object.keys(dataSummary.type_distribution).length > 0" class="type-section">
              <h4 class="section-title">数据类型分布</h4>
              <div class="type-list">
                <div v-for="(count, type) in dataSummary.type_distribution" :key="type" class="type-item">
                  <span class="type-name">{{ type === 'link' ? '链接' : type === 'image' ? '图片' : type }}</span>
                  <span class="type-count">{{ count }} 条</span>
                </div>
              </div>
            </div>

            <div v-if="dataSummary.last_collected_at" class="time-section">
              <h4 class="section-title">最近采集时间</h4>
              <span class="last-time">{{ dataSummary.last_collected_at }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import NavBar from '../components/NavBar.vue'
import { taskAPI } from '../api/task'
import { systemAPI } from '../api/system'

const route = useRoute()
const activeTab = ref('info')
const editing = ref(false)
const autoScroll = ref(true)
const logViewerRef = ref(null)

const task = ref({})

const tabs = [
  { key: 'info', label: '基础信息' },
  { key: 'logs', label: '运行日志' },
  { key: 'records', label: '执行记录' },
  { key: 'preview', label: '数据预览' }
]

const statusLabelMap = { running: '运行中', pending: '待执行', completed: '已完成', failed: '失败' }
function statusLabel(status) { return statusLabelMap[status] || status }

function formatDuration(seconds) {
  if (!seconds) return '0s'
  if (seconds >= 3600) return `${Math.floor(seconds/3600)}h ${Math.floor((seconds%3600)/60)}m`
  if (seconds >= 60) return `${Math.floor(seconds/60)}m ${seconds%60}s`
  return `${seconds}s`
}

function minutesToCron(minutes) {
  if (!minutes || minutes < 1) return '*/30 * * * *'
  return `*/${minutes} * * * *`
}

function cronToMinutes(cron) {
  if (!cron) return 30
  const match = cron.match(/^\*\/(\d+)\s+\*\s+\*\s+\*\s+\*$/)
  if (match) return parseInt(match[1]) || 30
  return 30
}

const form = reactive({
  name: '',
  url: '',
  intervalMinutes: 30,
  concurrency: 0,
  interval: 0,
  maxRetries: 0,
  headers: '',
  crawlMode: 'link',
  totalPages: 1
})

const formBackup = ref(null)

function parseTaskConfig(raw) {
  if (!raw) return {}
  if (typeof raw === 'object') return raw
  if (typeof raw === 'string' && raw.trim()) {
    try {
      return JSON.parse(raw)
    } catch (e) {
      return {}
    }
  }
  return {}
}

function loadForm() {
  const t = task.value
  const config = parseTaskConfig(t.config)

  // 任务表字段（优先从任务表读取，其次从 config 读取）
  form.name = t.name || ''
  form.url = t.target_url || config.target_url || ''
  
  // 处理执行周期（cron_expr 在 config 中，格式为 "*/30 * * * *"）
  const cronExpr = config.cron_expr || t.cron_expr || ''
  if (cronExpr) {
    form.intervalMinutes = cronToMinutes(cronExpr)
  } else {
    // 无 cron 时回退：从 interval_seconds 换算为分钟
    const intervalSec = config.interval_seconds || config.interval || t.interval_seconds || 0
    form.intervalMinutes = intervalSec > 0 ? Math.round(intervalSec / 60) : 30
  }
  
  // 处理并发数（config 中是 concurrency）
  form.concurrency = config.concurrency || t.concurrency || 0
  
  // 处理请求间隔（config 中是 interval_seconds）
  form.interval = config.interval_seconds || config.interval || t.interval_seconds || 0
  
  // 处理最大重试次数（config 中是 maxRetries/max_retries，表中是 retry_count）
  form.maxRetries = config.maxRetries ?? config.max_retries ?? t.retry_count ?? 0

  // 处理爬取模式
  form.crawlMode = config.crawl_mode || 'link'

  // 处理爬取页数
  form.totalPages = config.total_pages || 1

  // 处理请求头
  if (typeof config.headers === 'object') {
    form.headers = JSON.stringify(config.headers)
  } else if (typeof config.headers === 'string') {
    form.headers = config.headers
  } else {
    form.headers = ''
  }
  
  formBackup.value = { ...form }
}

function cancelEdit() {
  if (formBackup.value) {
    Object.assign(form, formBackup.value)
  }
  editing.value = false
}

async function saveConfig() {
  try {
    // 解析请求头 JSON 字符串为对象
    let parsedHeaders = form.headers
    if (typeof form.headers === 'string' && form.headers.trim()) {
      try {
        parsedHeaders = JSON.parse(form.headers)
      } catch (e) {
        parsedHeaders = form.headers.trim()
      }
    }

    const config = {
      target_url: form.url,
      total_pages: form.totalPages,
      cron_expr: minutesToCron(form.intervalMinutes),
      interval_seconds: form.interval,
      concurrency: form.concurrency,
      maxRetries: form.maxRetries,
      crawl_mode: form.crawlMode,
      headers: parsedHeaders
    }
    const res = await taskAPI.updateTask(task.value.id, {
      name: form.name,
      config: config
    })
    if (res.data.success) {
      task.value.name = form.name
      task.value.target_url = form.url
      task.value.config = config
      editing.value = false
      ElMessage.success('保存成功')
    } else {
      ElMessage.error(res.data.message || '保存失败')
    }
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const executionRecords = ref([])
const logs = ref([])
const logsLoading = ref(false)
const dataSummary = ref(null)
const dataSummaryLoading = ref(false)

async function fetchTask() {
  const taskId = route.params.id
  if (!taskId || taskId === 'new' || taskId === 'undefined') {
    return
  }
  try {
    const res = await taskAPI.getTask(taskId)
    if (res.data.success) {
      const data = res.data.data
      if (typeof data.config === 'string') {
        data.config = parseTaskConfig(data.config)
      }
      task.value = data
      loadForm()
      if (route.query.edit === '1') {
        editing.value = true
      }
    }
  } catch (e) {
    console.error('获取任务详情失败:', e)
    ElMessage.error('获取任务详情失败')
  }
}

async function fetchVersions() {
  // 跳过无效的 task id
  if (!route.params.id || route.params.id === 'new' || route.params.id === 'undefined') {
    return
  }
  try {
    const res = await taskAPI.getVersions(route.params.id)
    if (res.data.success) {
      const versions = res.data.data || []
      executionRecords.value = versions.map((v, index) => {
        // 从配置中提取执行结果信息
        let status = 'completed'
        let duration = 'N/A'
        let dataCount = 0
        let errorInfo = ''
        
        try {
          const config = typeof v.config === 'string' ? JSON.parse(v.config) : (v.config || {})
          const lastExec = config._last_execution || {}
          if (lastExec.status) {
            status = lastExec.status.toLowerCase() === 'completed' ? 'completed' : 'failed'
          }
          if (lastExec.execution_time) {
            const t = lastExec.execution_time
            if (t >= 3600) {
              duration = `${Math.floor(t/3600)}h ${Math.floor((t%3600)/60)}m`
            } else if (t >= 60) {
              duration = `${Math.floor(t/60)}m ${t%60}s`
            } else {
              duration = `${t}s`
            }
          }
          dataCount = lastExec.data_count || 0
          errorInfo = lastExec.error_message || ''
        } catch (e) {}
        
        return {
          id: v.id,
          version: v.version_index || (versions.length - index),
          status: status,
          duration: duration,
          dataCount: dataCount,
          time: v.created_at || '',
          changeLog: v.change_log || ''
        }
      })
    }
  } catch (e) {
    console.error('获取版本列表失败:', e)
  }
}

async function refreshLogs() {
  logsLoading.value = true
  try {
    // 传递 task_id 参数过滤任务相关日志
    const res = await systemAPI.getLogs({ task_id: route.params.id, limit: 200, page_size: 200 })
    if (res.data.success) {
      const logList = res.data.data?.list || []
      logs.value = logList.map(item => ({
        time: item.created_at ? item.created_at.split(' ')[1] || item.created_at : '',
        type: item.level ? item.level.toLowerCase() : 'info',
        level: item.level || 'INFO',
        message: item.message || ''
      }))
    }
  } catch (e) {
    console.error('获取日志失败:', e)
  } finally {
    logsLoading.value = false
  }
}

async function fetchDataSummary() {
  if (!route.params.id || route.params.id === 'new' || route.params.id === 'undefined') {
    return
  }
  dataSummaryLoading.value = true
  try {
    const res = await taskAPI.getDataSummary(route.params.id)
    if (res.data.success) {
      dataSummary.value = res.data.data
    }
  } catch (e) {
    console.error('获取数据概览失败:', e)
  } finally {
    dataSummaryLoading.value = false
  }
}

onMounted(() => {
  fetchTask()
})

watch(() => route.params.id, (id, prevId) => {
  if (id && id !== prevId && id !== 'new' && id !== 'undefined') {
    editing.value = route.query.edit === '1'
    fetchTask()
    if (activeTab.value === 'logs') {
      refreshLogs()
    }
  }
})

watch(activeTab, (val) => {
  if (val === 'records') {
    fetchVersions()
  }
  if (val === 'logs') {
    refreshLogs()
    if (autoScroll.value) {
      nextTick(() => {
        if (logViewerRef.value) {
          logViewerRef.value.scrollTop = logViewerRef.value.scrollHeight
        }
      })
    }
  }
  if (val === 'preview') {
    fetchDataSummary()
  }
})
</script>

<style scoped>
.task-detail-page {
  min-height: 100vh;
  background-color: var(--bg-primary);
  background-image:
    linear-gradient(var(--border-color) 1px, transparent 1px),
    linear-gradient(90deg, var(--border-color) 1px, transparent 1px);
  background-size: 40px 40px;
}

.task-detail-page::before {
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

.detail-content {
  max-width: 960px;
  margin: 0 auto;
  padding: 40px 24px 80px;
  position: relative;
  z-index: 1;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;
}

.btn-back {
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.25s ease;
  flex-shrink: 0;
}

.btn-back:hover {
  color: var(--text-primary);
  border-color: rgba(255, 255, 255, 0.15);
}

.btn-back svg {
  width: 20px;
  height: 20px;
}

.header-info {
  flex: 1;
  min-width: 0;
}

.detail-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  letter-spacing: -0.4px;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-status-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-running {
  background: rgba(16, 185, 129, 0.12);
  color: #34d399;
}
.status-running .status-dot {
  background: #34d399;
  box-shadow: 0 0 6px rgba(52, 211, 153, 0.5);
  animation: pulse 1.5s ease-in-out infinite;
}

.status-pending { background: var(--active-bg); color: var(--active-color); }
.status-pending .status-dot { background: var(--active-color); }
.status-completed { background: rgba(255, 255, 255, 0.05); color: var(--text-muted); }
.status-completed .status-dot { background: var(--text-muted); }
.status-failed { background: rgba(239, 68, 68, 0.12); color: #f87171; }
.status-failed .status-dot { background: #f87171; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.btn-version {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 500;
  background: var(--border-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-version:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.15);
}

.btn-version svg {
  width: 14px;
  height: 14px;
}

.tab-nav {
  display: flex;
  gap: 4px;
  background: var(--bg-card);
  border-radius: 12px;
  padding: 5px;
  margin-bottom: 24px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.tab-btn {
  flex: 1;
  padding: 11px 20px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
  background: transparent;
  border: none;
  border-radius: 9px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.tab-btn:hover {
  color: rgba(255, 255, 255, 0.7);
}

.tab-btn.active {
  background: rgba(var(--accent-rgb), 0.15);
  color: var(--active-color);
  font-weight: 600;
}

.tab-panel {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 28px;
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group.full {
  grid-column: 1 / -1;
}

.form-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-input {
  width: 100%;
  padding: 11px 16px;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  outline: none;
  transition: all 0.25s ease;
}

.form-input:focus {
  border-color: rgba(var(--accent-rgb), 0.4);
  box-shadow: 0 0 0 3px var(--glow-color);
}

.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-textarea {
  width: 100%;
  padding: 11px 16px;
  font-size: 13px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  outline: none;
  resize: vertical;
  transition: all 0.25s ease;
}

.form-textarea:focus {
  border-color: rgba(var(--accent-rgb), 0.4);
}

.form-textarea:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 11px 22px;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.25s ease;
  background: var(--border-color);
  color: var(--text-secondary);
}

.action-btn svg { width: 16px; height: 16px; }

.action-btn.primary {
  background: var(--gradient-primary);
  color: #fff;
  border: none;
  box-shadow: 0 4px 14px rgba(var(--accent-rgb), 0.3);
}

.action-btn.primary:hover { box-shadow: 0 6px 20px rgba(var(--accent-rgb), 0.45); transform: translateY(-1px); }

.action-btn.success {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border-color: rgba(16, 185, 129, 0.2);
}

.action-btn.success:hover { background: rgba(16, 185, 129, 0.22); }

.action-btn.cancel {
  background: var(--border-color);
  color: var(--text-secondary);
}

.action-btn.cancel:hover { background: rgba(255, 255, 255, 0.08); color: var(--text-primary); }

.log-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 14px;
  margin-bottom: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.auto-scroll-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
}

.auto-scroll-label input {
  accent-color: var(--accent-primary);
}

.btn-clear-log {
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 500;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.15);
  border-radius: 8px;
  color: #f87171;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-clear-log:hover {
  background: rgba(239, 68, 68, 0.15);
}

.log-viewer {
  height: 480px;
  overflow-y: auto;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 12px;
  line-height: 1.8;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  padding: 16px;
}

.log-viewer::-webkit-scrollbar { width: 6px; }
.log-viewer::-webkit-scrollbar-track { background: transparent; }
.log-viewer::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.08); border-radius: 3px; }

.log-line {
  display: flex;
  gap: 10px;
}

.log-time {
  color: var(--text-muted);
  flex-shrink: 0;
}

.log-level {
  width: 50px;
  flex-shrink: 0;
  font-weight: 600;
}

.log-level.info { color: var(--active-color); }
.log-level.warn { color: #fbbf24; }
.log-level.error { color: #f87171; }

.log-msg { color: var(--text-secondary); }

.log-msg :deep(.kw) { color: var(--active-color); }
.log-msg :deep(.err) { color: #f87171; }

.log-line.error .log-msg { color: #f87171; }
.log-line.warn .log-msg { color: #fbbf24; }

.log-empty {
  text-align: center;
  color: rgba(255, 255, 255, 0.15);
  padding: 60px 0;
  font-size: 13px;
}

.timeline {
  position: relative;
  padding-left: 32px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 11px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: rgba(255, 255, 255, 0.06);
}

.timeline-item {
  position: relative;
  margin-bottom: 24px;
}

.timeline-item:last-child { margin-bottom: 0; }

.timeline-dot {
  position: absolute;
  left: -26px;
  top: 16px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.1);
  background: #0d1117;
}

.timeline-dot.dot-completed {
  border-color: #34d399;
  background: #34d399;
  box-shadow: 0 0 8px rgba(52, 211, 153, 0.4);
}

.timeline-dot.dot-failed {
  border-color: #f87171;
  background: #f87171;
  box-shadow: 0 0 8px rgba(248, 113, 113, 0.4);
}

.timeline-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px 20px;
}

.timeline-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.record-version {
  font-size: 13px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.7);
}

.record-status {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 10px;
}

.record-status.status-completed { background: rgba(16, 185, 129, 0.12); color: #34d399; }
.record-status.status-failed { background: rgba(239, 68, 68, 0.12); color: #f87171; }

.timeline-card-meta {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 6px;
}

.timeline-card-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.2);
}

.preview-panel {
  padding: 24px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 60px;
  color: rgba(255, 255, 255, 0.4);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #4c6ef5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 80px 20px;
}

.empty-icon {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.03);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.15);
}

.empty-icon svg { width: 32px; height: 32px; }

.empty-text {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.35);
}

.empty-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.2);
}

.data-overview {
  max-width: 800px;
  margin: 0 auto;
}

.overview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.overview-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.overview-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.overview-badge.running { background: rgba(16, 185, 129, 0.12); color: #34d399; }
.overview-badge.pending { background: rgba(76, 110, 245, 0.12); color: #7c8aff; }
.overview-badge.completed { background: rgba(255, 255, 255, 0.05); color: rgba(255, 255, 255, 0.4); }
.overview-badge.failed, .overview-badge.error { background: rgba(239, 68, 68, 0.12); color: #f87171; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.blue { background: rgba(76, 110, 245, 0.15); color: #7c8aff; }
.stat-icon.green { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.stat-icon.yellow { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }
.stat-icon.purple { background: rgba(124, 58, 237, 0.15); color: #a78bfa; }

.stat-icon svg { width: 24px; height: 24px; }

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 12px;
  color: var(--text-muted);
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.type-section, .time-section {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
}

.type-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.type-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 8px;
}

.type-name {
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
}

.type-count {
  font-size: 13px;
  color: var(--text-muted);
}

.last-time {
  font-size: 14px;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .detail-content { padding: 24px 16px 64px; }
  .detail-title { font-size: 20px; }
  .form-row { grid-template-columns: 1fr; }
  .tab-nav { overflow-x: auto; }
  .preview-panel { padding: 16px; }
}
</style>